"""CLI 入口 -- 使用 Typer + Rich 美化输出

命令:
    novel-factory plan "灵感描述" --genre 重生 --chapters 10
    novel-factory write <project_id>
    novel-factory review <project_id>
    novel-factory list
    novel-factory new "灵感描述" --words 8000
"""

from __future__ import annotations

import asyncio
import sys
from typing import Optional

# Windows 下强制使用 UTF-8 输出，避免 GBK 编码错误
if sys.platform == "win32":
    import ctypes
    # 设置控制台代码页为 UTF-8 (65001) — 通过 Win32 API 直接设置
    # 这影响 Rich 的 legacy_windows_render 路径
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    import os
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.system("chcp 65001 >nul 2>&1")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import typer

console = Console()

app = typer.Typer(
    name="novel-factory",
    help="NovelFactory -- 自动化小说工厂：从灵感到全平台分发的多形态内容",
    add_completion=False,
)


def _run_async(coro):
    """运行异步函数（兼容已有事件循环）"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)


# ── plan：规划模式 ────────────────────────────────────────────


@app.command()
def plan(
    inspiration: str = typer.Argument(..., help="灵感描述"),
    genre: Optional[str] = typer.Option(None, "--genre", "-g", help="题材提示，如：重生、穿越、都市"),
    chapters: int = typer.Option(10, "--chapters", "-c", help="目标章节数"),
):
    """规划模式：选题 -> 世界观 -> 角色 -> 大纲

    只生成大纲，不写正文。适合先审阅结构再决定是否继续。

    示例:
        novel-factory plan "渣男和闺蜜联手害死后重生到被害前" --genre 重生 --chapters 10
    """
    from novel_factory.pipeline import NovelPipeline

    pipeline = NovelPipeline()
    project_id = _run_async(pipeline.plan_only(
        inspiration=inspiration,
        genre_hint=genre,
        target_chapters=chapters,
    ))

    console.print(f"\n[dim]提示：使用 [bold]novel-factory write {project_id}[/bold] 生成正文[/dim]\n")


# ── write：从大纲生成正文 ─────────────────────────────────────


@app.command()
def write(
    project_id: str = typer.Argument(..., help="项目 ID"),
):
    """从已有大纲生成正文

    逐章生成场景细纲 + 正文，输出到 data/<project_id>/drafts/

    示例:
        novel-factory write 20260528_191500_abc123
    """
    from novel_factory.pipeline import NovelPipeline

    pipeline = NovelPipeline()

    project = pipeline.store.get_project(project_id)
    if not project:
        console.print(f"[red]项目不存在: {project_id}[/red]")
        console.print("[dim]使用 [bold]novel-factory list[/bold] 查看所有项目[/dim]")
        raise typer.Exit(1)

    outline = pipeline.store.get_outline(project_id)
    if not outline:
        console.print(f"[red]项目 {project_id} 没有大纲，请先运行 plan[/red]")
        raise typer.Exit(1)

    project_id = _run_async(pipeline.write_from_outline(project_id))

    console.print(f"\n[dim]提示：使用 [bold]novel-factory review {project_id}[/bold] 运行审校[/dim]\n")


# ── review：审校 ──────────────────────────────────────────────


@app.command()
def review(
    project_id: str = typer.Argument(..., help="项目 ID"),
):
    """运行审校，输出审校报告

    检查角色一致性、时间线、伏笔、节奏、对话质量等。

    示例:
        novel-factory review 20260528_191500_abc123
    """
    from novel_factory.pipeline import NovelPipeline

    pipeline = NovelPipeline()

    project = pipeline.store.get_project(project_id)
    if not project:
        console.print(f"[red]项目不存在: {project_id}[/red]")
        raise typer.Exit(1)

    drafts = pipeline.store.get_all_drafts(project_id)
    if not drafts:
        console.print(f"[red]项目 {project_id} 没有正文，请先运行 write[/red]")
        raise typer.Exit(1)

    console.print()
    console.print(
        Panel(
            f"[bold cyan]项目:[/bold cyan] {project.get('title', project_id)}\n"
            f"[bold cyan]章节数:[/bold cyan] {len(drafts)}",
            title="[审校] 编辑审校",
            border_style="cyan",
        )
    )

    result = _run_async(pipeline._step_review(project_id))
    _print_review_report(result, project.get("title", project_id))

    console.print(f"\n[dim]审校报告已保存到 data/{project_id}/review.json[/dim]\n")


# ── list：列出所有项目 ────────────────────────────────────────


@app.command(name="list")
def list_projects():
    """列出所有项目

    显示项目 ID、标题、题材、状态、创建时间。
    """
    from novel_factory.db.project_store import ProjectStore

    store = ProjectStore()
    projects = store.list_projects()

    if not projects:
        console.print("[yellow]还没有项目[/yellow]")
        console.print("[dim]使用 [bold]novel-factory plan[/bold] 或 [bold]novel-factory new[/bold] 创建项目[/dim]\n")
        return

    table = Table(
        title="[项目列表]",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        padding=(0, 1),
    )
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("标题", style="bold")
    table.add_column("题材", style="green")
    table.add_column("状态", justify="center")
    table.add_column("创建时间", style="dim")

    status_styles = {
        "created": "[yellow]已创建[/yellow]",
        "topic_done": "[blue]选题完成[/blue]",
        "world_done": "[blue]世界观完成[/blue]",
        "characters_done": "[blue]角色完成[/blue]",
        "outlined": "[cyan]已规划[/cyan]",
        "planned": "[cyan]已规划[/cyan]",
        "drafting": "[magenta]写作中[/magenta]",
        "drafted": "[green]已完稿[/green]",
        "reviewed": "[green]已审校[/green]",
        "complete": "[bold green]完成[/bold green]",
    }

    for p in projects:
        status = p.get("status", "unknown")
        status_display = status_styles.get(status, f"[dim]{status}[/dim]")
        created = p.get("created_at", "")[:16].replace("T", " ")

        table.add_row(
            p["id"],
            p.get("title", "--"),
            p.get("genre", "--") or "--",
            status_display,
            created,
        )

    console.print()
    console.print(table)
    console.print()


# ── new：完整流程 ─────────────────────────────────────────────


@app.command(name="new")
def new_novel(
    inspiration: str = typer.Argument(..., help="灵感描述"),
    words: int = typer.Option(8000, "--words", "-w", help="目标字数"),
    genre: Optional[str] = typer.Option(None, "--genre", "-g", help="题材提示"),
):
    """完整流程：选题 -> 世界观 -> 角色 -> 大纲 -> 场景 -> 正文 -> 审校

    一键从灵感到完整小说。

    示例:
        novel-factory new "渣男和闺蜜联手害死后重生到被害前" --words 8000 --genre 重生
    """
    from novel_factory.pipeline import NovelPipeline

    pipeline = NovelPipeline()
    project_id = _run_async(pipeline.run_full_pipeline(
        inspiration=inspiration,
        genre_hint=genre,
        target_words=words,
    ))

    console.print(f"\n[dim]提示：使用 [bold]novel-factory review {project_id}[/bold] 重新审校[/dim]\n")


# ── 辅助函数 ──────────────────────────────────────────────────


def _print_review_report(review: dict, title: str):
    """打印审校报告"""
    console.print()

    info_table = Table(show_header=False, border_style="blue", padding=(0, 2))
    info_table.add_column("项目", style="bold")
    info_table.add_column("值")
    info_table.add_row("总章节数", str(review.get("total_chapters", "--")))
    info_table.add_row("总字数", str(review.get("total_words", "--")))
    if review.get("score") is not None:
        info_table.add_row("评分", str(review["score"]))

    console.print(Panel(info_table, title=f"[审校报告] {title}", border_style="blue"))

    checks = review.get("checks", {})
    if checks:
        check_table = Table(
            show_header=True,
            header_style="bold",
            border_style="green",
            title="[检查项]",
        )
        check_table.add_column("检查项", style="bold")
        check_table.add_column("结果", justify="center")

        check_names = {
            "character_consistency": "角色一致性",
            "timeline_consistency": "时间线一致性",
            "foreshadow_tracking": "伏笔追踪",
            "pacing": "节奏把控",
            "dialogue_quality": "对话质量",
        }

        for key, value in checks.items():
            display_name = check_names.get(key, key)
            if value == "待检查":
                display = "[yellow]待检查[/yellow]"
            elif "通过" in str(value) or "OK" in str(value).upper():
                display = f"[green]{value}[/green]"
            elif "问题" in str(value) or "error" in str(value).lower():
                display = f"[red]{value}[/red]"
            else:
                display = str(value)
            check_table.add_row(display_name, display)

        console.print(check_table)

    issues = review.get("issues", [])
    if issues:
        console.print("\n[bold red]发现的问题:[/bold red]")
        for i, issue in enumerate(issues, 1):
            if isinstance(issue, dict):
                severity = issue.get("severity", "info")
                msg = issue.get("message", str(issue))
                style = "red" if severity == "error" else ("yellow" if severity == "warning" else "dim")
                console.print(f"  {i}. [{style}]{msg}[/{style}]")
            else:
                console.print(f"  {i}. {issue}")
    else:
        console.print("\n[green]未发现明显问题[/green]")

    note = review.get("note")
    if note:
        console.print(f"\n[dim]{note}[/dim]")


# ── 入口 ──────────────────────────────────────────────────────


def main():
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    main()
