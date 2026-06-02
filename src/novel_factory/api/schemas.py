"""请求/响应 Pydantic 模型

基于 docs/phase2-project-creation.md 中的参数分层设计。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── 题材矩阵 ────────────────────────────────────────────────

GENRE_MATRIX: dict[str, list[str]] = {
    "古言": ["重生复仇", "宅斗权谋", "甜宠宫斗", "穿书逆袭", "种田经商", "古言仙侠"],
    "现代": ["总裁豪门", "娱乐圈", "职场逆袭", "都市情感", "悬疑推理", "医疗/法律"],
    "玄幻": ["系统流", "重生修仙", "异世大陆", "灵异悬疑", "末日生存", "魔法工业", "理工科穿越", "种田基建"],
    "科幻": ["星际", "赛博朋克", "时间循环", "末日废土", "硬科幻", "科技种田"],
    "年代": ["70-80年代", "90年代经商", "年代重生"],
    "都市": ["校园", "职场", "家庭伦理", "情感婚姻", "学霸/科研"],
    "男频": ["玄幻修仙", "都市异能", "游戏竞技", "科幻机甲", "历史架空", "末日求生"],
    "其他": ["自定义"],
}

# 篇幅→默认参数映射
LENGTH_DEFAULTS: dict[str, dict[str, Any]] = {
    "short": {
        "target_words": 5000,
        "target_chapters": 3,
        "chapter_word_range": [1500, 2000],
        "climax_density": "high",
        "foreshadow_count": 2,
        "platforms_default": ["xiaohongshu"],
    },
    "medium": {
        "target_words": 50000,
        "target_chapters": 20,
        "chapter_word_range": [2000, 3000],
        "climax_density": "medium",
        "foreshadow_count": 5,
        "platforms_default": ["fanqie"],
    },
    "long": {
        "target_words": 200000,
        "target_chapters": 80,
        "chapter_word_range": [2500, 4000],
        "climax_density": "medium",
        "foreshadow_count": 10,
        "platforms_default": ["fanqie"],
    },
    "comic": {
        "target_words": 80000,
        "target_chapters": 80,
        "chapter_word_range": [2000, 3000],
        "climax_density": "high",
        "foreshadow_count": 5,
        "platforms_default": ["comic_drama"],
    },
}


# ── 请求模型 ────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """创建项目请求 — 5 级参数，Level 1 必填，其余可选"""

    # Level 1: 必填
    premise: str = Field(..., min_length=10, max_length=500, description="灵感/前提，50-200字核心冲突")
    platforms: list[str] = Field(..., min_length=1, description="目标平台: xiaohongshu/fanqie/comic_drama/short_drama")
    length_type: str = Field(..., description="篇幅: short/medium/long/comic")

    # Level 2: 题材定位（选填）
    genre_major: str | None = Field(None, description="大类: 古言/现代/玄幻/科幻/都市/年代/仙侠/末日")
    genre_minor: str | None = Field(None, description="细分题材，根据大类动态变化")
    target_audience: str = Field("female", description="目标读者: female/male/general")
    tone: str | None = Field(None, description="内容基调: 爽文/虐文/甜文/悬疑/热血/治愈")

    # 书籍元数据（可选，AI可生成）
    book_title: str | None = Field(None, max_length=30, description="书名，留空则AI生成")
    book_synopsis: str | None = Field(None, max_length=500, description="简介，留空则AI生成")
    book_tags: list[str] = Field(default_factory=list, description="标签，留空则AI推荐")
    book_category: str | None = Field(None, description="分类，留空则AI匹配")

    # Level 3: 角色预设（选填）
    protagonist_name: str | None = Field(None, description="主角名，留空则 AI 命名")
    protagonist_desc: str | None = Field(None, description="主角人设，一句话描述")
    antagonist_name: str | None = Field(None, description="反派名")
    antagonist_desc: str | None = Field(None, description="反派人设")
    has_romance: str = Field("flexible", description="CP线: yes/no/flexible")
    romance_desc: str | None = Field(None, description="CP设定，如'先婚后爱'")
    supporting_count: int = Field(3, ge=1, le=10, description="配角数量")

    # Level 4: 世界观约束（选填）
    world_setting: str | None = Field(None, description="时空背景")
    world_custom: str | None = Field(None, description="自定义世界观（world_setting=自定义时启用）")
    reference_works: str | None = Field(None, description="参考作品")
    forbidden_elements: list[str] = Field(default_factory=list, description="禁忌元素")

    # Level 5: 生成策略（高级，全部有默认值）
    target_words: int | None = Field(None, description="目标字数，根据 length_type 自动推算")
    target_chapters: int | None = Field(None, description="目标章节数")
    chapter_word_range: list[int] = Field([2000, 3000], description="每章字数范围")
    climax_density: str = Field("medium", description="爽点密度: high/medium/low")
    climax_interval: int = Field(3, ge=1, description="每几章一个小爽点")
    foreshadow_count: int = Field(5, ge=0, description="伏笔数量")
    model_provider: str = Field("flash", description="AI模型: flash/pro/mimo")
    style_sample: str | None = Field(None, description="风格样本（范文）")

    def resolve_defaults(self) -> dict[str, Any]:
        """根据 length_type 解析默认值，返回完整参数字典"""
        defaults = LENGTH_DEFAULTS.get(self.length_type, LENGTH_DEFAULTS["medium"])
        data = self.model_dump()
        # 自动填充未指定的数值字段
        if data["target_words"] is None:
            data["target_words"] = defaults["target_words"]
        if data["target_chapters"] is None:
            data["target_chapters"] = defaults["target_chapters"]
        # 确保 chapter_word_range 至少有 2 个元素
        if len(data["chapter_word_range"]) < 2:
            data["chapter_word_range"] = defaults["chapter_word_range"]
        return data


# ── 响应模型 ────────────────────────────────────────────────

class ProjectResponse(BaseModel):
    """项目详情响应"""
    id: str
    title: str
    inspiration: str
    genre: str | None = None
    target_words: int = 8000
    status: str = "created"
    created_at: str | None = None
    updated_at: str | None = None
    # 扩展参数（来自 ProjectCreate）
    premise: str | None = None
    platforms: list[str] | None = None
    length_type: str | None = None
    genre_major: str | None = None
    genre_minor: str | None = None
    target_audience: str | None = None
    tone: str | None = None
    protagonist_name: str | None = None
    protagonist_desc: str | None = None
    antagonist_name: str | None = None
    antagonist_desc: str | None = None
    has_romance: str | None = None
    romance_desc: str | None = None
    supporting_count: int | None = None
    world_setting: str | None = None
    world_custom: str | None = None
    reference_works: str | None = None
    forbidden_elements: list[str] | None = None
    target_chapters: int | None = None
    chapter_word_range: list[int] | None = None
    climax_density: str | None = None
    climax_interval: int | None = None
    foreshadow_count: int | None = None
    model_provider: str | None = None


class ProjectListItem(BaseModel):
    """项目列表项"""
    id: str
    title: str
    genre: str | None = None
    status: str = "created"
    created_at: str | None = None


class StageStatus(BaseModel):
    """单个阶段状态"""
    stage: str
    status: str = "pending"  # pending/running/completed/failed/waiting_confirm
    progress: float = 0.0
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None


class PipelineStatus(BaseModel):
    """流水线状态"""
    project_id: str
    current_stage: str | None = None
    stages: list[StageStatus] = []
    started_at: str | None = None
    updated_at: str | None = None

    # 保留后端内部使用的扁平字段（可选）
    current_stage_label: str | None = None
    progress_percent: float = 0.0
    total_stages: int = 7
    completed_stages: int = 0
    needs_confirmation: bool = False
    status: str = "idle"
    error: str | None = None


class ChapterResponse(BaseModel):
    """章节响应（场景 + 正文）"""
    project_id: str
    chapter_num: int
    chapter_number: int | None = None  # 前端别名
    title: str | None = None
    scenes: dict[str, Any] | list[dict[str, Any]] | None = None
    draft: str | None = None
    content: str | None = None  # 前端别名
    word_count: int = 0
    status: str = "draft"

    def model_post_init(self, __context) -> None:
        # 兼容前端字段名
        if self.chapter_number is None:
            self.chapter_number = self.chapter_num
        if self.content is None:
            self.content = self.draft or ""
        if self.word_count == 0:
            self.word_count = len(self.content.replace("\s", "")) if self.content else 0


class CharacterResponse(BaseModel):
    """单角色详情"""
    id: str
    name: str
    role: str
    personality: str | None = None
    appearance: str | None = None
    background: str | None = None  # 兼容旧字段
    core_desire: str | None = None
    core_fear: str | None = None
    fatal_flaw: str | None = None
    wound: str | None = None
    speaking_style: str | None = None
    arc: str | None = None
    arc_description: str | None = None
    traits: list[str] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)


class CharacterListResponse(BaseModel):
    """角色列表响应"""
    project_id: str
    characters: list[CharacterResponse]


class ReviewResponse(BaseModel):
    """审校报告响应"""
    project_id: str
    review: dict[str, Any] | list[dict[str, Any]]


class WorldSettingResponse(BaseModel):
    """世界观响应"""
    project_id: str
    world: dict[str, Any] | list[dict[str, Any]]


class TopicResponse(BaseModel):
    """选题方案响应"""
    project_id: str
    topic: dict[str, Any] | list[dict[str, Any]]


class BookMetadata(BaseModel):
    """书籍元数据响应"""
    title: str = ""
    title_candidates: list[str] = []  # 5个候选书名
    synopsis_short: str = ""   # 50字简介
    synopsis_medium: str = ""  # 150字简介
    synopsis_long: str = ""    # 300字简介
    tags: list[str] = []
    category: str = ""
    category_path: str = ""  # 如 "男频 > 玄幻 > 异世大陆"


class OutlineResponse(BaseModel):
    """大纲响应"""
    project_id: str
    outline: dict[str, Any] | list[dict[str, Any]]


class ConfirmRequest(BaseModel):
    """确认/编辑/重新生成请求"""
    action: str = Field(..., description="操作: adopt/edit/regenerate/approve")
    edits: dict[str, Any] | None = Field(None, description="编辑内容（action=edit 时使用）")
    stage: str | None = Field(None, description="指定阶段（可选，避免后端推断错误）")


class ConfigResponse(BaseModel):
    """系统配置响应"""
    models: dict[str, Any]                 # 各模型配置
    default_provider: str                  # 默认模型
    output_dir: str                        # 输出目录


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    default_provider: str | None = None
    # 可扩展其他配置项


# ── 阶段状态追踪 ─────────────────────────────────────────────

class StageInfo(BaseModel):
    """单个阶段的状态信息"""
    status: str = Field("pending", description="阶段状态: pending/generated/editing/saved/confirmed")
    updated_at: str | None = Field(None, description="最后更新时间")


class StagesResponse(BaseModel):
    """阶段状态追踪响应"""
    topic: StageInfo = Field(default_factory=StageInfo)
    world: StageInfo = Field(default_factory=StageInfo)
    character: StageInfo = Field(default_factory=StageInfo)
    outline: StageInfo = Field(default_factory=StageInfo)
    metadata: StageInfo = Field(default_factory=StageInfo)
    scene: StageInfo = Field(default_factory=StageInfo)
    draft: StageInfo = Field(default_factory=StageInfo)
    review: StageInfo = Field(default_factory=StageInfo)


class StageConfirmRequest(BaseModel):
    """阶段确认请求"""
    status: str = Field("confirmed", description="确认后的状态，默认 confirmed")
