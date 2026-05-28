"""编排器 -- NovelPipeline

协调叙事引擎的各个阶段：选题 -> 世界观 -> 角色 -> 大纲 -> 场景 -> 正文 -> 审校

每个阶段调用对应的 engine 模块，阶段之间打印中间结果供用户确认。
使用 Rich 美化输出（进度条、面板、表格）。
"""

from __future__ import annotations

import asyncio
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from novel_factory.db.project_store import ProjectStore

console = Console()

# ── 阶段名称 ────────────────────────────────────────────────

STAGES = [
    ("topic", "选题评估"),
    ("world", "世界观搭建"),
    ("character", "角色设计"),
    ("outline", "大纲编剧"),
    ("scene", "场景细纲"),
    ("draft", "正文生成"),
    ("review", "编辑审校"),
]


class NovelPipeline:
    """小说生成流水线编排器

    用法:
        pipeline = NovelPipeline()
        project_id = await pipeline.run_full_pipeline("重生复仇打脸")
        project_id = await pipeline.plan_only("重生复仇打脸", target_chapters=10)
        await pipeline.write_from_outline(project_id)
    """

    def __init__(self):
        self.store = ProjectStore()

    # ── 完整流程 ──────────────────────────────────────────────

    async def run_full_pipeline(
        self,
        inspiration: str,
        genre_hint: str | None = None,
        target_words: int = 8000,
    ) -> str:
        """完整流程：选题 -> 世界观 -> 角色 -> 大纲 -> 场景 -> 正文 -> 审校

        Args:
            inspiration: 灵感描述
            genre_hint: 题材提示（如"重生"、"穿越"）
            target_words: 目标字数

        Returns:
            project_id: 项目 ID
        """
        console.print()
        console.print(
            Panel(
                f"[bold cyan]灵感:[/bold cyan] {inspiration}\n"
                f"[bold cyan]题材:[/bold cyan] {genre_hint or '待定'}\n"
                f"[bold cyan]目标字数:[/bold cyan] {target_words}",
                title="[启动] 完整流水线",
                border_style="cyan",
            )
        )

        # 创建项目
        title = inspiration[:30] + ("..." if len(inspiration) > 30 else "")
        project_id = self.store.create_project(
            title=title,
            inspiration=inspiration,
            genre=genre_hint,
            target_words=target_words,
        )
        console.print(f"\n[dim]项目 ID: {project_id}[/dim]\n")

        # 使用简单进度显示，避免 Rich Spinner 的 braille 字符在 Windows GBK 下报错
        total_steps = len(STAGES)
        for i, (stage_key, stage_name) in enumerate(STAGES, 1):
            console.print(f"\n[bold cyan][{i}/{total_steps}][/bold cyan] {stage_name}...")

            if stage_key == "topic":
                topic = await self._step_topic(project_id, inspiration, genre_hint)
                self._print_stage_result("选题评估", topic)
            elif stage_key == "world":
                world = await self._step_world(project_id, topic)
                self._print_stage_result("世界观设定", world)
            elif stage_key == "character":
                characters = await self._step_character(project_id, topic, world)
                self._print_stage_result("角色设计", characters)
            elif stage_key == "outline":
                target_chapters = max(3, target_words // 800)
                outline = await self._step_outline(project_id, topic, world, characters, target_chapters)
                self._print_stage_result("章节大纲", outline)
                chapters = outline.get("chapters", [])
            elif stage_key == "scene":
                for ch in chapters:
                    ch_num = ch.get("chapter_num", 0)
                    ch_title = ch.get("title", f"第{ch_num}章")
                    console.print(f"  场景细纲: {ch_title}")
                    scenes = await self._step_scene(project_id, ch, characters)
                    self.store.save_scene(project_id, ch_num, scenes)
            elif stage_key == "draft":
                for ch in chapters:
                    ch_num = ch.get("chapter_num", 0)
                    ch_title = ch.get("title", f"第{ch_num}章")
                    console.print(f"  正文生成: {ch_title}")
                    ch_scenes = self.store.get_scene(project_id, ch_num) or []
                    chapter_draft = ""
                    scene_list = ch_scenes if isinstance(ch_scenes, list) else [ch_scenes]
                    for single_scene in scene_list:
                        draft = await self._step_draft(project_id, ch, single_scene, characters)
                        chapter_draft += draft + "\n\n"
                    self.store.save_draft(project_id, ch_num, chapter_draft.strip())
            elif stage_key == "review":
                review = await self._step_review(project_id)
                self._print_stage_result("审校报告", review)

        self.store.update_project_status(project_id, "complete")

        console.print()
        console.print(
            Panel(
                f"[bold green]完整流水线执行完毕[/bold green]\n\n"
                f"项目 ID: [cyan]{project_id}[/cyan]\n"
                f"总章数: {len(chapters)}\n"
                f"目标字数: {target_words}\n\n"
                f"使用 [bold]novel-factory write {project_id}[/bold] 重新生成正文\n"
                f"使用 [bold]novel-factory review {project_id}[/bold] 重新审校\n"
                f"输出目录: [dim]output/{project_id}/[/dim]",
                title="[完成]",
                border_style="green",
            )
        )

        return project_id

    # ── 只做到大纲 ────────────────────────────────────────────

    async def plan_only(
        self,
        inspiration: str,
        genre_hint: str | None = None,
        target_chapters: int = 10,
    ) -> str:
        """只做到大纲阶段：选题 -> 世界观 -> 角色 -> 大纲

        Args:
            inspiration: 灵感描述
            genre_hint: 题材提示
            target_chapters: 目标章节数

        Returns:
            project_id: 项目 ID
        """
        console.print()
        console.print(
            Panel(
                f"[bold cyan]灵感:[/bold cyan] {inspiration}\n"
                f"[bold cyan]题材:[/bold cyan] {genre_hint or '待定'}\n"
                f"[bold cyan]目标章节:[/bold cyan] {target_chapters}",
                title="[规划] 只生成大纲",
                border_style="cyan",
            )
        )

        title = inspiration[:30] + ("..." if len(inspiration) > 30 else "")
        project_id = self.store.create_project(
            title=title,
            inspiration=inspiration,
            genre=genre_hint,
            target_words=target_chapters * 800,
        )
        console.print(f"\n[dim]项目 ID: {project_id}[/dim]\n")

        total_steps = 4
        for i, (step_name, step_fn) in enumerate([
            ("选题评估", lambda: self._step_topic(project_id, inspiration, genre_hint)),
            ("世界观搭建", lambda: self._step_world(project_id, topic)),
            ("角色设计", lambda: self._step_character(project_id, topic, world)),
            ("大纲编剧", lambda: self._step_outline(project_id, topic, world, characters, target_chapters)),
        ], 1):
            console.print(f"\n[bold cyan][{i}/{total_steps}][/bold cyan] {step_name}...")
            result = await step_fn()
            self._print_stage_result(step_name, result)
            if i == 1:
                topic = result
            elif i == 2:
                world = result
            elif i == 3:
                characters = result
            elif i == 4:
                outline = result

        self.store.update_project_status(project_id, "planned")

        console.print()
        console.print(
            Panel(
                f"[bold green]大纲规划完成[/bold green]\n\n"
                f"项目 ID: [cyan]{project_id}[/cyan]\n"
                f"章节数: {target_chapters}\n\n"
                f"使用 [bold]novel-factory write {project_id}[/bold] 生成正文",
                title="[规划完成]",
                border_style="green",
            )
        )

        return project_id

    # ── 从大纲生成正文 ────────────────────────────────────────

    async def write_from_outline(self, project_id: str) -> str:
        """从已有大纲开始生成正文

        Args:
            project_id: 项目 ID

        Returns:
            project_id: 项目 ID
        """
        project = self.store.get_project(project_id)
        if not project:
            console.print(f"[red]项目不存在: {project_id}[/red]")
            return project_id

        outline = self.store.get_outline(project_id)
        if not outline:
            console.print(f"[red]项目 {project_id} 没有大纲，请先运行 plan[/red]")
            return project_id

        characters = self.store.get_characters(project_id) or {}

        chapters = outline.get("chapters", [])
        if not chapters:
            console.print(f"[red]大纲中没有章节信息[/red]")
            return project_id

        console.print()
        console.print(
            Panel(
                f"[bold cyan]项目:[/bold cyan] {project.get('title', project_id)}\n"
                f"[bold cyan]章节数:[/bold cyan] {len(chapters)}",
                title="[写作] 从大纲生成正文",
                border_style="cyan",
            )
        )

        for i, ch in enumerate(chapters, 1):
            ch_num = ch.get("chapter_num", 0)
            ch_title = ch.get("title", f"第{ch_num}章")

            console.print(f"\n[bold cyan][{i}/{len(chapters)}][/bold cyan] {ch_title}")

            # 场景细纲
            console.print(f"  场景细纲...")
            scenes = await self._step_scene(project_id, ch, characters)
            self.store.save_scene(project_id, ch_num, scenes)

            # 正文（为每个场景生成正文，合并为一章）
            console.print(f"  正文生成...")
            chapter_draft = ""
            scene_list = scenes if isinstance(scenes, list) else [scenes]
            for si, single_scene in enumerate(scene_list):
                draft = await self._step_draft(project_id, ch, single_scene, characters)
                chapter_draft += draft + "\n\n"
            self.store.save_draft(project_id, ch_num, chapter_draft.strip())

        self.store.update_project_status(project_id, "drafted")

        console.print()
        console.print(
            Panel(
                f"[bold green]正文生成完成[/bold green]\n\n"
                f"项目 ID: [cyan]{project_id}[/cyan]\n"
                f"已生成 {len(chapters)} 章\n\n"
                f"使用 [bold]novel-factory review {project_id}[/bold] 运行审校",
                title="[写作完成]",
                border_style="green",
            )
        )

        return project_id

    # ── 内部阶段方法 ──────────────────────────────────────────

    async def _step_topic(
        self, project_id: str, inspiration: str, genre_hint: str | None
    ) -> dict[str, Any]:
        """阶段 1：选题评估

        调用 engine.topic_planner 生成选题方案。
        如果 engine 模块尚未实现，使用占位数据。
        """
        try:
            from novel_factory.engine.planner import generate_proposals

            proposals = await generate_proposals(inspiration, genre_hint)
            result = proposals[0] if proposals else await self._placeholder_topic(inspiration, genre_hint)
        except (ImportError, AttributeError):
            result = await self._placeholder_topic(inspiration, genre_hint)

        self.store.save_topic(project_id, result)
        self.store.update_project_status(project_id, "topic_done")
        return result

    async def _step_world(self, project_id: str, topic: dict) -> dict[str, Any]:
        """阶段 2：世界观搭建"""
        try:
            from novel_factory.engine.worldbuilder import build_world

            result = await build_world(project_id, topic)
        except (ImportError, AttributeError):
            result = await self._placeholder_world(topic)

        self.store.save_world(project_id, result)
        self.store.update_project_status(project_id, "world_done")
        return result

    async def _step_character(
        self, project_id: str, topic: dict, world: dict
    ) -> dict[str, Any]:
        """阶段 3：角色设计"""
        try:
            from novel_factory.engine.character import design_characters

            result = await design_characters(project_id, world)
        except (ImportError, AttributeError):
            result = await self._placeholder_characters(topic, world)

        self.store.save_characters(project_id, result)
        self.store.update_project_status(project_id, "characters_done")
        return result

    async def _step_outline(
        self,
        project_id: str,
        topic: dict,
        world: dict,
        characters: dict,
        target_chapters: int,
    ) -> dict[str, Any]:
        """阶段 4：大纲编剧"""
        try:
            from novel_factory.engine.outliner import generate_outline

            # characters 可能是 list 或 dict，统一处理
            char_list = characters if isinstance(characters, list) else characters.get("protagonist", []) if isinstance(characters, dict) else []
            if isinstance(char_list, dict):
                char_list = [char_list]
            world_list = world if isinstance(world, list) else []

            result = await generate_outline(project_id, topic, world_list, char_list, target_chapters)
        except (ImportError, AttributeError):
            result = await self._placeholder_outline(topic, target_chapters)

        self.store.save_outline(project_id, result)
        self.store.update_project_status(project_id, "outlined")
        return result

    async def _step_scene(
        self, project_id: str, chapter: dict, characters: dict
    ) -> dict[str, Any]:
        """阶段 5：场景细纲"""
        try:
            from novel_factory.engine.scene import plan_scenes

            result = await plan_scenes(project_id, chapter)
        except (ImportError, AttributeError):
            result = await self._placeholder_scene(chapter)

        return result

    async def _step_draft(
        self,
        project_id: str,
        chapter: dict,
        scene: dict,
        characters: dict,
    ) -> str:
        """阶段 6：正文生成"""
        try:
            from novel_factory.engine.writer import write_scene

            char_list = characters if isinstance(characters, list) else []
            result = await write_scene(project_id, chapter, scene, char_list)
        except (ImportError, AttributeError):
            result = await self._placeholder_draft(chapter)

        return result

    async def _step_review(self, project_id: str) -> dict[str, Any]:
        """阶段 7：编辑审校"""
        drafts = self.store.get_all_drafts(project_id)
        outline = self.store.get_outline(project_id) or {}
        chapters = outline.get("chapters", [])

        try:
            from novel_factory.engine.editor import review_chapter

            # 审校第一章作为样本
            if drafts and chapters:
                first_ch = chapters[0]
                first_draft = drafts[0] if isinstance(drafts, list) else drafts
                if isinstance(first_draft, dict):
                    first_draft = first_draft.get("draft", "")
                result = await review_chapter(project_id, first_ch, first_draft)
                result["total_chapters"] = len(drafts) if isinstance(drafts, list) else 1
            else:
                result = await self._placeholder_review(drafts)
        except (ImportError, AttributeError):
            result = await self._placeholder_review(drafts)

        self.store.save_review(project_id, result)
        self.store.update_project_status(project_id, "reviewed")
        return result

    # ── 占位实现（engine 模块就绪后删除） ─────────────────────

    async def _placeholder_topic(self, inspiration: str, genre: str | None) -> dict:
        """占位：选题评估"""
        return {
            "title": inspiration[:20],
            "genre": genre or "通用",
            "premise": f"基于灵感「{inspiration}」的故事",
            "target_audience": "网文读者",
            "selling_points": ["悬念", "反转", "爽感"],
            "recommendation": "推荐采用重生/复仇框架",
            "note": "[占位数据] 请实现 engine.topic_planner.TopicPlanner",
        }

    async def _placeholder_world(self, topic: dict) -> dict:
        """占位：世界观"""
        return {
            "time_period": "现代都市",
            "setting": "一线城市",
            "core_rules": ["重生者拥有前世记忆", "时间线重置"],
            "factions": ["主角阵营", "反派阵营", "中立势力"],
            "power_system": None,
            "note": "[占位数据] 请实现 engine.world_builder.WorldBuilder",
        }

    async def _placeholder_characters(self, topic: dict, world: dict) -> dict:
        """占位：角色设计"""
        return {
            "protagonist": {
                "name": "待定",
                "role": "protagonist",
                "personality": "隐忍、果断",
                "core_desire": "复仇",
                "arc": "从弱势到强势",
            },
            "antagonist": {
                "name": "待定",
                "role": "antagonist",
                "personality": "虚伪、贪婪",
                "core_desire": "权力",
            },
            "supporting": [],
            "note": "[占位数据] 请实现 engine.character_designer.CharacterDesigner",
        }

    async def _placeholder_outline(self, topic: dict, target_chapters: int) -> dict:
        """占位：大纲"""
        chapters = []
        for i in range(1, target_chapters + 1):
            chapters.append({
                "chapter_num": i,
                "title": f"第{i}章",
                "core_event": f"第{i}章核心事件",
                "emotion_position": "铺垫" if i < target_chapters // 3 else ("高潮" if i > target_chapters * 2 // 3 else "过渡"),
                "hook": f"第{i}章末尾悬念",
            })
        return {
            "total_chapters": target_chapters,
            "structure": "三幕式",
            "chapters": chapters,
            "plot_lines": ["主线：复仇"],
            "note": "[占位数据] 请实现 engine.outline_writer.OutlineWriter",
        }

    async def _placeholder_scene(self, chapter: dict) -> dict:
        """占位：场景细纲"""
        return {
            "chapter_num": chapter.get("chapter_num", 0),
            "scenes": [
                {
                    "scene_num": 1,
                    "location": "待定",
                    "characters": ["主角"],
                    "conflict": chapter.get("core_event", ""),
                    "emotion_arc": {"start": "平静", "peak": "紧张", "end": "悬念"},
                    "detailed_plan": f"展开{chapter.get('title', '本章')}的核心场景",
                }
            ],
            "note": "[占位数据] 请实现 engine.scene_planner.ScenePlanner",
        }

    async def _placeholder_draft(self, chapter: dict) -> str:
        """占位：正文"""
        ch_num = chapter.get("chapter_num", 0)
        title = chapter.get("title", f"第{ch_num}章")
        event = chapter.get("core_event", "")
        return (
            f"# {title}\n\n"
            f"<!-- [占位正文] 请实现 engine.novel_writer.NovelWriter -->\n\n"
            f"核心事件：{event}\n\n"
            f"（此处应为 AI 生成的正文内容，约 800-1500 字）\n"
        )

    async def _placeholder_review(self, drafts: list[tuple[int, str]]) -> dict:
        """占位：审校"""
        total_words = sum(len(text) for _, text in drafts)
        return {
            "total_chapters": len(drafts),
            "total_words": total_words,
            "checks": {
                "character_consistency": "待检查",
                "timeline_consistency": "待检查",
                "foreshadow_tracking": "待检查",
                "pacing": "待检查",
                "dialogue_quality": "待检查",
            },
            "issues": [],
            "score": None,
            "note": "[占位数据] 请实现 engine.editor.Editor",
        }

    # ── 工具方法 ──────────────────────────────────────────────

    @staticmethod
    def _print_stage_result(stage_name: str, data: Any):
        """打印阶段结果到控制台"""
        console.print()
        if isinstance(data, dict):
            # 提取关键信息显示
            lines = []
            for key, value in data.items():
                if key == "note":
                    continue
                if isinstance(value, (list, dict)):
                    display = str(value)[:100]
                else:
                    display = str(value)[:200]
                lines.append(f"[bold]{key}:[/bold] {display}")
            content = "\n".join(lines)
        else:
            content = str(data)[:500]

        console.print(
            Panel(
                content,
                title=f"[{stage_name}] 中间结果",
                border_style="blue",
                padding=(1, 2),
            )
        )
