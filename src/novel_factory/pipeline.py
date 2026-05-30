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
    ("metadata", "元数据生成"),
    ("scene", "场景细纲"),
    ("draft", "正文生成"),
    ("review", "编辑审校"),
]


class NovelPipeline:
    """小说生成流水线编排器

    用法:
        pipeline = NovelPipeline()
        project_id = await pipeline.run_full_pipeline("重生复仇打脸", params={...})
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
        params: dict | None = None,
    ) -> str:
        """完整流程：选题 -> 世界观 -> 角色 -> 大纲 -> 场景 -> 正文 -> 审校"""
        params = params or {}
        genre_hint = params.get("genre_minor") or params.get("genre_major") or genre_hint
        target_words = params.get("target_words") or target_words

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

        title = inspiration[:30] + ("..." if len(inspiration) > 30 else "")
        project_id = self.store.create_project(
            title=title, inspiration=inspiration, genre=genre_hint, target_words=target_words,
        )
        self.store.save_params(project_id, params)
        console.print(f"\n[dim]项目 ID: {project_id}[/dim]\n")

        # 计算章节数
        if params.get("target_chapters"):
            target_chapters = params["target_chapters"]
        else:
            cw = params.get("chapter_word_range", [2000, 3000])
            avg = sum(cw) // 2 if isinstance(cw, list) else 2500
            target_chapters = max(3, target_words // avg)

        chapters = []
        total_steps = len(STAGES)
        for i, (stage_key, stage_name) in enumerate(STAGES, 1):
            console.print(f"\n[bold cyan][{i}/{total_steps}][/bold cyan] {stage_name}...")

            if stage_key == "topic":
                proposals = await self._step_topic(project_id, inspiration, genre_hint, params)
                self._print_stage_result("选题评估", proposals)
                # 下游步骤使用选中的方案
                topic = next((p for p in proposals if p.get("selected")), proposals[0]) if proposals else {}
            elif stage_key == "world":
                world = await self._step_world(project_id, topic, params)
                self._print_stage_result("世界观设定", world)
            elif stage_key == "character":
                characters = await self._step_character(project_id, topic, world, params)
                self._print_stage_result("角色设计", characters)
            elif stage_key == "outline":
                outline = await self._step_outline(project_id, topic, world, characters, target_chapters, params)
                self._print_stage_result("章节大纲", outline)
                chapters = outline.get("chapters", [])
            elif stage_key == "metadata":
                metadata = await self._step_metadata(project_id, topic, outline, characters, params)
                self._print_stage_result("书籍元数据", metadata)
            elif stage_key == "scene":
                for ch in chapters:
                    ch_num = ch.get("chapter_num", 0)
                    console.print(f"  场景细纲: {ch.get('title', f'第{ch_num}章')}")
                    scenes = await self._step_scene(project_id, ch, characters, params)
                    self.store.save_scene(project_id, ch_num, scenes)
            elif stage_key == "draft":
                for ch in chapters:
                    ch_num = ch.get("chapter_num", 0)
                    console.print(f"  正文生成: {ch.get('title', f'第{ch_num}章')}")
                    ch_scenes = self.store.get_scene(project_id, ch_num) or []
                    scene_list = ch_scenes if isinstance(ch_scenes, list) else [ch_scenes]
                    chapter_draft = ""
                    for single_scene in scene_list:
                        draft = await self._step_draft(project_id, ch, single_scene, characters, params)
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
                f"使用 [bold]novel-factory review {project_id}[/bold] 重新审校",
                title="[完成]", border_style="green",
            )
        )
        return project_id

    # ── 只做到大纲 ────────────────────────────────────────────

    async def plan_only(
        self, inspiration: str, genre_hint: str | None = None,
        target_chapters: int = 10, params: dict | None = None,
    ) -> str:
        """只做到大纲阶段"""
        params = params or {}
        genre_hint = params.get("genre_minor") or params.get("genre_major") or genre_hint

        console.print()
        console.print(
            Panel(
                f"[bold cyan]灵感:[/bold cyan] {inspiration}\n"
                f"[bold cyan]题材:[/bold cyan] {genre_hint or '待定'}\n"
                f"[bold cyan]目标章节:[/bold cyan] {target_chapters}",
                title="[规划] 只生成大纲", border_style="cyan",
            )
        )

        title = inspiration[:30] + ("..." if len(inspiration) > 30 else "")
        project_id = self.store.create_project(
            title=title, inspiration=inspiration, genre=genre_hint, target_words=target_chapters * 800,
        )
        self.store.save_params(project_id, params)
        console.print(f"\n[dim]项目 ID: {project_id}[/dim]\n")

        for i, (step_name, step_fn) in enumerate([
            ("选题评估", lambda: self._step_topic(project_id, inspiration, genre_hint, params)),
            ("世界观搭建", lambda: self._step_world(project_id, topic, params)),
            ("角色设计", lambda: self._step_character(project_id, topic, world, params)),
            ("大纲编剧", lambda: self._step_outline(project_id, topic, world, characters, target_chapters, params)),
        ], 1):
            console.print(f"\n[bold cyan][{i}/4][/bold cyan] {step_name}...")
            result = await step_fn()
            self._print_stage_result(step_name, result)
            if i == 1:
                proposals = result
                topic = next((p for p in proposals if p.get("selected")), proposals[0]) if proposals else {}
            elif i == 2: world = result
            elif i == 3: characters = result
            elif i == 4: outline = result

        self.store.update_project_status(project_id, "planned")
        console.print()
        console.print(Panel(
            f"[bold green]大纲规划完成[/bold green]\n\n项目 ID: [cyan]{project_id}[/cyan]\n章节数: {target_chapters}",
            title="[规划完成]", border_style="green",
        ))
        return project_id

    # ── 从大纲生成正文 ────────────────────────────────────────

    async def write_from_outline(self, project_id: str) -> str:
        """从已有大纲开始生成正文"""
        project = self.store.get_project(project_id)
        if not project:
            console.print(f"[red]项目不存在: {project_id}[/red]")
            return project_id

        outline = self.store.get_outline(project_id)
        if not outline:
            console.print(f"[red]项目 {project_id} 没有大纲，请先运行 plan[/red]")
            return project_id

        characters = self.store.get_characters(project_id) or {}
        params = self.store.get_params(project_id) or {}
        chapters = outline.get("chapters", [])
        if not chapters:
            console.print(f"[red]大纲中没有章节信息[/red]")
            return project_id

        console.print()
        console.print(Panel(
            f"[bold cyan]项目:[/bold cyan] {project.get('title', project_id)}\n"
            f"[bold cyan]章节数:[/bold cyan] {len(chapters)}",
            title="[写作] 从大纲生成正文", border_style="cyan",
        ))

        for i, ch in enumerate(chapters, 1):
            ch_num = ch.get("chapter_num", 0)
            console.print(f"\n[bold cyan][{i}/{len(chapters)}][/bold cyan] {ch.get('title', f'第{ch_num}章')}")
            console.print(f"  场景细纲...")
            scenes = await self._step_scene(project_id, ch, characters, params)
            self.store.save_scene(project_id, ch_num, scenes)

            console.print(f"  正文生成...")
            scene_list = scenes if isinstance(scenes, list) else [scenes]
            chapter_draft = ""
            for single_scene in scene_list:
                draft = await self._step_draft(project_id, ch, single_scene, characters, params)
                chapter_draft += draft + "\n\n"
            self.store.save_draft(project_id, ch_num, chapter_draft.strip())

        self.store.update_project_status(project_id, "drafted")
        console.print()
        console.print(Panel(
            f"[bold green]正文生成完成[/bold green]\n\n项目 ID: [cyan]{project_id}[/cyan]\n已生成 {len(chapters)} 章",
            title="[写作完成]", border_style="green",
        ))
        return project_id

    # ── 内部阶段方法 ──────────────────────────────────────────

    async def _step_topic(self, project_id: str, inspiration: str, genre_hint: str | None, params: dict) -> list[dict]:
        """阶段 1：选题评估，返回全部方案列表"""
        try:
            from novel_factory.engine.planner import generate_proposals
            proposals = await generate_proposals(inspiration, genre_hint, params)
            if not proposals:
                proposals = [await self._placeholder_topic(inspiration, genre_hint)]
        except Exception:
            proposals = [await self._placeholder_topic(inspiration, genre_hint)]
        # 给每个方案注入 id 和 project_id
        for i, p in enumerate(proposals):
            p.setdefault("id", f"topic_{i+1}")
            p["project_id"] = project_id
            p.setdefault("selected", i == 0)
        self.store.save_topic(project_id, proposals)
        self.store.update_project_status(project_id, "topic_done")
        return proposals

    async def _step_world(self, project_id: str, topic: dict, params: dict) -> dict:
        """阶段 2：世界观搭建"""
        try:
            from novel_factory.engine.worldbuilder import build_world
            result = await build_world(project_id, topic, params)
        except Exception:
            result = await self._placeholder_world(topic)
        self.store.save_world(project_id, result)
        self.store.update_project_status(project_id, "world_done")
        return result

    async def _step_character(self, project_id: str, topic: dict, world: dict, params: dict) -> dict:
        """阶段 3：角色设计"""
        try:
            from novel_factory.engine.character import design_characters
            result = await design_characters(project_id, world, params)
        except Exception:
            result = await self._placeholder_characters(topic, world)
        self.store.save_characters(project_id, result)
        self.store.update_project_status(project_id, "characters_done")
        return result

    async def _step_outline(self, project_id: str, topic: dict, world: dict, characters: dict, target_chapters: int, params: dict) -> dict:
        """阶段 4：大纲编剧"""
        try:
            from novel_factory.engine.outliner import generate_outline
            char_list = characters if isinstance(characters, list) else []
            world_list = world if isinstance(world, list) else []
            result = await generate_outline(project_id, topic, world_list, char_list, target_chapters, params)
        except Exception:
            result = await self._placeholder_outline(topic, target_chapters)
        self.store.save_outline(project_id, result)
        self.store.update_project_status(project_id, "outlined")
        return result

    async def _step_metadata(self, project_id: str, topic: dict, outline: dict, characters: dict, params: dict) -> dict:
        """阶段 5：书籍元数据生成"""
        try:
            from novel_factory.engine.metadata import generate_metadata
            result = await generate_metadata(project_id, topic, outline, characters, params)
        except Exception:
            result = await self._placeholder_metadata(topic)
        self.store.save_metadata(project_id, result)
        self.store.update_project_status(project_id, "metadata_done")
        return result

    async def _step_scene(self, project_id: str, chapter: dict, characters: dict, params: dict) -> dict:
        """阶段 5：场景细纲"""
        try:
            from novel_factory.engine.scene import plan_scenes
            result = await plan_scenes(project_id, chapter)
        except Exception:
            result = await self._placeholder_scene(chapter)
        return result

    async def _step_draft(self, project_id: str, chapter: dict, scene: dict, characters: dict, params: dict) -> str:
        """阶段 6：正文生成"""
        try:
            from novel_factory.engine.writer import write_scene
            char_list = characters if isinstance(characters, list) else []
            result = await write_scene(project_id, chapter, scene, char_list, params=params)
        except Exception:
            result = await self._placeholder_draft(chapter)
        return result

    async def _step_review(self, project_id: str) -> dict:
        """阶段 7：编辑审校"""
        drafts = self.store.get_all_drafts(project_id)
        outline = self.store.get_outline(project_id) or {}
        chapters = outline.get("chapters", [])
        try:
            from novel_factory.engine.editor import review_chapter
            if drafts and chapters:
                first_ch = chapters[0]
                first_draft = drafts[0] if isinstance(drafts, list) else drafts
                if isinstance(first_draft, dict):
                    first_draft = first_draft.get("draft", "")
                result = await review_chapter(project_id, first_ch, first_draft)
                result["total_chapters"] = len(drafts) if isinstance(drafts, list) else 1
            else:
                result = await self._placeholder_review(drafts)
        except Exception:
            result = await self._placeholder_review(drafts)
        self.store.save_review(project_id, result)
        self.store.update_project_status(project_id, "reviewed")
        return result

    # ── 占位实现 ──────────────────────────────────────────────

    async def _placeholder_topic(self, inspiration: str, genre: str | None) -> dict:
        return {
            "id": "topic_1",
            "title": inspiration[:20],
            "logline": f"基于灵感「{inspiration}」的故事",
            "theme": "待定",
            "genre": genre or "通用",
            "target_audience": "",
            "conflict": "",
            "hook": "",
            "platforms": [],
            "word_count": "",
            "score": 50,
            "reasoning": "占位方案，请重新生成",
            "selected": True,
        }

    async def _placeholder_world(self, topic: dict) -> dict:
        return [{"category": "时代背景", "content": "现代都市"}, {"category": "核心规则", "content": "重生者拥有前世记忆"}]

    async def _placeholder_characters(self, topic: dict, world: dict) -> list:
        return [{"name": "待定", "role": "protagonist", "personality": "隐忍、果断"}]

    async def _placeholder_outline(self, topic: dict, target_chapters: int) -> dict:
        chapters = [{"chapter_num": i, "title": f"第{i}章", "core_event": f"第{i}章核心事件", "hook": f"悬念{i}"} for i in range(1, target_chapters + 1)]
        return {"chapters": chapters, "foreshadows": []}

    async def _placeholder_metadata(self, topic: dict) -> dict:
        title = topic.get("title", "未命名") if topic else "未命名"
        return {
            "title": title,
            "title_candidates": [title],
            "synopsis_short": "",
            "synopsis_medium": "",
            "synopsis_long": "",
            "tags": [],
            "category": "",
            "category_path": "",
        }

    async def _placeholder_scene(self, chapter: dict) -> list:
        return [{"number": 1, "location": "待定", "conflict": chapter.get("core_event", ""), "emotion_start": "平静", "emotion_end": "悬念"}]

    async def _placeholder_draft(self, chapter: dict) -> str:
        return f"# {chapter.get('title', '未知章节')}\n\n（占位正文）\n"

    async def _placeholder_review(self, drafts: list) -> dict:
        return {"total_chapters": len(drafts) if isinstance(drafts, list) else 0, "total_words": 0, "checks": {}, "issues": [], "score": None}

    # ── 工具方法 ──────────────────────────────────────────────

    @staticmethod
    def _print_stage_result(stage_name: str, data: Any):
        console.print()
        if isinstance(data, dict):
            lines = [f"[bold]{k}:[/bold] {str(v)[:200]}" for k, v in data.items() if k != "note"]
            content = "\n".join(lines)
        elif isinstance(data, list):
            content = "\n".join(f"- {str(item)[:150]}" for item in data[:5])
        else:
            content = str(data)[:500]
        console.print(Panel(content, title=f"[{stage_name}] 中间结果", border_style="blue", padding=(1, 2)))
