"""寤鸿〃 DDL 鈥?鍙傜収 docs/system-architecture.md 涓殑鏁版嵁妯″瀷銆?""

from __future__ import annotations

from novel_factory.db.connection import get_connection

DDL_PROJECTS = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT,
    genre TEXT,
    sub_genre TEXT,
    premise TEXT,
    target_platforms TEXT,
    target_words INT,
    status TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
"""

DDL_WORLD_SETTINGS = """
CREATE TABLE IF NOT EXISTS world_settings (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    category TEXT,
    title TEXT,
    content TEXT,
    sort_order INT
);
"""

DDL_CHARACTERS = """
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    name TEXT,
    aliases TEXT,
    role TEXT,
    age INT,
    appearance TEXT,
    personality_surface TEXT,
    personality_deep TEXT,
    core_desire TEXT,
    core_fear TEXT,
    voice_style TEXT,
    secret TEXT,
    arc_start TEXT,
    arc_end TEXT,
    current_state TEXT,
    relation_summary TEXT,
    sort_order INT
);
"""

DDL_PLOT_LINES = """
CREATE TABLE IF NOT EXISTS plot_lines (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    name TEXT,
    plot_type TEXT,
    status TEXT,
    summary TEXT,
    key_events TEXT
);
"""

DDL_FORESHADOWS = """
CREATE TABLE IF NOT EXISTS foreshadows (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    content TEXT,
    planted_chapter INT,
    target_chapter INT,
    status TEXT,
    callback_chapter INT
);
"""

DDL_CHAPTERS = """
CREATE TABLE IF NOT EXISTS chapters (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    chapter_num INT,
    title TEXT,
    outline TEXT,
    core_event TEXT,
    characters_present TEXT,
    emotion_position TEXT,
    emotion_arc TEXT,
    plot_lines_progress TEXT,
    hook TEXT,
    foreshadow_ops TEXT,
    status TEXT,
    word_count INT
);
"""

DDL_SCENES = """
CREATE TABLE IF NOT EXISTS scenes (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    chapter_id TEXT REFERENCES chapters(id),
    scene_num INT,
    location TEXT,
    atmosphere TEXT,
    characters_present TEXT,
    character_goals TEXT,
    conflict TEXT,
    turning_point TEXT,
    emotion_start TEXT,
    emotion_end TEXT,
    dialogue_direction TEXT,
    sensory_details TEXT,
    detailed_plan TEXT,
    draft TEXT,
    final_text TEXT,
    summary TEXT,
    word_count INT,
    status TEXT
);
"""

DDL_EPISODES = """
CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    episode_num INT,
    duration_seconds INT,
    script TEXT,
    hook_first_5s TEXT,
    cliffhanger TEXT,
    is_paid BOOLEAN,
    storyboard TEXT,
    image_prompts TEXT,
    image_urls TEXT,
    audio_url TEXT,
    video_url TEXT,
    status TEXT
);
"""

DDL_PUBLICATIONS = """
CREATE TABLE IF NOT EXISTS publications (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    platform TEXT,
    content_type TEXT,
    content_id TEXT,
    title TEXT,
    publish_time TIMESTAMP,
    status TEXT,
    metrics TEXT,
    notes TEXT
);
"""

ALL_DDL: list[str] = [
    DDL_PROJECTS,
    DDL_WORLD_SETTINGS,
    DDL_CHARACTERS,
    DDL_PLOT_LINES,
    DDL_FORESHADOWS,
    DDL_CHAPTERS,
    DDL_SCENES,
    DDL_EPISODES,
    DDL_PUBLICATIONS,
]


def init_db() -> None:
    """
    鍒濆鍖栨暟鎹簱 鈥?鎵ц鎵€鏈夊缓琛?DDL銆?

    鍙噸澶嶈皟鐢紝浣跨敤 IF NOT EXISTS 淇濊瘉骞傜瓑銆?
    """
    with get_connection() as conn:
        for ddl in ALL_DDL:
            conn.executescript(ddl)
