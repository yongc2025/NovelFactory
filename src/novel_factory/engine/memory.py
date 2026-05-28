"""
记忆系统 — 管理小说创作过程中的上下文和记忆

职责：
1. 生成场景摘要和章节摘要（层次化压缩）
2. 构建上下文窗口（全局记忆 + 前文摘要 + 滑动窗口 + 当前任务）
3. 更新角色状态（跟踪角色在故事中的变化）

记忆架构：
- 全局记忆（角色卡+世界观）：~1000 tokens
- 前文摘要（层次化压缩）：~500 tokens
- 滑动窗口（最近2-3场景原文）：~2000 tokens
- 当前任务指令：~300 tokens
- 总计 ≈ 7600 tokens/调用，留足余量
"""

from __future__ import annotations

import json
import logging

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import render_prompt

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    记忆管理器

    负责维护创作过程中的上下文信息，确保长文本创作的一致性。
    采用分层摘要策略：场景级 → 章节级 → 项目级
    """

    async def generate_scene_summary(self, scene_text: str) -> str:
        """
        生成场景摘要（~100字）

        将场景正文压缩为简短摘要，保留关键信息：
        - 发生了什么（事件）
        - 谁参与了（角色）
        - 情绪变化（从X到Y）
        - 重要对话/决定

        Args:
            scene_text: 场景正文文本

        Returns:
            约100字的场景摘要
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一位文本摘要专家。请将以下场景正文压缩为约100字的摘要。\n"
                    "保留：关键事件、参与角色、情绪变化、重要对话/决定。\n"
                    "去掉：细节描写、环境描写、过渡性文字。\n"
                    "输出纯文本，不要标题或格式。"
                ),
            },
            {
                "role": "user",
                "content": f"请生成摘要：\n\n{scene_text}",
            },
        ]

        summary = await complete(messages=messages, role="summary", temperature=0.2, max_tokens=200)
        logger.debug("场景摘要生成完成: %d 字", len(summary))
        return summary.strip()

    async def generate_chapter_summary(self, scenes: list[dict]) -> str:
        """
        生成章节摘要（~200字）

        将多个场景摘要合并为章节级摘要，保留章节的核心叙事线。

        Args:
            scenes: 场景列表，每个包含 number, summary 等字段

        Returns:
            约200字的章节摘要
        """
        scene_texts = []
        for s in scenes:
            num = s.get("scene_num") or s.get("number", "?")
            summary = s.get("summary", "无摘要")
            scene_texts.append(f"场景{num}: {summary}")

        combined = "\n".join(scene_texts)

        messages = [
            {
                "role": "system",
                "content": (
                    "你是一位文本摘要专家。请将以下多个场景摘要合并为约200字的章节摘要。\n"
                    "保留：章节核心事件线、角色发展、情绪走向、关键转折。\n"
                    "输出纯文本，不要标题或格式。"
                ),
            },
            {
                "role": "user",
                "content": f"请生成章节摘要：\n\n{combined}",
            },
        ]

        summary = await complete(messages=messages, role="summary", temperature=0.2, max_tokens=400)
        logger.debug("章节摘要生成完成: %d 字", len(summary))
        return summary.strip()

    async def build_context_window(
        self,
        project_id: str,
        current_chapter: int,
        current_scene: int,
    ) -> dict:
        """
        构建上下文窗口

        为正文生成构建完整的上下文信息，采用分层策略：
        - system: 系统指令（写作风格、红线等）
        - global_memory: 全局记忆（角色卡+世界观，~1000 tokens）
        - recent_summary: 前文摘要（~500 tokens）
        - sliding_window: 滑动窗口（最近2-3场景原文，~2000 tokens）
        - current_task: 当前任务指令（~300 tokens）

        Args:
            project_id: 项目 ID
            current_chapter: 当前章节号
            current_scene: 当前场景号

        Returns:
            包含 5 个层级的上下文字典
        """
        with get_connection() as conn:
            # 1. 获取项目信息
            project = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not project:
                raise ValueError(f"项目不存在: {project_id}")

            # 2. 构建全局记忆（角色卡 + 世界观）
            global_memory = self._build_global_memory(conn, project_id)

            # 3. 构建前文摘要
            recent_summary = self._build_recent_summary(conn, project_id, current_chapter)

            # 4. 构建滑动窗口
            sliding_window = self._build_sliding_window(conn, project_id, current_chapter, current_scene)

            # 5. 构建当前任务
            current_task = self._build_current_task(conn, project_id, current_chapter, current_scene)

        return {
            "system": "",  # 由调用方填充 STYLE_INSTRUCTION
            "global_memory": global_memory,
            "recent_summary": recent_summary,
            "sliding_window": sliding_window,
            "current_task": current_task,
        }

    def _build_global_memory(self, conn, project_id: str) -> str:
        """构建全局记忆 — 角色卡 + 世界观"""
        characters = conn.execute(
            "SELECT name, role, personality_surface, personality_deep, "
            "core_desire, core_fear, voice_style, current_state "
            "FROM characters WHERE project_id = ?",
            (project_id,),
        ).fetchall()

        char_texts = []
        for c in characters:
            char_texts.append(
                f"- {c['name']}（{c['role'] or '未设定'}）: "
                f"{c['personality_surface'] or '未设定'}\n"
                f"  核心欲望: {c['core_desire'] or '未设定'}\n"
                f"  核心恐惧: {c['core_fear'] or '未设定'}\n"
                f"  说话风格: {c['voice_style'] or '未设定'}\n"
                f"  当前状态: {c['current_state'] or '未设定'}"
            )
        characters_text = "\n".join(char_texts) if char_texts else "暂无角色信息"

        world_settings = conn.execute(
            "SELECT category, content FROM world_settings WHERE project_id = ?",
            (project_id,),
        ).fetchall()

        world_texts = []
        for w in world_settings:
            world_texts.append(f"【{w['category']}】\n{w['content']}")
        world_text = "\n\n".join(world_texts) if world_texts else "暂无世界观设定"

        return f"## 角色信息\n{characters_text}\n\n## 世界观设定\n{world_text}"

    def _build_recent_summary(self, conn, project_id: str, current_chapter: int) -> str:
        """构建前文摘要 — 已完成章节的摘要"""
        chapters = conn.execute(
            "SELECT chapter_num, title, outline FROM chapters "
            "WHERE project_id = ? AND chapter_num < ? "
            "ORDER BY chapter_num DESC LIMIT 5",
            (project_id, current_chapter),
        ).fetchall()

        if not chapters:
            return "这是故事的开始，暂无前文。"

        summaries = []
        for ch in reversed(chapters):
            summaries.append(
                f"第{ch['chapter_num']}章《{ch['title'] or '未命名'}》: "
                f"{ch['outline'] or '暂无摘要'}"
            )
        return "\n".join(summaries)

    def _build_sliding_window(
        self, conn, project_id: str, current_chapter: int, current_scene: int
    ) -> str:
        """构建滑动窗口 — 最近2-3个已写完的场景原文"""
        scenes = conn.execute(
            "SELECT s.scene_num, s.final_text, s.location, "
            "c.chapter_num, c.title as chapter_title "
            "FROM scenes s "
            "JOIN chapters c ON s.chapter_id = c.id "
            "WHERE s.project_id = ? AND s.final_text IS NOT NULL "
            "ORDER BY c.chapter_num DESC, s.scene_num DESC LIMIT 3",
            (project_id,),
        ).fetchall()

        if not scenes:
            return "暂无已写完的场景。"

        window_texts = []
        for s in reversed(scenes):
            text = s["final_text"] or ""
            if len(text) > 500:
                text = "..." + text[-500:]
            window_texts.append(
                f"--- 第{s['chapter_num']}章 场景{s['scene_num']} "
                f"（{s['location'] or '未知地点'}）---\n{text}"
            )
        return "\n\n".join(window_texts)

    def _build_current_task(
        self, conn, project_id: str, current_chapter: int, current_scene: int
    ) -> str:
        """构建当前任务描述"""
        chapter = conn.execute(
            "SELECT * FROM chapters WHERE project_id = ? AND chapter_num = ?",
            (project_id, current_chapter),
        ).fetchone()

        if not chapter:
            return f"请撰写第{current_chapter}章第{current_scene}个场景的正文。"

        scene = conn.execute(
            "SELECT * FROM scenes WHERE chapter_id = ? AND scene_num = ?",
            (chapter["id"], current_scene),
        ).fetchone()

        task_parts = [
            f"当前任务：撰写第{current_chapter}章《{chapter['title'] or '未命名'}》",
            f"第{current_scene}个场景的正文。",
            f"\n章节核心事件：{chapter['core_event'] or '未设定'}",
            f"情绪定位：{chapter['emotion_position'] or '未设定'}",
        ]

        if scene:
            task_parts.extend([
                f"\n场景地点：{scene['location'] or '未设定'}",
                f"场景氛围：{scene['atmosphere'] or '未设定'}",
                f"出场角色：{scene['characters_present'] or '未设定'}",
                f"核心冲突：{scene['conflict'] or '未设定'}",
                f"转折点：{scene['turning_point'] or '未设定'}",
                f"情绪变化：{scene['emotion_start'] or '?'} → {scene['emotion_end'] or '?'}",
                f"对话方向：{scene['dialogue_direction'] or '未设定'}",
                f"感官细节：{scene['sensory_details'] or '未设定'}",
            ])

        return "\n".join(task_parts)

    async def update_character_state(self, character_id: str, scene_summary: str) -> None:
        """
        更新角色状态

        根据场景摘要更新角色的当前状态，跟踪角色在故事中的发展。

        Args:
            character_id: 角色 ID
            scene_summary: 场景摘要
        """
        with get_connection() as conn:
            character = conn.execute(
                "SELECT name, current_state FROM characters WHERE id = ?",
                (character_id,),
            ).fetchone()

            if not character:
                logger.warning("角色不存在: %s", character_id)
                return

            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一位小说编辑。根据场景摘要，更新角色的当前状态。\n"
                        "输出格式：只输出更新后的角色状态描述（50字内），不要其他内容。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"角色：{character['name']}\n"
                        f"当前状态：{character['current_state'] or '故事开始'}\n\n"
                        f"最新场景摘要：{scene_summary}\n\n"
                        f"请更新角色状态："
                    ),
                },
            ]

            new_state = await complete(messages=messages, role="summary", temperature=0.3, max_tokens=100)
            conn.execute(
                "UPDATE characters SET current_state = ? WHERE id = ?",
                (new_state.strip(), character_id),
            )
            logger.info("角色状态已更新: %s", character["name"])
