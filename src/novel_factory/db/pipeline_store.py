"""
流水线状态存储 — SQLite 实现
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from novel_factory.db.connection import get_connection

logger = logging.getLogger(__name__)

class PipelineStore:
    """流水线状态存储管理器"""

    def get_stage_states(self, project_id: str) -> dict[str, dict[str, Any]]:
        """获取项目的所有阶段状态"""
        stages = ["topic", "world", "character", "outline", "metadata", "scene", "draft", "review"]
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT stage, status, updated_at FROM stage_states WHERE project_id = ?",
                (project_id,)
            )
            rows = cursor.fetchall()
            
            # 转换为字典，不存在的阶段默认为 pending
            results = {stage: {"status": "pending", "updated_at": None} for stage in stages}
            for row in rows:
                if row["stage"] in results:
                    results[row["stage"]] = {
                        "status": row["status"],
                        "updated_at": row["updated_at"]
                    }
            return results

    def update_stage_state(self, project_id: str, stage: str, status: str) -> None:
        """更新某个阶段的状态"""
        now = datetime.now().isoformat()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO stage_states (project_id, stage, status, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id, stage) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (project_id, stage, status, now)
            )

    def get_pipeline_state(self, project_id: str) -> dict[str, Any] | None:
        """获取流水线全局状态"""
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM pipeline_states WHERE project_id = ?",
                (project_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
                
            return {
                "project_id": row["project_id"],
                "current_stage": row["current_stage"],
                "current_stage_label": row["current_stage_label"],
                "progress_percent": row["progress_percent"],
                "total_stages": row["total_stages"],
                "completed_stages": row["completed_stages"],
                "needs_confirmation": bool(row["needs_confirmation"]),
                "status": row["status"],
                "error": row["error"],
                "updated_at": row["updated_at"],
            }

    def update_pipeline_state(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        """更新流水线状态"""
        now = datetime.now().isoformat()
        
        # 1. 获取当前状态（或初始化）
        current = self.get_pipeline_state(project_id)
        if not current:
            current = {
                "project_id": project_id,
                "current_stage": None,
                "current_stage_label": None,
                "progress_percent": 0.0,
                "total_stages": 8, # STAGES 长度
                "completed_stages": 0,
                "needs_confirmation": False,
                "status": "idle",
                "error": None,
                "updated_at": now,
            }
        
        # 2. 合并更新
        current.update(kwargs)
        current["updated_at"] = now
        
        # 3. 计算进度
        if current["total_stages"] > 0:
            current["progress_percent"] = round(
                current["completed_stages"] / current["total_stages"] * 100, 1
            )
            
        # 4. 持久化
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO pipeline_states (
                    project_id, current_stage, current_stage_label, progress_percent,
                    total_stages, completed_stages, needs_confirmation, status, error, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    current_stage = excluded.current_stage,
                    current_stage_label = excluded.current_stage_label,
                    progress_percent = excluded.progress_percent,
                    total_stages = excluded.total_stages,
                    completed_stages = excluded.completed_stages,
                    needs_confirmation = excluded.needs_confirmation,
                    status = excluded.status,
                    error = excluded.error,
                    updated_at = excluded.updated_at
                """,
                (
                    current["project_id"], current["current_stage"], current["current_stage_label"],
                    current["progress_percent"], current["total_stages"], current["completed_stages"],
                    int(current["needs_confirmation"]), current["status"], current["error"], current["updated_at"]
                )
            )
        
        return current

pipeline_store = PipelineStore()
