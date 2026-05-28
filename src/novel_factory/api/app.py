"""FastAPI 应用 — NovelFactory API 服务

路由概览：
  - 项目管理: /api/projects/*
  - 流水线控制: /api/projects/{id}/pipeline/*
  - 数据查询: /api/projects/{id}/topic|world|characters|outline|chapters|review
  - 系统配置: /api/config/*
"""

from __future__ import annotations

import asyncio
import traceback
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from novel_factory.api.deps import get_pipeline, get_store
from novel_factory.api.schemas import (
    GENRE_MATRIX,
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
    ("scene", "场景细纲"),
    ("draft", "正文生成"),
    ("review", "编辑审校"),
]

# ── 流水线状态内存存储（进程内） ────────────────────────────

# project_id -> PipelineStatus 数据
_pipeline_states: dict[str, dict[str, Any]] = {}


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
                    result = await pipeline._step_topic(project_id, inspiration, genre_hint)
                elif stage_key == "world":
                    topic = store.get_topic(project_id) or {}
                    result = await pipeline._step_world(project_id, topic)
                elif stage_key == "character":
                    topic = store.get_topic(project_id) or {}
                    world = store.get_world(project_id) or {}
                    result = await pipeline._step_character(project_id, topic, world)
                elif stage_key == "outline":
                    topic = store.get_topic(project_id) or {}
                    world = store.get_world(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    target_chapters = params.get("target_chapters", max(3, target_words // 800))
                    result = await pipeline._step_outline(
                        project_id, topic, world, characters, target_chapters
                    )
                elif stage_key == "scene":
                    outline = store.get_outline(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    chapters = outline.get("chapters", [])
                    for ch in chapters:
                        ch_num = ch.get("chapter_num", 0)
                        scenes = await pipeline._step_scene(project_id, ch, characters)
                        store.save_scene(project_id, ch_num, scenes)
                elif stage_key == "draft":
                    outline = store.get_outline(project_id) or {}
                    characters = store.get_characters(project_id) or {}
                    chapters = outline.get("chapters", [])
                    for ch in chapters:
                        ch_num = ch.get("chapter_num", 0)
                        ch_scenes = store.get_scene(project_id, ch_num) or []
                        chapter_draft = ""
                        scene_list = ch_scenes if isinstance(ch_scenes, list) else [ch_scenes]
                        for single_scene in scene_list:
                            draft = await pipeline._step_draft(
                                project_id, ch, single_scene, characters
                            )
                            chapter_draft += draft + "\n\n"
                        store.save_draft(project_id, ch_num, chapter_draft.strip())
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
                    result = await pipeline._step_topic(project_id, inspiration, genre_hint)
                elif stage_key == "world":
                    topic = store.get_topic(project_id) or {}
                    result = await pipeline._step_world(project_id, topic)
                elif stage_key == "character":
                    topic = store.get_topic(project_id) or {}
                    world = store.get_world(project_id) or {}
                    result = await pipeline._step_character(project_id, topic, world)
                elif stage_key == "outline":
                    topic = store.get_topic(project_id) or {}
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
        "target_words": project.get("target_words", 8000),
        "target_chapters": project.get("target_chapters"),
    }

    background_tasks.add_task(_run_pipeline_background, project_id, "full", params)
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

    params = {
        "inspiration": project.get("inspiration") or project.get("premise", ""),
        "genre_hint": project.get("genre") or project.get("genre_major"),
        "target_chapters": project.get("target_chapters", 10),
    }

    background_tasks.add_task(_run_pipeline_background, project_id, "plan", params)
    _update_state(project_id, status="running", current_stage=STAGES[0][0],
                   current_stage_label=STAGES[0][1])

    return {"message": "大纲规划流水线已启动", "project_id": project_id}


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

    background_tasks.add_task(
        _run_pipeline_background, project_id, "write", {}
    )
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
    return PipelineStatus(**state)


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
    if state["status"] != "confirming":
        raise HTTPException(status_code=400, detail="当前没有待确认的阶段")

    current_stage = state.get("current_stage")

    if body.action == "adopt":
        # 采用：标记当前阶段完成，更新状态
        stage_idx = next(
            (i for i, (k, _) in enumerate(STAGES) if k == current_stage), 0
        )
        _update_state(
            project_id,
            needs_confirmation=False,
            status="running",
            completed_stages=stage_idx + 1,
        )
        return {"message": f"已采用 {current_stage} 阶段结果", "next_stage": STAGES[stage_idx + 1][0] if stage_idx + 1 < len(STAGES) else None}

    elif body.action == "edit":
        # 编辑：将用户编辑的内容保存到对应阶段
        if not body.edits:
            raise HTTPException(status_code=400, detail="edit 操作需要提供 edits 内容")
        _save_stage_edits(store, project_id, current_stage, body.edits)
        _update_state(project_id, needs_confirmation=False, status="running")
        return {"message": f"已保存 {current_stage} 阶段编辑内容"}

    elif body.action == "regenerate":
        # 重新生成：标记状态，后续由前端触发重新运行该阶段
        _update_state(project_id, needs_confirmation=False, status="running")
        return {"message": f"已请求重新生成 {current_stage} 阶段", "stage": current_stage}

    else:
        raise HTTPException(status_code=400, detail=f"未知操作: {body.action}，可选: adopt/edit/regenerate")


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
    """获取选题方案"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    topic = store.get_topic(project_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="选题方案尚未生成")
    return TopicResponse(project_id=project_id, topic=topic)


@app.get("/api/projects/{project_id}/world", response_model=WorldSettingResponse)
async def get_world(project_id: str):
    """获取世界观设定"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    world = store.get_world(project_id)
    if world is None:
        raise HTTPException(status_code=404, detail="世界观尚未生成")
    return WorldSettingResponse(project_id=project_id, world=world)


@app.get("/api/projects/{project_id}/characters", response_model=CharacterResponse)
async def get_characters(project_id: str):
    """获取角色列表"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    characters = store.get_characters(project_id)
    if characters is None:
        raise HTTPException(status_code=404, detail="角色设计尚未生成")
    return CharacterResponse(project_id=project_id, characters=characters)


@app.get("/api/projects/{project_id}/outline", response_model=OutlineResponse)
async def get_outline(project_id: str):
    """获取大纲"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    outline = store.get_outline(project_id)
    if outline is None:
        raise HTTPException(status_code=404, detail="大纲尚未生成")
    return OutlineResponse(project_id=project_id, outline=outline)


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
        if ch.get("chapter_num") == chapter_num:
            title = ch.get("title")
            break

    return ChapterResponse(
        project_id=project_id,
        chapter_num=chapter_num,
        title=title,
        scenes=scenes,
        draft=draft,
    )


@app.get("/api/projects/{project_id}/review", response_model=ReviewResponse)
async def get_review(project_id: str):
    """获取审校报告"""
    store = get_store()
    if not store.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    review = store.get_review(project_id)
    if review is None:
        raise HTTPException(status_code=404, detail="审校报告尚未生成")
    return ReviewResponse(project_id=project_id, review=review)


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
