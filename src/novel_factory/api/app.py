"""NovelFactory API 服务

路由概览：
  - 项目管理: /api/projects/*
  - 流水线控制: /api/projects/{id}/pipeline/*
  - 数据查询: /api/projects/{id}/topic|world|characters|outline|chapters|review
  - 系统配置: /api/config/*
"""

from __future__ import annotations

import asyncio
import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# ── 日志配置 ──────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("novel_factory")
logger.setLevel(logging.DEBUG)

# 后台任务线程池（用于流水线，避免阻塞主事件循环）
_bg_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pipeline")

_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# app.log: INFO 及以上（关键业务事件）
_app = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
_app.setLevel(logging.INFO)
_app.setFormatter(_formatter)
logger.addHandler(_app)

# debug.log: DEBUG 及以上（全量，含 HTTP 细节）
_dbg = logging.FileHandler(LOG_DIR / "debug.log", encoding="utf-8")
_dbg.setLevel(logging.DEBUG)
_dbg.setFormatter(_formatter)
logger.addHandler(_dbg)

# error.log: 仅 ERROR 及以上
_err = logging.FileHandler(LOG_DIR / "error.log", encoding="utf-8")
_err.setLevel(logging.ERROR)
_err.setFormatter(_formatter)
logger.addHandler(_err)

# 控制台
_console = logging.StreamHandler()
_console.setLevel(logging.INFO)
_console.setFormatter(_formatter)
logger.addHandler(_console)

logger.propagate = False

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from novel_factory.api.deps import get_pipeline, get_store, get_context_store
from novel_factory.api.task_registry import registry
from novel_factory.api.schemas import (
    GENRE_MATRIX,
    BookMetadata,
    ChapterResponse,
    CharacterResponse,
    ConfigResponse,
    ConfigUpdateRequest,
    ConfirmRequest,
    OutlineResponse,
    PipelineStatus,
    ProjectCreate,
    ProjectListItem,
    ProjectResponse,
    ReviewResponse,
    StageConfirmRequest,
    StagesResponse,
    TopicResponse,
    WorldSettingResponse,
)
from novel_factory.config import settings

# ── 流水线阶段定义 ──────────────────────────────────────────

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

# ── 流水线状态内存存储（进程内） ────────────────────────────

# project_id -> PipelineStatus 数据
_pipeline_states: dict[str, dict[str, Any]] = {}

# ── 阶段状态追踪（进程内） ─────────────────────────────────
# project_id -> {stage_name: StageInfo}
_stage_states: dict[str, dict[str, dict[str, Any]]] = {}

# 所有阶段列表（与流水线一致）
_ALL_STAGES = ["topic", "world", "character", "outline", "metadata", "scene", "draft", "review"]


def _selected_topic(topic_data: dict | list | None) -> dict:
    """从选题方案列表中取出选中的方案（兼容旧格式单个 dict）"""
    if not topic_data:
        return {}
    if isinstance(topic_data, list):
        return next((t for t in topic_data if t.get("selected")), topic_data[0]) if topic_data else {}
    return topic_data


def _get_stage_states(project_id: str) -> dict[str, dict[str, Any]]:
    """获取或初始化项目的阶段状态"""
    if project_id not in _stage_states:
        _stage_states[project_id] = {
            stage: {"status": "pending", "updated_at": None}
            for stage in _ALL_STAGES
        }
    return _stage_states[project_id]


def _update_stage_state(project_id: str, stage: str, status: str) -> None:
    """更新某个阶段的状态和时间戳"""
    states = _get_stage_states(project_id)
    if stage in states:
        states[stage]["status"] = status
        states[stage]["updated_at"] = datetime.now().isoformat()


def _get_or_create_state(project_id: str) -> dict[str, Any]:
    """获取或创建流水线状态"""
    if project_id not in _pipeline_states:
        _pipeline_states[project_id] = {
            "project_id": project_id,
            "current_stage": None,
            "current_stage_label": None,
            "progress_percent": 0.0,
            "total_stages": len(STAGES),
            "completed_stages": 0,
            "needs_confirmation": False,
            "status": "idle",
            "error": None,
            "updated_at": datetime.now().isoformat(),
        }
    return _pipeline_states[project_id]


def _update_state(project_id: str, **kwargs: Any) -> None:
    """更新流水线状态"""
    state = _get_or_create_state(project_id)
    state.update(kwargs)
    state["updated_at"] = datetime.now().isoformat()
    if state["total_stages"] > 0:
        state["progress_percent"] = round(
            state["completed_stages"] / state["total_stages"] * 100, 1
        )


# ── 创建 FastAPI 应用 ───────────────────────────────────────

app = FastAPI(
    title="NovelFactory API",
    description="小说工厂后端 API — 从灵感到全平台分发的多模态内容流水线",
    version="0.1.0",
)

# CORS：允许本地开发前端（Vite 默认端口 5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 全局异常处理 ────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """统一 JSON 错误响应"""
    from fastapi.responses import JSONResponse

    logger.error("未捕获异常: %s %s -> %s", request.method, request.url, str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
        },
    )


# ── 项目管理 ────────────────────────────────────────────────

