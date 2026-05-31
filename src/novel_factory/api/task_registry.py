"""异步任务注册表 — 幂等、互斥、状态机

所有流水线任务通过 TaskRegistry 统一管理：
- 幂等：同 project+stage 重复提交返回同一 task_id
- 互斥：同 project 同时只能有一个 running 任务
- 状态机：pending → running → success / failed / cancelled
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# 合法状态转换表
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"running", "cancelled"},
    "running": {"success", "failed", "cancelled"},
    "success": set(),
    "failed": set(),
    "cancelled": set(),
}


@dataclass
class PipelineTask:
    """流水线任务"""

    id: str
    project_id: str
    stage: str
    status: str = "pending"
    cancel_requested: bool = False
    progress_current: int = 0
    progress_total: int = 0
    progress_label: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0
    result: Any = None
    error: str | None = None
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """序列化为 API 响应"""
        return {
            "task_id": self.id,
            "project_id": self.project_id,
            "stage": self.stage,
            "status": self.status,
            "cancel_requested": self.cancel_requested,
            "progress": {
                "current": self.progress_current,
                "total": self.progress_total,
                "label": self.progress_label,
                "percent": round(self.progress_current / self.progress_total * 100)
                if self.progress_total > 0
                else 0,
            },
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


class TaskRegistry:
    """任务注册表 — 单例使用"""

    def __init__(self) -> None:
        self._tasks: dict[str, PipelineTask] = {}
        self._running: dict[str, str] = {}  # project_id → task_id
        self._lock = asyncio.Lock()

    async def submit(
        self,
        project_id: str,
        stage: str,
        params: dict | None = None,
    ) -> tuple[PipelineTask, bool]:
        """提交任务。返回 (task, is_new)。

        幂等：同 project+stage 在跑时返回已有任务 (is_new=False)。
        互斥：同 project 只能有一个 running 任务。
        """
        async with self._lock:
            # 检查同 project 是否有任务在跑
            existing_id = self._running.get(project_id)
            if existing_id:
                existing = self._tasks.get(existing_id)
                if existing and existing.status in ("pending", "running"):
                    if existing.stage == stage:
                        # 幂等命中：同 stage 在跑
                        logger.info(
                            "幂等命中: project=%s stage=%s task=%s",
                            project_id, stage, existing.id,
                        )
                        return existing, False
                    else:
                        # 不同 stage 在跑，不能覆盖
                        raise RuntimeError(
                            f"项目 {project_id} 的 {existing.stage} 阶段正在执行中，"
                            f"请等待完成后再启动 {stage}"
                        )
                # 旧任务已结束，清理
                del self._running[project_id]

            # 创建新任务
            task = PipelineTask(
                id=str(uuid.uuid4()),
                project_id=project_id,
                stage=stage,
                status="pending",
                started_at=time.time(),
                params=params or {},
            )
            self._tasks[task.id] = task
            self._running[project_id] = task.id
            logger.info("任务创建: task=%s project=%s stage=%s", task.id, project_id, stage)
            return task, True

    async def transition(
        self,
        task_id: str,
        new_status: str,
        **kwargs: Any,
    ) -> None:
        """状态转换 — 单点写入，原子性。"""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"任务不存在: {task_id}")

            valid = _VALID_TRANSITIONS.get(task.status, set())
            if new_status not in valid:
                raise ValueError(
                    f"非法转换: {task.status} → {new_status} (task={task_id})"
                )

            task.status = new_status
            if "result" in kwargs:
                task.result = kwargs["result"]
            if "error" in kwargs:
                task.error = kwargs["error"]

            if new_status in ("success", "failed", "cancelled"):
                task.finished_at = time.time()
                # 释放互斥锁
                if self._running.get(task.project_id) == task_id:
                    del self._running[task.project_id]

            logger.info(
                "状态转换: task=%s %s → %s", task_id, task.status, new_status,
            )

    async def update_progress(
        self,
        task_id: str,
        current: int,
        total: int,
        label: str = "",
    ) -> None:
        """更新批量任务进度。"""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task.progress_current = current
            task.progress_total = total
            task.progress_label = label

    async def cancel(self, task_id: str) -> bool:
        """标记取消意图。返回是否成功标记。"""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            if task.status not in ("pending", "running"):
                return False
            task.cancel_requested = True
            logger.info("取消标记: task=%s", task_id)
            return True

    def get(self, task_id: str) -> PipelineTask | None:
        """获取任务。"""
        return self._tasks.get(task_id)

    def get_active(self, project_id: str) -> PipelineTask | None:
        """获取项目的当前活跃任务。"""
        task_id = self._running.get(project_id)
        if not task_id:
            return None
        task = self._tasks.get(task_id)
        if task and task.status in ("pending", "running"):
            return task
        return None

    def is_running(self, project_id: str) -> bool:
        """检查项目是否有任务在跑。"""
        return self.get_active(project_id) is not None


# 全局单例
registry = TaskRegistry()
