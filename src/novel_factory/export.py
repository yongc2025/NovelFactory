"""导出工具 -- 将项目导出为 Markdown 文件

导出到 output/<project_id>/ 目录。
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from novel_factory.db.project_store import ProjectStore

console = Console()


def export_to_markdown(project_id: str) -> str:
    """导出完整小说为单个 Markdown 文件

    将所有章节合并为一个文件，输出到 output/<project_id>/<标题>.md

    Args:
        project_id: 项目 ID

    Returns:
        输出文件路径
    """
    store = ProjectStore()
    project = store.get_project(project_id)
    if not project:
        raise FileNotFoundError(f"项目不存在: {project_id}")

    drafts = store.get_all_drafts(project_id)
    if not drafts:
        raise FileNotFoundError(f"项目 {project_id} 没有正文内容")

    outline = store.get_outline(project_id)
    characters = store.get_characters(project_id)
    world = store.get_world(project_id)

    title = project.get("title", project_id)
    output_dir = store.get_output_dir(project_id)
    output_path = output_dir / f"{title}.md"

    lines = []

    # 封面信息
    lines.append(f"# {title}\n")
    lines.append(f"> **题材:** {project.get('genre', '--') or '--'}\n")
    lines.append(f"> **目标字数:** {project.get('target_words', '--')}\n")
    lines.append(f"> **灵感:** {project.get('inspiration', '--')}\n")
    lines.append("---\n")

    # 世界观摘要（如果有）
    if world and isinstance(world, dict):
        lines.append("## 世界观设定\n")
        for key, value in world.items():
            if key == "note":
                continue
            if isinstance(value, list):
                lines.append(f"**{key}:** {', '.join(str(v) for v in value)}\n")
            elif isinstance(value, dict):
                lines.append(f"**{key}:**\n")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}\n")
            else:
                lines.append(f"**{key}:** {value}\n")
        lines.append("---\n")

    # 角色摘要（如果有）
    if characters and isinstance(characters, dict):
        lines.append("## 角色介绍\n")
        for char_key, char_data in characters.items():
            if char_key == "note":
                continue
            if isinstance(char_data, dict):
                char_name = char_data.get("name", char_key)
                lines.append(f"### {char_name}\n")
                for k, v in char_data.items():
                    if k == "name":
                        continue
                    lines.append(f"- **{k}:** {v}\n")
                lines.append("\n")
        lines.append("---\n")

    # 目录
    lines.append("## 目录\n")
    for ch_num, _ in drafts:
        ch_title = f"第{ch_num}章"
        # 尝试从大纲获取章节标题
        if outline and isinstance(outline, dict):
            for ch in outline.get("chapters", []):
                if ch.get("chapter_num") == ch_num:
                    ch_title = ch.get("title", ch_title)
                    break
        lines.append(f"- [{ch_title}](#第{ch_num}章)\n")
    lines.append("---\n")

    # 正文
    for ch_num, content in drafts:
        lines.append(content)
        if not content.endswith("\n"):
            lines.append("\n")
        lines.append("---\n")

    # 统计
    total_words = sum(len(text) for _, text in drafts)
    lines.append(f"\n> **统计:** {len(drafts)} 章，共 {total_words} 字\n")

    # 写入文件
    output_path.write_text("".join(lines), encoding="utf-8")

    console.print(f"[green]已导出:[/green] {output_path}")
    return str(output_path)


def export_chapters_separately(project_id: str) -> list[str]:
    """每章单独导出为一个 Markdown 文件

    输出到 output/<project_id>/chapters/ 目录

    Args:
        project_id: 项目 ID

    Returns:
        输出文件路径列表
    """
    store = ProjectStore()
    project = store.get_project(project_id)
    if not project:
        raise FileNotFoundError(f"项目不存在: {project_id}")

    drafts = store.get_all_drafts(project_id)
    if not drafts:
        raise FileNotFoundError(f"项目 {project_id} 没有正文内容")

    outline = store.get_outline(project_id)
    title = project.get("title", project_id)

    output_dir = store.get_output_dir(project_id)
    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    output_files = []

    for ch_num, content in drafts:
        # 获取章节标题
        ch_title = f"第{ch_num}章"
        if outline and isinstance(outline, dict):
            for ch in outline.get("chapters", []):
                if ch.get("chapter_num") == ch_num:
                    ch_title = ch.get("title", ch_title)
                    break

        # 构建文件内容
        lines = []
        lines.append(f"# {ch_title}\n")
        lines.append(f"> 来自: {title}\n")
        lines.append("---\n")
        lines.append(content)
        if not content.endswith("\n"):
            lines.append("\n")

        # 写入文件
        file_path = chapters_dir / f"ch{ch_num:02d}_{ch_title}.md"
        file_path.write_text("".join(lines), encoding="utf-8")
        output_files.append(str(file_path))

    # 生成索引文件
    index_lines = [f"# {title} -- 章节目录\n\n"]
    for ch_num, _ in drafts:
        ch_title = f"第{ch_num}章"
        if outline and isinstance(outline, dict):
            for ch in outline.get("chapters", []):
                if ch.get("chapter_num") == ch_num:
                    ch_title = ch.get("title", ch_title)
                    break
        file_name = f"ch{ch_num:02d}_{ch_title}.md"
        index_lines.append(f"- [{ch_title}]({file_name})\n")

    index_path = chapters_dir / "INDEX.md"
    index_path.write_text("".join(index_lines), encoding="utf-8")
    output_files.append(str(index_path))

    console.print(f"[green]已导出 {len(drafts)} 个章节文件到:[/green] {chapters_dir}")
    return output_files
