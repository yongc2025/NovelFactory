"""数据库层 -- SQLite 连接管理、Pydantic 数据模型、项目存储。"""

from novel_factory.db.connection import get_connection
from novel_factory.db.project_store import ProjectStore
from novel_factory.db.models import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    Chapter,
    ChapterCreate,
    Episode,
    EpisodeCreate,
    Foreshadow,
    ForeshadowCreate,
    PlotLine,
    Project,
    ProjectCreate,
    ProjectUpdate,
    Publication,
    PublicationCreate,
    Scene,
    SceneCreate,
    WorldSetting,
    WorldSettingCreate,
)

__all__ = [
    "get_connection",
    "ProjectStore",
    # Pydantic 模型
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "WorldSetting",
    "WorldSettingCreate",
    "Character",
    "CharacterCreate",
    "CharacterUpdate",
    "Chapter",
    "ChapterCreate",
    "Scene",
    "SceneCreate",
    "Foreshadow",
    "ForeshadowCreate",
    "PlotLine",
    "Episode",
    "EpisodeCreate",
    "Publication",
    "PublicationCreate",
]
