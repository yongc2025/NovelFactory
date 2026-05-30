# 任务清单

> 同步自 `tasks/INDEX.md`，每次完成任务后同步更新此处。

## 进行中 / 待开始

| ID | Slug | 状态 | 优先级 | 目标 |
|---:|---|---|---|---|
| 0007 | process-realignment | 🟢 进行中 | P0 | 审计并回正任务包驱动开发流程 |
| 0004 | cover-generation | 🟡 待开始 | P0 | 封面生成（AI 绘图） |
| 0005 | publish-packaging | 🟡 待开始 | P0 | 发布打包（TXT/图文/视频导出） |
| 0006 | platform-taxonomy | 🟡 待开始 | P0 | 番茄/小红书分类体系对接 |

## 已完成

| ID | Slug | 状态 | 优先级 | 目标 | 完成时间 |
|---:|---|---|---|---|---|
| 0001 | repair-ci-lint-and-paths | ✅ Done | P0 | 修复迁移后 CI lint 失效 | 2026-05-28 |
| 0002 | book-metadata-generation | ✅ Done | P0 | 书名+简介+标签+分类自动生成 | 2026-05-28 |
| 0003 | inline-editing | ✅ Done | P0 | 二次编辑功能 | 2026-05-28 |
| 0008 | frontend-api-contract-repair | ✅ Done | P0 | 修复详情页阶段确认与前后端契约 | 2026-05-30 |
| — | coding-standards | ✅ Done | P1 | 编码规范文档 + AGENTS.md 规则 | 2026-05-29 |
| — | docs-alignment | ✅ Done | P1 | 设计文档与实现对齐 | 2026-05-29 |

## 执行顺序（规划）

```
0007 (流程回正) → 0008 (前后端契约修复) → 0006 (分类体系) → 0004 (封面) → 0005 (发布打包)
```

## 当前流程回正结论

详见 `docs/process-realignment-audit.md`。`0008-frontend-api-contract-repair` 已完成；下一步建议补齐
`0009-task-bundle-normalization`，复核 0001-0006 的任务包结构与真实状态。

## 未列入 Task 的设计需求（来自系统设计文档）

以下需求在设计文档中有定义，但尚未创建对应的 Task：

| 需求 | 来源 | 说明 |
|------|------|------|
| WebSocket 实时进度 | frontend-architecture.md | 替代轮询，推送流水线状态 |
| SQLite + FTS5 存储 | system-architecture.md | 替代 JSON 文件存储 |
| 记忆系统 | system-architecture.md | 角色状态/层次摘要/伏笔追踪/滑动窗口 |
| 大纲拖拽排序 | frontend-architecture.md | vuedraggable 章节排序 |
| 正文编辑模式 | frontend-architecture.md | Markdown 编辑器 + 自动保存 |
| 审校报告对比视图 | frontend-architecture.md | 原文 vs 建议修改并排对比 |
| 角色关系图 | frontend-architecture.md | ECharts 力导向图 |
| 流水线日志流 | frontend-architecture.md | 实时日志输出 |
| 内容适配师 | system-architecture.md | 小红书/番茄/知乎格式转换 |
| 剧本改编编剧 | system-architecture.md | 漫剧/短剧分集剧本 |
| 漫剧制作人 | system-architecture.md | 分镜+绘图+配音+视频合成 |
| TXT/EPUB/PDF 导出 | frontend-architecture.md | 多格式导出 |
| 单阶段独立运行 | frontend-architecture.md | 只运行某个阶段 |
| 测试 | — | 核心流程 mock 测试 |
| 流水线断点续跑 | — | 阶段状态持久化，支持 resume |
| LLM 调用重试 | — | 指数退避重试 + 错误隔离 |
