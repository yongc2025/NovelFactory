"""异步任务注册表 — 幂等、互斥、状态机

所有流水线任务通过 TaskRegistry 统一管理：
- 幂等：同 project+stage 重复提交返回同一 task_id
- 互斥：同 project 同时只能有一个 running 任务
- 状态机：pending → running → success / failed / cancelled
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from novel_factory.db.connection import get_connection

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
    """任务注册表 — SQLite 持久化实现"""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    def _row_to_task(self, row: Any) -> PipelineTask:
        """将 SQLite Row 转为 PipelineTask 对象"""
        return PipelineTask(
            id=row["id"],
            project_id=row["project_id"],
            stage=row["stage"],
            status=row["status"],
            cancel_requested=bool(row["cancel_requested"]),
            progress_current=row["progress_current"] or 0,
            progress_total=row["progress_total"] or 0,
            progress_label=row["progress_label"] or "",
            started_at=row["started_at"] or 0.0,
            finished_at=row["finished_at"] or 0.0,
            result=json.loads(row["result"]) if row["result"] else None,
            error=row["error"],
            params=json.loads(row["params"]) if row["params"] else {},
        )

    async def submit(
        self,
        project_id: str,
        stage: str,
        params: dict | None = None,
    ) -> tuple[PipelineTask, bool]:
        """提交任务。返回 (task, is_new)。"""
        async with self._lock:
            with get_connection() as conn:
                # 检查同 project 是否有活跃任务
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE project_id = ? AND status IN ('pending', 'running')",
                    (project_id,)
                )
                existing_row = cursor.fetchone()
                
                if existing_row:
                    existing = self._row_to_task(existing_row)
                    if existing.stage == stage:
                        logger.info("幂等命中: project=%s stage=%s task=%s", project_id, stage, existing.id)
                        return existing, False
                    else:
                        raise RuntimeError(
                            f"项目 {project_id} 的 {existing.stage} 阶段正在执行中，"
                            f"请等待完成后再启动 {stage}"
                        )

                # 创建新任务
                task_id = str(uuid.uuid4())
                now = time.time()
                params_json = json.dumps(params or {}, ensure_ascii=False)
                
                conn.execute(
                    "INSERT INTO tasks (id, project_id, stage, status, started_at, params) VALUES (?, ?, ?, ?, ?, ?)",
                    (task_id, project_id, stage, "pending", now, params_json)
                )
                
                new_task = PipelineTask(
                    id=task_id,
                    project_id=project_id,
                    stage=stage,
                    status="pending",
                    started_at=now,
                    params=params or {},
                )
                logger.info("任务创建(DB): task=%s project=%s stage=%s", task_id, project_id, stage)
                return new_task, True

    async def transition(
        self,
        task_id: str,
        new_status: str,
        **kwargs: Any,
    ) -> None:
        """状态转换 — 持久化到 DB"""
        async with self._lock:
            with get_connection() as conn:
                cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if not row:
                    raise KeyError(f"任务不存在: {task_id}")
                
                old_status = row["status"]
                valid = _VALID_TRANSITIONS.get(old_status, set())
                if new_status not in valid:
                    raise ValueError(f"非法转换: {old_status} → {new_status} (task={task_id})")

                update_fields = ["status = ?", "finished_at = ?"]
                params = [new_status, None]
                
                if new_status in ("success", "failed", "cancelled"):
                    params[1] = time.time()
                
                if "result" in kwargs:
                    update_fields.append("result = ?")
                    params.append(json.dumps(kwargs["result"], ensure_ascii=False))
                if "error" in kwargs:
                    update_fields.append("error = ?")
                    params.append(kwargs["error"])

                query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
                params.append(task_id)
                conn.execute(query, tuple(params))
                logger.info("状态转换(DB): task=%s %s → %s", task_id, old_status, new_status)

    async def update_progress(
        self,
        task_id: str,
        current: int,
        total: int,
        label: str = "",
    ) -> None:
        """更新批量任务进度。"""
        async with self._lock:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET progress_current = ?, progress_total = ?, progress_label = ? WHERE id = ?",
                    (current, total, label, task_id)
                )

    async def cancel(self, task_id: str) -> bool:
        """标记取消意图。"""
        async with self._lock:
            with get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE tasks SET cancel_requested = 1 WHERE id = ? AND status IN ('pending', 'running')",
                    (task_id,)
                )
                success = cursor.rowcount > 0
                if success:
                    logger.info("取消标记(DB): task=%s", task_id)
                return success

    def get(self, task_id: str) -> PipelineTask | None:
        """获取任务。"""
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None

    def get_active(self, project_id: str) -> PipelineTask | None:
        """获取项目的当前活跃任务。"""
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ? AND status IN ('pending', 'running')",
                (project_id,)
            )
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None

    def is_running(self, project_id: str) -> bool:
        """检查项目是否有任务在跑。"""
        return self.get_active(project_id) is not None


# 全局单例
registry = TaskRegistry()
