"""项目存储：JSON 索引 + 文件系统结构

目录结构:
    data/
    ├── projects.json          # 项目索引
    └── <project_id>/
        ├── project.json       # 项目元数据 + 选题结果
        ├── world.json         # 世界观设定
        ├── characters.json    # 角色设计
        ├── outline.json       # 章节大纲
        ├── scenes/
        │   └── ch<NN>.json    # 每章场景细纲
        ├── drafts/
        │   └── ch<NN>.md      # 每章初稿
        └── review.json        # 审校报告
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


def _get_data_dir() -> Path:
    """获取数据目录（项目根目录下的 data/）"""
    # 从当前文件向上找项目根目录
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data"
    # fallback: 当前工作目录
    return Path.cwd() / "data"


def _get_output_dir() -> Path:
    """获取输出目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "output"
    return Path.cwd() / "output"


class ProjectStore:
    """项目存储管理器"""

    def __init__(self):
        self.data_dir = _get_data_dir()
        self.output_dir = _get_output_dir()
        self.index_path = self.data_dir / "projects.json"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保必要目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._save_index({})

    def _load_index(self) -> dict[str, Any]:
        """加载项目索引"""
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_index(self, index: dict[str, Any]):
        """保存项目索引"""
        self.index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def generate_project_id(self) -> str:
        """生成项目 ID（短格式：时间戳 + 随机后缀）"""
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = uuid.uuid4().hex[:6]
        return f"{now}_{short_id}"

    def create_project(self, title: str, inspiration: str, genre: str = None,
                       target_words: int = 8000) -> str:
        """创建新项目，返回 project_id"""
        project_id = self.generate_project_id()
        project_dir = self.data_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "scenes").mkdir(exist_ok=True)
        (project_dir / "drafts").mkdir(exist_ok=True)

        # 项目元数据
        meta = {
            "id": project_id,
            "title": title,
            "inspiration": inspiration,
            "genre": genre,
            "target_words": target_words,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._write_json(project_dir / "project.json", meta)

        # 更新索引
        index = self._load_index()
        index[project_id] = {
            "title": title,
            "genre": genre,
            "status": "created",
            "created_at": meta["created_at"],
        }
        self._save_index(index)

        return project_id

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        """获取项目元数据"""
        path = self.data_dir / project_id / "project.json"
        if not path.exists():
            return None
        return self._read_json(path)

    def update_project_status(self, project_id: str, status: str):
        """更新项目状态"""
        path = self.data_dir / project_id / "project.json"
        meta = self._read_json(path)
        meta["status"] = status
        meta["updated_at"] = datetime.now().isoformat()
        self._write_json(path, meta)

        index = self._load_index()
        if project_id in index:
            index[project_id]["status"] = status
            self._save_index(index)

    def save_topic(self, project_id: str, topic_data: dict):
        """保存选题结果"""
        self._write_json(self.data_dir / project_id / "topic.json", topic_data)

    def get_topic(self, project_id: str) -> dict | None:
        return self._read_json_safe(self.data_dir / project_id / "topic.json")

    def save_world(self, project_id: str, world_data: dict):
        """保存世界观设定"""
        self._write_json(self.data_dir / project_id / "world.json", world_data)

    def get_world(self, project_id: str) -> dict | None:
        return self._read_json_safe(self.data_dir / project_id / "world.json")

    def save_characters(self, project_id: str, characters_data: dict):
        """保存角色设计"""
        self._write_json(self.data_dir / project_id / "characters.json", characters_data)

    def get_characters(self, project_id: str) -> dict | None:
        return self._read_json_safe(self.data_dir / project_id / "characters.json")

    def save_outline(self, project_id: str, outline_data: dict):
        """保存章节大纲"""
        self._write_json(self.data_dir / project_id / "outline.json", outline_data)

    def get_outline(self, project_id: str) -> dict | None:
        return self._read_json_safe(self.data_dir / project_id / "outline.json")

    def save_scene(self, project_id: str, chapter_num: int, scene_data: dict):
        """保存某章的场景细纲"""
        scenes_dir = self.data_dir / project_id / "scenes"
        scenes_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(scenes_dir / f"ch{chapter_num:02d}.json", scene_data)

    def get_scene(self, project_id: str, chapter_num: int) -> dict | None:
        return self._read_json_safe(
            self.data_dir / project_id / "scenes" / f"ch{chapter_num:02d}.json"
        )

    def save_draft(self, project_id: str, chapter_num: int, content: str):
        """保存某章初稿（Markdown）"""
        drafts_dir = self.data_dir / project_id / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        (drafts_dir / f"ch{chapter_num:02d}.md").write_text(content, encoding="utf-8")

    def get_draft(self, project_id: str, chapter_num: int) -> str | None:
        path = self.data_dir / project_id / "drafts" / f"ch{chapter_num:02d}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def get_all_drafts(self, project_id: str) -> list[tuple[int, str]]:
        """获取所有章节草稿，按章节号排序"""
        drafts_dir = self.data_dir / project_id / "drafts"
        if not drafts_dir.exists():
            return []
        result = []
        for f in sorted(drafts_dir.glob("ch*.md")):
            num = int(f.stem.replace("ch", ""))
            result.append((num, f.read_text(encoding="utf-8")))
        return result

    def save_review(self, project_id: str, review_data: dict):
        """保存审校报告"""
        self._write_json(self.data_dir / project_id / "review.json", review_data)

    def get_review(self, project_id: str) -> dict | None:
        return self._read_json_safe(self.data_dir / project_id / "review.json")

    def list_projects(self) -> list[dict[str, Any]]:
        """列出所有项目"""
        index = self._load_index()
        result = []
        for pid, info in index.items():
            result.append({"id": pid, **info})
        result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return result

    def project_exists(self, project_id: str) -> bool:
        """检查项目是否存在"""
        return (self.data_dir / project_id / "project.json").exists()

    def get_project_dir(self, project_id: str) -> Path:
        """获取项目数据目录"""
        return self.data_dir / project_id

    def get_output_dir(self, project_id: str) -> Path:
        """获取项目输出目录"""
        out = self.output_dir / project_id
        out.mkdir(parents=True, exist_ok=True)
        return out

    # ── 内部工具 ──────────────────────────────────────────────

    @staticmethod
    def _write_json(path: Path, data: Any):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _read_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _read_json_safe(path: Path) -> Any | None:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return None