@app.post("/api/projects", response_model=ProjectResponse, status_code=201)
async def create_project(body: ProjectCreate):
    """创建新项目

    接收 ProjectCreate（5 级参数），创建项目并返回详情。
    参数中的扩展字段保存到 project.json 中。
    """
    logger.info("创建项目请求: premise_len=%d, platforms=%s, length_type=%s", len(body.premise), body.platforms, body.length_type)
    logger.debug("创建项目参数: %s", body.model_dump_json(indent=2)[:500])
    store = get_store()
    data = body.resolve_defaults()

    # 用 premise 的前 30 字作为 title
    title = data["premise"][:30] + ("..." if len(data["premise"]) > 30 else "")

    project_id = store.create_project(
        title=title,
        inspiration=data["premise"],
        genre=data.get("genre_major") or data.get("genre_minor"),
        target_words=data["target_words"],
    )

    # 将扩展参数写入 project.json
    project = store.get_project(project_id)
    if project:
        # 合并 ProjectCreate 的所有字段到 project 元数据
        for key in [
            "premise", "platforms", "length_type",
            "genre_major", "genre_minor", "target_audience", "tone",
            "protagonist_name", "protagonist_desc",
            "antagonist_name", "antagonist_desc",
            "has_romance", "romance_desc", "supporting_count",
            "world_setting", "world_custom", "reference_works", "forbidden_elements",
            "target_chapters", "chapter_word_range",
            "climax_density", "climax_interval", "foreshadow_count",
            "model_provider", "style_sample",
        ]:
            if key in data:
                project[key] = data[key]
        # 回写
        import json
        from pathlib import Path

        project_path = store.data_dir / project_id / "project.json"
        project_path.write_text(
            json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    logger.info("项目创建成功: id=%s, title=%s", project_id, title)
    return ProjectResponse(**project)


@app.get("/api/projects", response_model=list[ProjectListItem])
async def list_projects():
    """列出所有项目"""
    store = get_store()
    projects = store.list_projects()
    return [ProjectListItem(**p) for p in projects]


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """获取项目详情"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    return ProjectResponse(**project)


@app.delete("/api/projects/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """删除项目（移动到回收站或直接删除）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    # 清理流水线状态
    _pipeline_states.pop(project_id, None)

    # 删除项目目录
    import shutil

    project_dir = store.get_project_dir(project_id)
    if project_dir.exists():
        shutil.rmtree(project_dir)

    # 从索引中移除
    index = store._load_index()
    index.pop(project_id, None)
    store._save_index(index)

    return None


# ── 流水线控制 ──────────────────────────────────────────────

def _run_in_background(coro):
    """在独立线程中运行异步任务，不阻塞主事件循环"""
    def _wrapper():
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
    _bg_executor.submit(_wrapper)


async def _run_pipeline_background(
    project_id: str,
    mode: str,
    params: dict[str, Any],
) -> None:
    """后台运行流水线任务"""
    try:
        _update_state(project_id, status="running", current_stage=STAGES[0][0],
                       current_stage_label=STAGES[0][1])

        pipeline = get_pipeline()
        store = get_store()

        if mode == "full":
            # 完整流水线：逐阶段执行，每阶段更新状态
            inspiration = params["inspiration"]
            genre_hint = params.get("genre_hint")
            target_words = params.get("target_words", 8000)

            for i, (stage_key, stage_label) in enumerate(STAGES):
                _update_state(
                    project_id,
                    current_stage=stage_key,
                    current_stage_label=stage_label,
                    completed_stages=i,
                )

                if stage_key == "topic":
                    result = await pipeline._step_topic(project_id, inspiration, genre_hint, params)
                elif stage_key == "world":
                    topic = _selected_topic(store.get_topic(project_id))
                    result = await pipeline._step_world(project_id, topic, params)
                elif stage_key == "character":
                    topic = _selected_topic(store.get_topic(project_id))
                    world = store.get_world(project_id) or {}
                    result = await pipeline._step_character(project_id, topic, world, params)
                elif stage_key == "outline":
                    topic = _selected_topic(store.get_topic(project_id))
                    world = store.get_world(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    target_chapters = params.get("target_chapters", max(3, target_words // 800))
                    result = await pipeline._step_outline(
                        project_id, topic, world, characters, target_chapters, params
                    )
                elif stage_key == "metadata":
                    topic = _selected_topic(store.get_topic(project_id))
                    outline = store.get_outline(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    result = await pipeline._step_metadata(project_id, topic, outline, characters, params)
                elif stage_key == "scene":
                    outline = store.get_outline(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    chapters = outline.get("chapters", [])
                    for ch in chapters:
                        ch_num = ch.get("chapter_num", 0)
                        scenes = await pipeline._step_scene(project_id, ch, characters, params)
                        store.save_scene(project_id, ch_num, scenes)
                elif stage_key == "draft":
                    outline = store.get_outline(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    chapters = outline.get("chapters", [])
                    # 0019: 从 ContextStore 读前文摘要并保存本章摘要
                    ctx_store = get_context_store()
                    from novel_factory.engine.memory import generate_summary
                    for ch in chapters:
                        ch_num = ch.get("chapter_num", 0)
                        ch_scenes = store.get_scene(project_id, ch_num) or []
                        chapter_draft = ""
                        scene_list = ch_scenes if isinstance(ch_scenes, list) else [ch_scenes]
                        prev_summary = ctx_store.get_recent_summaries(project_id, ch_num, window=3)
                        for single_scene in scene_list:
                            draft = await pipeline._step_draft(
                                project_id, ch, single_scene, characters, params,
                                prev_summary=prev_summary,
                            )
                            chapter_draft += draft + "\n\n"
                        full_draft = chapter_draft.strip()
                        store.save_draft(project_id, ch_num, full_draft)
                        # 0019: 生成并保存本章摘要
                        try:
                            summary = await generate_summary(full_draft, max_words=150)
                            ctx_store.save_summary(project_id, ch_num, summary)
                        except Exception as e:
                            logger.warning("摘要生成失败: ch%d: %s", ch_num, e)
                elif stage_key == "review":
                    result = await pipeline._step_review(project_id)

            store.update_project_status(project_id, "complete")
            _update_state(
                project_id,
                status="complete",
                current_stage=None,
                current_stage_label=None,
                completed_stages=len(STAGES),
            )

        elif mode == "plan":
            # 只做到大纲
            inspiration = params["inspiration"]
            genre_hint = params.get("genre_hint")
            target_chapters = params.get("target_chapters", 10)

            for i, (stage_key, stage_label) in enumerate(STAGES[:4]):
                _update_state(
                    project_id,
                    current_stage=stage_key,
                    current_stage_label=stage_label,
                    completed_stages=i,
                )

                if stage_key == "topic":
                    result = await pipeline._step_topic(project_id, inspiration, genre_hint, params)
                elif stage_key == "world":
                    topic = _selected_topic(store.get_topic(project_id))
                    result = await pipeline._step_world(project_id, topic, params)
                elif stage_key == "character":
                    topic = _selected_topic(store.get_topic(project_id))
                    world = store.get_world(project_id) or {}
                    result = await pipeline._step_character(project_id, topic, world, params)
                elif stage_key == "outline":
                    topic = _selected_topic(store.get_topic(project_id))
                    world = store.get_world(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    result = await pipeline._step_outline(
                        project_id, topic, world, characters, target_chapters
                    )

            store.update_project_status(project_id, "planned")
            _update_state(
                project_id,
                status="complete",
                current_stage=None,
                current_stage_label=None,
                completed_stages=4,
            )

        elif mode == "write":
            # 从大纲生成正文
            await pipeline.write_from_outline(project_id)
            _update_state(
                project_id,
                status="complete",
                current_stage=None,
                current_stage_label=None,
                completed_stages=len(STAGES),
            )

    except Exception as e:
        _update_state(
            project_id,
            status="error",
            error=f"{type(e).__name__}: {e}",
        )
        traceback.print_exc()


@app.post("/api/projects/{project_id}/pipeline/start")
async def pipeline_start(project_id: str, background_tasks: BackgroundTasks):
    """启动完整流水线（后台异步运行）"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    state = _get_or_create_state(project_id)
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="流水线正在运行中")

    params = {
        "inspiration": project.get("inspiration") or project.get("premise", ""),
        "genre_hint": project.get("genre") or project.get("genre_major"),
        "genre_major": project.get("genre_major") or project.get("genre"),
        "target_words": project.get("target_words", 8000),
        "target_chapters": project.get("target_chapters"),
        "target_audience": project.get("target_audience", "male"),
    }

    _run_in_background(_run_pipeline_background(project_id, "full", params))
    _update_state(project_id, status="running", current_stage=STAGES[0][0],
                   current_stage_label=STAGES[0][1])

    return {"message": "完整流水线已启动", "project_id": project_id}


@app.post("/api/projects/{project_id}/pipeline/plan")
async def pipeline_plan(project_id: str, background_tasks: BackgroundTasks):
    """只运行到大纲阶段"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    state = _get_or_create_state(project_id)
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="流水线正在运行中")

    # 计算章节数：target_words / chapter_word_count
    chapter_word_count = project.get("chapter_word_count", 3000)
    target_words = project.get("target_words", 8000)
    calculated_chapters = max(3, target_words // chapter_word_count) if chapter_word_count > 0 else 10

    params = {
        "inspiration": project.get("inspiration") or project.get("premise", ""),
        "genre_hint": project.get("genre") or project.get("genre_major"),
        "genre_major": project.get("genre_major") or project.get("genre"),
        "target_words": target_words,
        "target_chapters": project.get("target_chapters", calculated_chapters),
        "chapter_word_count": chapter_word_count,
        "target_audience": project.get("target_audience", "male"),
    }

    _run_in_background(_run_pipeline_background(project_id, "plan", params))
    _update_state(project_id, status="running", current_stage=STAGES[0][0],
                   current_stage_label=STAGES[0][1])

    return {"message": "大纲规划流水线已启动", "project_id": project_id}


@app.post("/api/projects/{project_id}/pipeline/stage/{stage}")
async def pipeline_stage(project_id: str, stage: str, background_tasks: BackgroundTasks, body: dict | None = None):
    """运行单个阶段（通过 TaskRegistry 管理）"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    valid_stages = [s[0] for s in STAGES]
    if stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"无效阶段: {stage}，可选: {valid_stages}")

    # 计算章节数
    chapter_word_count = project.get("chapter_word_count", 3000)
    target_words = project.get("target_words", 8000)
    calculated_chapters = max(3, target_words // chapter_word_count) if chapter_word_count > 0 else 10
    target_chapters = project.get("target_chapters") or calculated_chapters

    params = {
        "inspiration": project.get("inspiration") or project.get("premise", ""),
        "genre_hint": project.get("genre") or project.get("genre_major"),
        "genre_major": project.get("genre_major") or project.get("genre"),
        "target_words": target_words,
        "target_chapters": target_chapters,
        "chapter_word_count": chapter_word_count,
        "target_audience": project.get("target_audience", "male"),
    }

    # 接收 feedback 和批量参数
    if body:
        feedback = body.get("feedback")
        if feedback:
            params["feedback"] = feedback
        # 批量生成参数（draft/scene/review 阶段）
        if body.get("start_chapter"):
            params["start_chapter"] = body["start_chapter"]
        if body.get("batch_size"):
            params["batch_size"] = min(body["batch_size"], 10)
        if body.get("force"):
            params["force"] = True

    # 通过 TaskRegistry 提交（幂等+互斥）
    try:
        task, is_new = await registry.submit(project_id, stage, params)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if not is_new:
        # 幂等命中：返回已有任务
        return task.to_dict()

    # 启动后台执行
    await registry.transition(task.id, "running")
    _run_in_background(_execute_stage_task(task))

    stage_label = dict(STAGES).get(stage, stage)
    return {"task_id": task.id, "message": f"阶段 [{stage_label}] 已启动", "project_id": project_id, "stage": stage}


async def _execute_stage_task(task) -> None:
    """后台执行阶段任务（通过 TaskRegistry 管理状态）"""
    project_id = task.project_id
    stage = task.stage
    params = task.params
    try:
        pipeline = get_pipeline()
        store = get_store()
        inspiration = params["inspiration"]
        genre_hint = params.get("genre_hint")
        target_words = params.get("target_words", 8000)

        if stage == "topic":
            await pipeline._step_topic(project_id, inspiration, genre_hint, params)
        elif stage == "world":
            topic = _selected_topic(store.get_topic(project_id))
            await pipeline._step_world(project_id, topic, params)
        elif stage == "character":
            topic = _selected_topic(store.get_topic(project_id))
            world = store.get_world(project_id) or {}
            await pipeline._step_character(project_id, topic, world, params)
        elif stage == "outline":
            topic = _selected_topic(store.get_topic(project_id))
            world = store.get_world(project_id) or {}
            characters = store.get_characters(project_id) or {}
            chapter_word_count = params.get("chapter_word_count", 3000)
            target_chapters = params.get("target_chapters", max(3, target_words // chapter_word_count) if chapter_word_count > 0 else 10)
            await pipeline._step_outline(project_id, topic, world, characters, target_chapters, params)
        elif stage == "metadata":
            topic = _selected_topic(store.get_topic(project_id))
            outline = store.get_outline(project_id) or {}
            characters = store.get_characters(project_id) or {}
            await pipeline._step_metadata(project_id, topic, outline, characters, params)
        elif stage == "scene":
            outline = store.get_outline(project_id) or {}
            characters = store.get_characters(project_id) or {}
            chapters = outline.get("chapters", [])
            for i, ch in enumerate(chapters):
                if task.cancel_requested:
                    await registry.transition(task.id, "cancelled")
                    return
                ch_num = ch.get("chapter_num", 0)
                await registry.update_progress(task.id, i, len(chapters), f"第 {ch_num} 章")
                scenes = await pipeline._step_scene(project_id, ch, characters, params)
                store.save_scene(project_id, ch_num, scenes)
        elif stage == "draft":
            outline = store.get_outline(project_id) or {}
            characters = store.get_characters(project_id) or {}
            chapters = outline.get("chapters", [])
            ctx_store = get_context_store()
            from novel_factory.engine.memory import generate_summary

            # 批量参数
            start_ch = params.get("start_chapter", 1)
            batch = params.get("batch_size", len(chapters))
            force = params.get("force", False)
            # 筛选本次要生成的章节
            target_chapters = [ch for ch in chapters if ch.get("chapter_num", 0) >= start_ch][:batch]

            for i, ch in enumerate(target_chapters):
                if task.cancel_requested:
                    await registry.transition(task.id, "cancelled")
                    return
                ch_num = ch.get("chapter_num", 0)
                await registry.update_progress(task.id, i, len(target_chapters), f"第 {ch_num} 章")

                # 断点续写：跳过已有正文
                existing = store.get_draft(project_id, ch_num)
                if existing and not force:
                    logger.info("跳过已有正文: ch%d", ch_num)
                    continue

                # 读取前文摘要
                prev_summary = ctx_store.get_recent_summaries(project_id, ch_num, window=3)
                ch_scenes = store.get_scene(project_id, ch_num) or []
                chapter_draft = ""
                scene_list = ch_scenes if isinstance(ch_scenes, list) else [ch_scenes]
                for single_scene in scene_list:
                    draft = await pipeline._step_draft(
                        project_id, ch, single_scene, characters, params,
                        prev_summary=prev_summary,
                    )
                    chapter_draft += draft + "\n\n"
                full_draft = chapter_draft.strip()
                store.save_draft(project_id, ch_num, full_draft)
                # 生成并保存本章摘要
                try:
                    summary = await generate_summary(full_draft, max_words=150)
                    ctx_store.save_summary(project_id, ch_num, summary)
                except Exception as e:
                    logger.warning("摘要生成失败: ch%d: %s", ch_num, e)
        elif stage == "review":
            outline = store.get_outline(project_id) or {}
            chapters = outline.get("chapters", [])
            ctx_store = get_context_store()
            from novel_factory.engine.editor import review_chapter

            # 批量参数
            start_ch = params.get("start_chapter", 1)
            batch = params.get("batch_size", len(chapters))
            target_chapters = [ch for ch in chapters if ch.get("chapter_num", 0) >= start_ch][:batch]

            for i, ch in enumerate(target_chapters):
                if task.cancel_requested:
                    await registry.transition(task.id, "cancelled")
                    return
                ch_num = ch.get("chapter_num", 0)
                await registry.update_progress(task.id, i, len(target_chapters), f"审校第 {ch_num} 章")

                draft = store.get_draft(project_id, ch_num)
                if not draft:
                    logger.info("跳过无正文章节: ch%d", ch_num)
                    continue

                # 读取上下文
                prev_summary = ctx_store.get_recent_summaries(project_id, ch_num, window=3)
                prev_reviews = ctx_store.get_recent_reviews(project_id, ch_num, window=3)
                prev_issues = []
                for r in prev_reviews:
                    prev_issues.extend(r.get("issues", []))

                characters = store.get_characters(project_id) or {}
                char_list = characters if isinstance(characters, list) else []
                foreshadows = outline.get("foreshadows", [])

                result = await review_chapter(
                    project_id, ch, draft, char_list, foreshadows,
                    prev_summary=prev_summary,
                    prev_issues=prev_issues,
                )
                ctx_store.save_chapter_review(project_id, ch_num, result)

            # 保存汇总审校报告（兼容旧格式）
            all_reviews = []
            for ch in target_chapters:
                ch_num = ch.get("chapter_num", 0)
                r = ctx_store.get_chapter_review(project_id, ch_num)
                if r:
                    all_reviews.append({"chapter": ch_num, **r})
            store.save_review(project_id, {"chapters": all_reviews, "total_chapters": len(chapters)})

        await registry.transition(task.id, "success")
        # 同步旧状态（兼容其他端点）
        _update_state(project_id, status="confirming", current_stage=stage,
                       current_stage_label=dict(STAGES).get(stage, stage),
                       needs_confirmation=True)
        logger.info("阶段 [%s] 完成: %s", stage, project_id)
    except Exception as e:
        await registry.transition(task.id, "failed", error=str(e))
        _update_state(project_id, status="failed", error=str(e))
        logger.error("阶段 [%s] 失败: %s: %s", stage, project_id, e, exc_info=True)


@app.post("/api/projects/{project_id}/pipeline/write")
async def pipeline_write(project_id: str, background_tasks: BackgroundTasks):
    """从已有大纲生成正文"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    outline = store.get_outline(project_id)
    if not outline:
        raise HTTPException(status_code=400, detail="项目没有大纲，请先运行 plan")

    state = _get_or_create_state(project_id)
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="流水线正在运行中")

    _run_in_background(_run_pipeline_background(project_id, "write", {}))
    _update_state(project_id, status="running", current_stage="scene",
                   current_stage_label="场景细纲")

    return {"message": "正文生成流水线已启动", "project_id": project_id}


@app.get("/api/projects/{project_id}/pipeline/status", response_model=PipelineStatus)
async def pipeline_status(project_id: str):
    """获取流水线状态"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    state = _get_or_create_state(project_id)
    # 生成 stages 数组
    stages = _build_stages_list(state)
    return PipelineStatus(
        project_id=state["project_id"],
        current_stage=state.get("current_stage"),
        stages=stages,
        started_at=state.get("updated_at"),
        updated_at=state.get("updated_at"),
        # 保留扁平字段
        current_stage_label=state.get("current_stage_label"),
        progress_percent=state.get("progress_percent", 0),
        total_stages=state.get("total_stages", len(STAGES)),
        completed_stages=state.get("completed_stages", 0),
        needs_confirmation=state.get("needs_confirmation", False),
        status=state.get("status", "idle"),
        error=state.get("error"),
    )


def _build_stages_list(state: dict) -> list[dict]:
    """从扁平状态生成前端需要的 stages 数组"""
    completed = state.get("completed_stages", 0)
    current = state.get("current_stage")
    pipeline_status = state.get("status", "idle")
    stages = []
    for i, (stage_key, stage_label) in enumerate(STAGES):
        if i < completed:
            s = "completed"
        elif stage_key == current and pipeline_status == "running":
            s = "running"
        elif stage_key == current and pipeline_status == "confirming":
            s = "waiting_confirm"
        elif stage_key == current and pipeline_status == "failed":
            s = "failed"
        else:
            s = "pending"
        stages.append({
            "stage": stage_key,
            "status": s,
            "progress": 100.0 if s == "completed" else (50.0 if s == "running" else 0.0),
            "error": state.get("error") if s == "failed" else None,
        })
    return stages




@app.post("/api/projects/{project_id}/pipeline/confirm")
async def pipeline_confirm(project_id: str, body: ConfirmRequest):
    """确认当前阶段结果

    action:
      - adopt: 采用当前结果，进入下一阶段
      - edit: 编辑当前结果（需提供 edits）
      - regenerate: 重新生成当前阶段
    """
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    state = _get_or_create_state(project_id)
    # 前端传了 stage 就用，没传且状态不是 confirming，重置到 topic
    if body.stage:
        _update_state(project_id, status="confirming", current_stage=body.stage,
                      current_stage_label=dict(STAGES).get(body.stage, body.stage),
                      needs_confirmation=True)
        state = _get_or_create_state(project_id)
    elif state["status"] != "confirming":
        # 状态丢失，重置到 topic
        _update_state(project_id, status="confirming", current_stage="topic",
                      current_stage_label=dict(STAGES).get("topic", "选题评估"),
                      needs_confirmation=True, completed_stages=0)
        state = _get_or_create_state(project_id)

    current_stage = state.get("current_stage")

    # 兼容前端 approve -> adopt
    action = body.action
    if action == "approve":
        action = "adopt"

    if action == "adopt":
        # 采用：标记当前阶段完成，更新状态
        stage_idx = next(
            (i for i, (k, _) in enumerate(STAGES) if k == current_stage), 0
        )
        _update_state(
            project_id,
            needs_confirmation=False,
            status="idle",
            completed_stages=stage_idx + 1,
        )
        return {"message": f"已采用 {current_stage} 阶段结果", "next_stage": STAGES[stage_idx + 1][0] if stage_idx + 1 < len(STAGES) else None}

    elif action == "edit":
        # 编辑反馈：设为 idle，由前端触发 runStage(feedback) 来重新生成
        if not body.edits:
            raise HTTPException(status_code=400, detail="edit 操作需要提供 edits 内容")
        _update_state(project_id, needs_confirmation=False, status="idle")
        return {"message": f"已提交反馈，即将重新生成 {current_stage} 阶段", "stage": current_stage, "feedback": body.edits}

    elif action == "regenerate":
        # 重新生成：设为 idle，由前端触发 runStage 来真正执行
        _update_state(project_id, needs_confirmation=False, status="idle")
        return {"message": f"已请求重新生成 {current_stage} 阶段", "stage": current_stage}

    else:
        raise HTTPException(status_code=400, detail=f"未知操作: {body.action}，可选: adopt/edit/regenerate/approve")


@app.get("/api/projects/{project_id}/pipeline/stages")
async def get_pipeline_stages(project_id: str):
    """获取所有阶段状态列表"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    state = _get_or_create_state(project_id)
    stages = _build_stages_list(state)
    return {"project_id": project_id, "stages": stages}


@app.post("/api/projects/{project_id}/pipeline/stages/{stage}/confirm")
async def confirm_pipeline_stage(project_id: str, stage: str):
    """确认指定阶段（简化接口）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    _update_state(project_id, needs_confirmation=False, status="running")
    return {"message": f"阶段 {stage} 已确认", "stage": stage}


def _save_stage_edits(store, project_id: str, stage: str, edits: dict[str, Any]) -> None:
    """将用户编辑保存到对应阶段的数据文件"""
    if stage == "topic":
        store.save_topic(project_id, edits)
    elif stage == "world":
        store.save_world(project_id, edits)
    elif stage == "character":
        store.save_characters(project_id, edits)
    elif stage == "outline":
        store.save_outline(project_id, edits)
    elif stage == "scene":
        # 场景编辑需要指定 chapter_num
        ch_num = edits.get("chapter_num", 1)
        store.save_scene(project_id, ch_num, edits)
    elif stage == "draft":
        ch_num = edits.get("chapter_num", 1)
        content = edits.get("content", "")
        store.save_draft(project_id, ch_num, content)
    elif stage == "review":
        store.save_review(project_id, edits)


# ── 数据查询 ────────────────────────────────────────────────

@app.get("/api/projects/{project_id}/topic", response_model=TopicResponse)
async def get_topic(project_id: str):
    """获取选题方案（返回列表）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    topic = store.get_topic(project_id)
    # 兼容旧数据：单个 dict 包装为列表
    if isinstance(topic, dict):
        topic = [topic]
    return TopicResponse(project_id=project_id, topic=topic or [])


@app.get("/api/projects/{project_id}/world", response_model=WorldSettingResponse)
async def get_world(project_id: str):
    """获取世界观设定"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    world = store.get_world(project_id)
    # 兼容前端：将 [{category, content}] 转为 {era, geography, ...}
    if isinstance(world, list):
        world = _normalize_world(world)
    return WorldSettingResponse(project_id=project_id, world=world or {})


def _normalize_world(world_list: list) -> dict:
    """将后端 [{category, content}] 格式转为前端期望的扁平对象"""
    category_map = {
        "时代背景": "era",
        "地理环境": "geography",
        "核心规则": "power_system",
        "力量体系": "power_system",
        "势力分布": "geography",
        "社会体系": "social_structure",
        "社会结构": "social_structure",
    }
    result = {v: "" for v in category_map.values()}
    result["key_locations"] = []
    result["rules"] = []
    result["constraints"] = []
    for item in world_list:
        category = str(item.get("category", ""))
        content = str(item.get("content", ""))
        key = category_map.get(category)
        if key:
            result[key] = content
        if "地点" in category or "势力" in category:
            result["key_locations"].append(content)
        if "规则" in category or "体系" in category:
            result["rules"].append(content)
        if "约束" in category or "限制" in category or "禁忌" in category:
            result["constraints"].append(content)
    if not result["constraints"] and result.get("social_structure"):
        result["constraints"].append(result["social_structure"])
    return result


@app.get("/api/projects/{project_id}/characters", response_model=CharacterResponse)
async def get_characters(project_id: str):
    """获取角色列表"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    characters = store.get_characters(project_id)
    if isinstance(characters, list):
        characters = [_normalize_character(c, i) for i, c in enumerate(characters)]
    return CharacterResponse(project_id=project_id, characters=characters or {})


def _normalize_character(char: dict, index: int) -> dict:
    """将后端角色格式转为前端期望的格式"""
    return {
        "id": char.get("id", f"char_{index}"),
        "name": char.get("name", ""),
        "role": char.get("role", "supporting"),
        "personality": char.get("personality", ""),
        "appearance": char.get("appearance", ""),
        "background": char.get("core_desire", char.get("background", "")),
        "arc": char.get("arc_description", char.get("arc", "")),
        "traits": char.get("traits", []),
        "relationships": char.get("relationships", []),
    }


@app.get("/api/projects/{project_id}/outline", response_model=OutlineResponse)
async def get_outline(project_id: str):
    """获取大纲"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    outline = store.get_outline(project_id)
    if outline:
        outline = _normalize_outline(outline)
    return OutlineResponse(project_id=project_id, outline=outline or {})


@app.post("/api/projects/{project_id}/outline/generate")
async def generate_outline_batch(project_id: str, body: dict):
    """分批生成大纲（通过 TaskRegistry 管理）"""
    store = get_store()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    batch_size = body.get("batch_size", 10)
    if batch_size < 1 or batch_size > 100:
        raise HTTPException(status_code=400, detail="batch_size 必须在 1-100 之间")

    existing_outline = store.get_outline(project_id) or {}
    existing_chapters = existing_outline.get("chapters", [])
    existing_foreshadows = existing_outline.get("foreshadows", [])
    start_chapter = len(existing_chapters) + 1

    chapter_word_count = project.get("chapter_word_count", 3000)
    target_words = project.get("target_words", 8000)
    total_chapters = project.get("target_chapters") or max(3, target_words // chapter_word_count)

    if start_chapter > total_chapters:
        raise HTTPException(status_code=400, detail=f"大纲已全部生成（共 {total_chapters} 章）")

    actual_batch = min(batch_size, total_chapters - len(existing_chapters))

    context = ""
    if existing_chapters:
        context = "已生成章节摘要：\n"
        for ch in existing_chapters[-10:]:
            context += f"- 第{ch.get('chapter_num', 0)}章 {ch.get('title', '')}: {ch.get('core_event', '')}\n"

    params = {
        "inspiration": project.get("inspiration") or project.get("premise", ""),
        "genre_hint": project.get("genre") or project.get("genre_major"),
        "genre_major": project.get("genre_major") or project.get("genre"),
        "target_words": target_words,
        "chapter_word_count": chapter_word_count,
        "target_audience": project.get("target_audience", "male"),
        "start_chapter": start_chapter,
        "batch_size": actual_batch,
        "total_chapters": total_chapters,
        "existing_chapters_context": context,
        "existing_foreshadows": existing_foreshadows,
    }

    try:
        task, is_new = await registry.submit(project_id, "outline", params)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if not is_new:
        return task.to_dict()

    await registry.transition(task.id, "running")
    _run_in_background(_execute_outline_task(task))

    return {
        "task_id": task.id,
        "message": f"开始生成第 {start_chapter}-{start_chapter + actual_batch - 1} 章大纲",
        "start_chapter": start_chapter,
        "batch_size": actual_batch,
        "total_chapters": total_chapters,
    }


async def _execute_outline_task(task) -> None:
    """后台执行大纲生成任务"""
    project_id = task.project_id
    params = task.params
    try:
        pipeline = get_pipeline()
        store = get_store()

        topic = _selected_topic(store.get_topic(project_id))
        world = store.get_world(project_id) or {}
        characters = store.get_characters(project_id) or {}
        char_list = characters if isinstance(characters, list) else []
        world_context = world if isinstance(world, (dict, list)) else {}

        start_chapter = params["start_chapter"]
        batch_size = params["batch_size"]

        from novel_factory.engine.outliner import generate_outline_batch
        new_chapters, new_foreshadows = await generate_outline_batch(
            project_id, topic, world_context, char_list,
            start_chapter, batch_size, params
        )

        existing_outline = store.get_outline(project_id) or {}
        existing_chapters = existing_outline.get("chapters", [])
        existing_foreshadows = existing_outline.get("foreshadows", [])
        existing_chapters.extend(new_chapters)
        existing_foreshadows.extend(new_foreshadows)

        store.save_outline(project_id, {
            "chapters": existing_chapters,
            "foreshadows": existing_foreshadows,
            "total_chapters": params.get("total_chapters", len(existing_chapters)),
        })

        await registry.transition(task.id, "success")
        _update_state(project_id, status="confirming", current_stage="outline",
                       current_stage_label="大纲生成", needs_confirmation=True)
        logger.info("大纲批次完成: %s, 第 %d-%d 章", project_id, start_chapter, start_chapter + len(new_chapters) - 1)
    except Exception as e:
        await registry.transition(task.id, "failed", error=str(e))
        logger.error("大纲批次失败: %s: %s", project_id, e, exc_info=True)
        _update_state(project_id, status="idle", current_stage="outline",
                       current_stage_label="大纲生成")


def _normalize_outline(outline: dict) -> dict:
    """将后端大纲格式转为前端期望的格式"""
    chapters = outline.get("chapters", [])
    normalized = []
    for ch in chapters:
        normalized.append({
            "chapter_number": ch.get("chapter_num", ch.get("chapter_number", 0)),
            "title": ch.get("title", ""),
            "summary": ch.get("core_event", ch.get("summary", "")),
            "key_events": ch.get("key_events", []),
            "pov_character": ch.get("pov_character", ""),
            "word_count_target": ch.get("word_count_target", 2500),
        })
    return {
        "total_chapters": outline.get("total_chapters", len(normalized)),
        "chapters": normalized,
        "foreshadows": outline.get("foreshadows", []),
    }


@app.get("/api/projects/{project_id}/drafts/status")
async def get_draft_status(project_id: str):
    """获取各章正文状态（用于前端批量 UI）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    outline = store.get_outline(project_id) or {}
    chapters = outline.get("chapters", [])
    total_chapters = outline.get("total_chapters", len(chapters))

    result = []
    for ch in chapters:
        ch_num = ch.get("chapter_num", 0)
        has_draft = store.get_draft(project_id, ch_num) is not None
        has_scenes = store.get_scene(project_id, ch_num) is not None
        result.append({
            "chapter_num": ch_num,
            "title": ch.get("title", f"第{ch_num}章"),
            "has_draft": has_draft,
            "has_scenes": has_scenes,
        })

    generated = sum(1 for r in result if r["has_draft"])
    return {
        "project_id": project_id,
        "total_chapters": total_chapters,
        "generated_count": generated,
        "chapters": result,
    }


@app.get("/api/projects/{project_id}/scenes/{chapter_num}")
async def get_scene(project_id: str, chapter_num: int):
    """获取某章场景细纲"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    scenes = store.get_scene(project_id, chapter_num)
    return {"project_id": project_id, "chapter_num": chapter_num, "scenes": scenes or []}


@app.put("/api/projects/{project_id}/scenes/{chapter_num}")
async def update_scene(project_id: str, chapter_num: int, body: dict):
    """更新某章场景细纲"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    store.save_scene(project_id, chapter_num, body)
    return {"message": "场景已保存", "project_id": project_id, "chapter_num": chapter_num}


@app.get("/api/projects/{project_id}/chapters/{chapter_num}", response_model=ChapterResponse)
async def get_chapter(project_id: str, chapter_num: int):
    """获取章节（场景细纲 + 正文）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    scenes = store.get_scene(project_id, chapter_num)
    draft = store.get_draft(project_id, chapter_num)

    if scenes is None and draft is None:
        raise HTTPException(status_code=404, detail=f"第 {chapter_num} 章尚未生成")

    # 从大纲中获取章节标题
    outline = store.get_outline(project_id) or {}
    chapters = outline.get("chapters", [])
    title = None
    for ch in chapters:
        if ch.get("chapter_num", ch.get("chapter_number")) == chapter_num:
            title = ch.get("title")
            break

    return ChapterResponse(
        project_id=project_id,
        chapter_num=chapter_num,
        title=title,
        scenes=scenes,
        draft=draft,
    )


@app.get("/api/projects/{project_id}/review/{chapter_num}")
async def get_chapter_review(project_id: str, chapter_num: int):
    """获取某章审校结果"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    ctx_store = get_context_store()
    review = ctx_store.get_chapter_review(project_id, chapter_num)
    return {"project_id": project_id, "chapter_num": chapter_num, "review": review}


@app.get("/api/projects/{project_id}/review", response_model=ReviewResponse)
async def get_review(project_id: str):
    """获取审校报告"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    review = store.get_review(project_id)
    if review:
        review = _normalize_review(review)
    return ReviewResponse(project_id=project_id, review=review or {})


def _normalize_review(review: dict) -> dict:
    """将后端审校格式转为前端期望的格式"""
    quality = review.get("quality", {})
    dims = quality.get("dimensions", {})

    # 映射维度分数 (1-10 -> 0-100)
    def dim_score(key: str) -> int:
        d = dims.get(key, {})
        return round(d.get("score", 0) * 10) if isinstance(d, dict) else 0

    overall = quality.get("overall_score", review.get("score", 0))
    if isinstance(overall, (int, float)) and overall <= 10:
        overall = round(overall * 10)

    # 映射 issues
    issues = []
    for issue in review.get("issues", []):
        severity = issue.get("severity", "warning")
        if severity == "error":
            severity = "critical"
        issues.append({
            "chapter_number": 0,
            "severity": severity,
            "category": issue.get("type", ""),
            "description": issue.get("detail", ""),
            "suggestion": "",
        })

    return {
        "overall_score": overall,
        "consistency_score": dim_score("pacing"),
        "plot_score": dim_score("emotion"),
        "character_score": dim_score("dialogue"),
        "writing_score": dim_score("readability"),
        "issues": issues,
        "summary": "、".join(quality.get("highlights", [])),
        "suggestions": quality.get("improvements", []),
    }


# ── 二次编辑（PUT 路由） ─────────────────────────────────────

@app.put("/api/projects/{project_id}/topic", response_model=TopicResponse)
async def update_topic(project_id: str, body: dict):
    """更新选题数据（二次编辑），body 为单个方案，按 id 匹配更新"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    existing = store.get_topic(project_id)
    if isinstance(existing, list):
        # 按 id 替换匹配的方案
        topic_id = body.get("id", "")
        updated = False
        for i, t in enumerate(existing):
            if t.get("id") == topic_id:
                existing[i] = {**t, **body}
                updated = True
                break
        if not updated:
            existing.append(body)
        store.save_topic(project_id, existing)
    else:
        store.save_topic(project_id, body)
    _update_stage_state(project_id, "topic", "saved")
    return TopicResponse(project_id=project_id, topic=body)


@app.put("/api/projects/{project_id}/world", response_model=WorldSettingResponse)
async def update_world(project_id: str, body: dict):
    """更新世界观设定（二次编辑）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    store.save_world(project_id, body)
    _update_stage_state(project_id, "world", "saved")
    return WorldSettingResponse(project_id=project_id, world=body)


@app.put("/api/projects/{project_id}/characters", response_model=CharacterResponse)
async def update_characters(project_id: str, body: dict):
    """更新角色（支持单个或列表）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    existing = store.get_characters(project_id) or []
    incoming = body.get("characters", body) if isinstance(body, dict) else body
    if not isinstance(incoming, list):
        incoming = [incoming]

    # 按 name 匹配合并
    if isinstance(existing, list) and len(existing) > 0:
        existing_by_name = {c.get("name", ""): i for i, c in enumerate(existing)}
        for char in incoming:
            name = char.get("name", "")
            if name in existing_by_name:
                existing[existing_by_name[name]] = char
            else:
                existing.append(char)
        store.save_characters(project_id, existing)
    else:
        store.save_characters(project_id, incoming)

    _update_stage_state(project_id, "character", "saved")
    result = store.get_characters(project_id) or incoming
    return CharacterResponse(project_id=project_id, characters=result)


@app.put("/api/projects/{project_id}/outline", response_model=OutlineResponse)
async def update_outline(project_id: str, body: dict):
    """更新大纲（二次编辑，包含 chapters 和 foreshadows）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    store.save_outline(project_id, body)
    _update_stage_state(project_id, "outline", "saved")
    return OutlineResponse(project_id=project_id, outline=body)


@app.put("/api/projects/{project_id}/chapters/{chapter_num}")
async def update_chapter(project_id: str, chapter_num: int, body: dict):
    """更新章节正文（二次编辑）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    # 兼容前端 content 和后端 draft
    draft = body.get("draft") or body.get("content", "")
    store.save_draft(project_id, chapter_num, draft)
    _update_stage_state(project_id, "draft", "saved")
    return {"project_id": project_id, "chapter_num": chapter_num, "draft": draft, "content": draft}


@app.post("/api/projects/{project_id}/chapters/{chapter_num}/revise")
async def revise_chapter(project_id: str, chapter_num: int, body: dict):
    """根据审校意见修改正文"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    feedback = body.get("feedback", "")
    issues = body.get("issues", [])

    draft = store.get_draft(project_id, chapter_num)
    if not draft:
        raise HTTPException(status_code=404, detail=f"第 {chapter_num} 章正文不存在")

    outline = store.get_outline(project_id) or {}
    chapters = outline.get("chapters", [])
    chapter = next((ch for ch in chapters if ch.get("chapter_num") == chapter_num), {})
    characters = store.get_characters(project_id) or {}
    char_list = characters if isinstance(characters, list) else []

    from novel_factory.engine.writer import revise_with_feedback
    from novel_factory.engine.memory import generate_summary
    from novel_factory.db.context_store import ContextStore

    revised = await revise_with_feedback(
        project_id, chapter, draft, char_list, issues, feedback,
    )
    store.save_draft(project_id, chapter_num, revised)

    # 更新摘要
    ctx_store = ContextStore(store.data_dir)
    try:
        summary = await generate_summary(revised, max_words=150)
        ctx_store.save_summary(project_id, chapter_num, summary)
    except Exception as e:
        logger.warning("摘要生成失败: ch%d: %s", chapter_num, e)

    return {"project_id": project_id, "chapter_num": chapter_num, "status": "revised"}


# ── 阶段状态追踪 ─────────────────────────────────────────────

@app.get("/api/projects/{project_id}/stages", response_model=StagesResponse)
async def get_stages(project_id: str):
    """获取项目各阶段的状态追踪"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    states = _get_stage_states(project_id)
    return StagesResponse(**{k: v for k, v in states.items()})


@app.post("/api/projects/{project_id}/stages/{stage}/confirm")
async def confirm_stage(project_id: str, stage: str, body: StageConfirmRequest):
    """确认某个阶段已完成（采用），更新状态为 confirmed"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    if stage not in _ALL_STAGES:
        raise HTTPException(
            status_code=400,
            detail=f"未知阶段: {stage}，可选: {', '.join(_ALL_STAGES)}"
        )
    _update_stage_state(project_id, stage, body.status)
    return {"message": f"阶段 {stage} 已确认为 {body.status}", "stage": stage, "status": body.status}


# ── 书籍元数据 ──────────────────────────────────────────────

@app.get("/api/projects/{project_id}/metadata", response_model=BookMetadata)
async def get_metadata(project_id: str):
    """获取书籍元数据"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    metadata = store.get_metadata(project_id)
    if metadata is None:
        return BookMetadata(title='', title_candidates=[], synopsis_short='', synopsis_medium='', synopsis_long='', tags=[], category='', category_path='')
    return BookMetadata(**metadata)


@app.post("/api/projects/{project_id}/metadata", response_model=BookMetadata)
async def update_metadata(project_id: str, body: dict):
    """手动更新书籍元数据"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    # 读取现有元数据并合并更新
    existing = store.get_metadata(project_id) or {}
    existing.update(body)
    store.save_metadata(project_id, existing)
    _update_stage_state(project_id, "metadata", "saved")
    return BookMetadata(**existing)


@app.put("/api/projects/{project_id}/metadata", response_model=BookMetadata)
async def replace_metadata(project_id: str, body: dict):
    """替换书籍元数据（二次编辑）"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    store.save_metadata(project_id, body)
    _update_stage_state(project_id, "metadata", "saved")
    return BookMetadata(**body)


@app.post("/api/projects/{project_id}/metadata/regenerate", response_model=BookMetadata)
async def regenerate_metadata(project_id: str):
    """重新生成书籍元数据"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")

    # 获取生成元数据所需的数据
    topic = _selected_topic(store.get_topic(project_id))
    outline = store.get_outline(project_id) or {}
    characters = store.get_characters(project_id) or {}
    params = store.get_params(project_id) or {}

    try:
        from novel_factory.engine.metadata import generate_metadata
        metadata = await generate_metadata(project_id, topic, outline, characters, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"元数据生成失败: {e}")

    store.save_metadata(project_id, metadata)
    return BookMetadata(**metadata)


# ── 系统配置 ────────────────────────────────────────────────

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """获取当前系统配置（模型、默认参数）"""
    return ConfigResponse(
        models={
            "pro": {
                "name": settings.PRO_MODEL_NAME,
                "base_url": settings.PRO_MODEL_BASE_URL,
                "has_key": bool(settings.PRO_MODEL_API_KEY),
            },
            "flash": {
                "name": settings.FLASH_MODEL_NAME,
                "base_url": settings.FLASH_MODEL_BASE_URL,
                "has_key": bool(settings.FLASH_MODEL_API_KEY),
            },
            "mimo": {
                "name": settings.MIMO_MODEL_NAME,
                "base_url": settings.MIMO_MODEL_BASE_URL,
                "has_key": bool(settings.MIMO_MODEL_API_KEY),
            },
        },
        default_provider=settings.DEFAULT_PROVIDER,
        output_dir=settings.OUTPUT_DIR,
    )


@app.put("/api/config", response_model=ConfigResponse)
async def update_config(body: ConfigUpdateRequest):
    """更新系统配置

    注意：当前仅支持内存级更新（重启后恢复默认）。
    后续可扩展为写入 .env 文件。
    """
    if body.default_provider is not None:
        if body.default_provider not in ("pro", "flash", "mimo"):
            raise HTTPException(
                status_code=400,
                detail=f"未知的模型提供者: {body.default_provider}，可选: pro/flash/mimo",
            )
        # 修改模块级单例（内存级）
        settings.DEFAULT_PROVIDER = body.default_provider

    return ConfigResponse(
        models={
            "pro": {
                "name": settings.PRO_MODEL_NAME,
                "base_url": settings.PRO_MODEL_BASE_URL,
                "has_key": bool(settings.PRO_MODEL_API_KEY),
            },
            "flash": {
                "name": settings.FLASH_MODEL_NAME,
                "base_url": settings.FLASH_MODEL_BASE_URL,
                "has_key": bool(settings.FLASH_MODEL_API_KEY),
            },
            "mimo": {
                "name": settings.MIMO_MODEL_NAME,
                "base_url": settings.MIMO_MODEL_BASE_URL,
                "has_key": bool(settings.MIMO_MODEL_API_KEY),
            },
        },
        default_provider=settings.DEFAULT_PROVIDER,
        output_dir=settings.OUTPUT_DIR,
    )


@app.get("/api/config/genres")
async def get_genres():
    """获取题材矩阵（大类→细分联动数据）

    前端用于联动选择：选中大类后动态加载对应的细分题材列表。
    """
    return {
        "matrix": GENRE_MATRIX,
        "majors": list(GENRE_MATRIX.keys()),
    }


# ── 任务查询（TaskRegistry）─────────────────────────────────


@app.get("/api/pipeline/tasks/{task_id}")
async def get_task(task_id: str):
    """查询任务状态"""
    task = registry.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return task.to_dict()


@app.post("/api/pipeline/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    task = registry.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    if task.status not in ("pending", "running"):
        return {"message": "任务已结束，无法取消", "status": task.status}
    ok = await registry.cancel(task_id)
    if ok:
        return {"message": "取消请求已标记", "task_id": task_id}
    return {"message": "取消失败"}


@app.get("/api/projects/{project_id}/pipeline/active-task")
async def get_active_task(project_id: str):
    """获取项目的当前活跃任务"""
    task = registry.get_active(project_id)
    if not task:
        return {"task_id": None, "status": "idle"}
    return task.to_dict()


# ── 灵感生成 ─────────────────────────────────────────────────

class InspirationRequest(BaseModel):
    """灵感生成请求"""
    gender: str = Field(..., description="读者频道: male/female")
    genre_name: str = Field("", description="题材名称")
    genre_desc: str = Field("", description="题材描述")
    protagonist_name: str = Field("", description="主角姓名")
    protagonist_desc: str = Field("", description="主角性格描述")
    heroine_desc: str = Field("", description="女主性格描述")
    romance_mode: str = Field("", description="感情线模式")
    story_background: str = Field("", description="故事背景")
    style_text: str = Field("", description="写作风格")
    reference_works: str = Field("", description="参考作品")
    forbidden_elements: str = Field("", description="禁忌元素")
    platform_name: str = Field("", description="目标平台")
    target_words: int = Field(120000, description="目标字数")
    direction: str = Field("", description="强调方向（重新生成时用户指定）")


class InspirationVersion(BaseModel):
    """单个灵感版本"""
    id: str
    synopsis: str
    titles: list[str]


class InspirationResponse(BaseModel):
    """灵感生成响应"""
    versions: list[InspirationVersion]


@app.post("/api/generate/inspiration", response_model=InspirationResponse)
async def generate_inspiration(body: InspirationRequest):
    """AI 生成灵感版本（2-3 个）"""
    from novel_factory.llm.gateway import complete_json

    user_parts: list[str] = []
    if body.story_background:
        user_parts.append(f"故事背景：{body.story_background}")
    if body.genre_name:
        user_parts.append(f"题材：{body.genre_name}（{body.genre_desc}）")
    if body.protagonist_name:
        user_parts.append(f"主角姓名：{body.protagonist_name}")
    if body.protagonist_desc:
        user_parts.append(f"主角性格：{body.protagonist_desc}")
    if body.heroine_desc and body.romance_mode and body.romance_mode != "none":
        user_parts.append(f"女主性格：{body.heroine_desc}")
    if body.romance_mode:
        user_parts.append(f"感情线：{body.romance_mode}")
    if body.style_text:
        user_parts.append(f"写作风格：{body.style_text}")
    if body.reference_works:
        user_parts.append(f"参考作品：{body.reference_works}")
    if body.forbidden_elements:
        user_parts.append(f"禁忌元素：{body.forbidden_elements}")
    if body.platform_name:
        user_parts.append(f"目标平台：{body.platform_name}，目标字数：{body.target_words}字")
    if body.direction:
        user_parts.append(f"强调方向：{body.direction}")

    gender_label = "男频" if body.gender == "male" else "女频"
    user_info = "\n".join(user_parts)

    system_prompt = f"""你是一位资深网文策划经理，擅长根据用户需求生成小说灵感。

根据用户提供的信息，生成 1 个灵感方案。

必须包含：
- synopsis: 200-300 字的故事梗概，包含主角身份、核心冲突、故事走向，要有具体细节
- titles: 3 个备选书名，要有网文感，能吸引读者点击

要求：
1. 故事梗概要有具体的冲突和转折点，不要泛泛而谈
2. 书名要有网文感，参考 {gender_label} 热门作品命名风格
3. 如果用户提供了故事背景，必须以此为核心，不要脱离用户描述
4. 所有内容用中文

输出 JSON 格式：
{{"versions": [{{"id": "v1", "synopsis": "...", "titles": ["书名1", "书名2", "书名3"]}}]}}"""

    logger.info("灵感生成请求: gender=%s, genre=%s, bg_len=%d", body.gender, body.genre_name, len(body.story_background))

    try:
        result = await complete_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_info},
            ],
            role="planner",
            temperature=0.85,
            max_tokens=2000,
        )

        versions = []
        for i, v in enumerate(result.get("versions", [])[:1]):
            versions.append(InspirationVersion(
                id=v.get("id", f"v{i+1}"),
                synopsis=v.get("synopsis", ""),
                titles=v.get("titles", []),
            ))

        if not versions:
            raise ValueError("AI 未返回有效灵感")

        logger.info("灵感生成成功: %d 个版本, synopsis_len=%d", len(versions), len(versions[0].synopsis))
        return InspirationResponse(versions=versions)

    except Exception as e:
        logger.error("灵感生成失败: %s", str(e), exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"灵感生成失败: {str(e)}")
