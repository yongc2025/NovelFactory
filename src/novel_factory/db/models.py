"""Pydantic 数据模型 -- 每个核心表对应 Create / Update / Response 变体。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Projects ──────────────────────────────────────────────────

class Project(BaseModel):
    """小说项目"""
    id: str
    title: str
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    premise: Optional[str] = None
    target_platforms: Optional[str] = None
    target_words: Optional[int] = None
    status: str = "created"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectCreate(BaseModel):
    title: str
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    premise: Optional[str] = None
    target_platforms: Optional[str] = None
    target_words: Optional[int] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    premise: Optional[str] = None
    target_platforms: Optional[str] = None
    target_words: Optional[int] = None
    status: Optional[str] = None


# ── World Settings ────────────────────────────────────────────

class WorldSetting(BaseModel):
    """世界观设定"""
    id: str
    project_id: str
    category: str  # time_period/rules/factions/economy/power_system
    title: Optional[str] = None
    content: str
    sort_order: Optional[int] = None
    created_at: Optional[datetime] = None


class WorldSettingCreate(BaseModel):
    project_id: str
    category: str
    title: Optional[str] = None
    content: str
    sort_order: Optional[int] = None


# ── Characters ────────────────────────────────────────────────

class Character(BaseModel):
    """角色卡"""
    id: str
    project_id: str
    name: str
    aliases: Optional[str] = None  # JSON: ["小名","绰号"]
    role: str  # protagonist/antagonist/supporting
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality_surface: Optional[str] = None
    personality_deep: Optional[str] = None
    core_desire: Optional[str] = None
    core_fear: Optional[str] = None
    voice_style: Optional[str] = None
    secret: Optional[str] = None
    arc_start: Optional[str] = None
    arc_end: Optional[str] = None
    current_state: Optional[str] = None
    relation_summary: Optional[str] = None
    sort_order: Optional[int] = None
    created_at: Optional[datetime] = None


class CharacterCreate(BaseModel):
    project_id: str
    name: str
    aliases: Optional[str] = None
    role: str
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality_surface: Optional[str] = None
    personality_deep: Optional[str] = None
    core_desire: Optional[str] = None
    core_fear: Optional[str] = None
    voice_style: Optional[str] = None
    secret: Optional[str] = None
    arc_start: Optional[str] = None
    arc_end: Optional[str] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    current_state: Optional[str] = None
    relation_summary: Optional[str] = None


# ── Chapters ──────────────────────────────────────────────────

class Chapter(BaseModel):
    """章节大纲"""
    id: str
    project_id: str
    chapter_num: int
    title: Optional[str] = None
    outline: Optional[str] = None
    core_event: Optional[str] = None
    characters_present: Optional[str] = None  # JSON
    emotion_position: Optional[str] = None
    emotion_arc: Optional[str] = None  # JSON
    plot_lines_progress: Optional[str] = None  # JSON
    hook: Optional[str] = None
    foreshadow_ops: Optional[str] = None  # JSON
    status: str = "outlined"
    word_count: Optional[int] = None
    created_at: Optional[datetime] = None


class ChapterCreate(BaseModel):
    project_id: str
    chapter_num: int
    title: Optional[str] = None
    outline: Optional[str] = None
    core_event: Optional[str] = None
    emotion_position: Optional[str] = None
    hook: Optional[str] = None


# ── Scenes ────────────────────────────────────────────────────

class Scene(BaseModel):
    """场景"""
    id: str
    project_id: str
    chapter_id: str
    scene_num: int
    location: Optional[str] = None
    atmosphere: Optional[str] = None
    characters_present: Optional[str] = None  # JSON
    character_goals: Optional[str] = None  # JSON
    conflict: Optional[str] = None
    turning_point: Optional[str] = None
    emotion_start: Optional[str] = None
    emotion_end: Optional[str] = None
    dialogue_direction: Optional[str] = None
    sensory_details: Optional[str] = None
    detailed_plan: Optional[str] = None
    draft: Optional[str] = None
    final_text: Optional[str] = None
    summary: Optional[str] = None
    word_count: Optional[int] = None
    status: str = "planned"
    created_at: Optional[datetime] = None


class SceneCreate(BaseModel):
    project_id: str
    chapter_id: str
    scene_num: int
    location: Optional[str] = None
    atmosphere: Optional[str] = None
    conflict: Optional[str] = None
    emotion_start: Optional[str] = None
    emotion_end: Optional[str] = None
    detailed_plan: Optional[str] = None


# ── Foreshadows ───────────────────────────────────────────────

class Foreshadow(BaseModel):
    """伏笔"""
    id: str
    project_id: str
    content: str
    planted_chapter: Optional[int] = None
    target_chapter: Optional[int] = None
    status: str = "planted"  # planted/called_back/abandoned
    callback_chapter: Optional[int] = None
    created_at: Optional[datetime] = None


class ForeshadowCreate(BaseModel):
    project_id: str
    content: str
    planted_chapter: Optional[int] = None
    target_chapter: Optional[int] = None


# ── Plot Lines ────────────────────────────────────────────────

class PlotLine(BaseModel):
    """情节线"""
    id: str
    project_id: str
    name: str
    plot_type: Optional[str] = None  # main/romance/sub1/sub2
    status: str = "active"
    summary: Optional[str] = None
    key_events: Optional[str] = None  # JSON
    created_at: Optional[datetime] = None


# ── Episodes ──────────────────────────────────────────────────

class Episode(BaseModel):
    """分集剧本"""
    id: str
    project_id: str
    episode_num: int
    duration_seconds: Optional[int] = None
    script: Optional[str] = None
    hook_first_5s: Optional[str] = None
    cliffhanger: Optional[str] = None
    is_paid: bool = False
    storyboard: Optional[str] = None  # JSON
    image_prompts: Optional[str] = None  # JSON
    image_urls: Optional[str] = None  # JSON
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    status: str = "scripted"
    created_at: Optional[datetime] = None


class EpisodeCreate(BaseModel):
    project_id: str
    episode_num: int
    script: Optional[str] = None
    hook_first_5s: Optional[str] = None
    cliffhanger: Optional[str] = None


# ── Publications ──────────────────────────────────────────────

class Publication(BaseModel):
    """发布记录"""
    id: str
    project_id: str
    platform: str  # xiaohongshu/fanqie/douyin/kuaishou/zhihu/gongzhonghao
    content_type: str  # note/chapter/episode/script
    content_id: Optional[str] = None
    title: Optional[str] = None
    publish_time: Optional[datetime] = None
    status: str = "draft"
    metrics: Optional[str] = None  # JSON
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class PublicationCreate(BaseModel):
    project_id: str
    platform: str
    content_type: str
    title: Optional[str] = None
