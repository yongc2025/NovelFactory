# 任务清单

> 同步自 `tasks/INDEX.md`，每次完成任务后同步更新此处。

## 进行中 / 待开始

| ID | Slug | 状态 | 优先级 | 目标 | 备注 |
|---:|---|---|---|---|---|
| 0023 | foreshadow-tracking | ✅ Done | P1 | 伏笔结构化追踪与自动修订 | 2026-06-02 |
| 0024 | state-unify-persist | ✅ Done | P0+P1 | 状态机统一与持久化（SQLite） | 2026-06-02 |
| 0004 | cover-generation | 🟡 待开始 | P1 | 封面生成（AI 绘图） | |
| 0005 | publish-packaging | 🟡 待开始 | P1 | 发布打包（TXT/图文/视频导出） | |
| 0006 | platform-taxonomy | 🟡 待开始 | P2 | 番茄/小红书分类体系对接 | |

## 已完成

| ID | Slug | 状态 | 优先级 | 目标 | 完成时间 |
|---:|---|---|---|---|---|
| 0022 | frontend-decompose | ✅ Done | P0+P1 | ProjectDetail.vue 巨型组件拆分 | 2026-06-01 |
| 0021 | api-contract-unify | ✅ Done | P0+P1 | ApiResponse 统一与协议体简化 | 2026-06-01 |
| 0020 | character-consistency-fix | ✅ Done | P0 | 角色名硬约束与 12D 灵魂注入 | 2026-06-01 |
| 0019 | context-pipeline-fix | ✅ Done | P0 | 修复前文摘要传递链与上下文构建 | 2026-06-01 |
| 0017 | frontend-task-status | ✅ Done | P0 | 前端任务状态展示（右侧面板） | 2026-05-31 |
| 0016 | post-review-workflow | ✅ Done | P0 | 审校后调整流程 | 2026-05-30 |
| 0015 | review-per-chapter | ✅ Done | P0 | 逐章审校逻辑实现 | 2026-05-30 |
| 0014 | scene-tab | ✅ Done | P0 | 前端场景细纲展示页 | 2026-05-30 |
| 0013 | draft-batch-generation | ✅ Done | P0 | 正文批量生成（10章/批） | 2026-05-30 |
| 0012 | context-store | ✅ Done | P0 | 上下文存储（摘要/审校） | 2026-05-29 |
| 0011 | pipeline-task-registry | ✅ Done | P0 | 异步任务注册表（幂等/互斥） | 2026-05-29 |
| 0010 | world-generation-contract-repair | ✅ Done | P0 | 修复世界观生成契约 | 2026-05-30 |
| 0009 | project-detail-action-bar-polish | ✅ Done | P0 | 操作栏行为与样式优化 | 2026-05-30 |
| 0008 | frontend-api-contract-repair | ✅ Done | P0 | 详情页阶段确认契约修复 | 2026-05-30 |
| 0007 | process-realignment | ✅ Done | P0 | 流程审计与回正 | 2026-05-31 |
| 0003 | inline-editing | ✅ Done | P0 | 二次编辑功能 | 2026-05-28 |
| 0002 | book-metadata-generation | ✅ Done | P0 | AI 书名/简介/标签生成 | 2026-05-28 |
| 0001 | repair-ci-lint-and-paths | ✅ Done | P0 | 修复迁移后状态 | 2026-05-28 |
| — | coding-standards | ✅ Done | P1 | 编码规范文档 | 2026-05-29 |
| — | docs-alignment | ✅ Done | P1 | 设计与实现对齐 | 2026-05-29 |

## 2026-05-31 架构审计结论

详见 `docs/architecture-audit-2026-05-31.md`。
当前进入 **Phase A: 紧急止血**，修复 P0 级数据流断裂与内容质量问题。

## 待转化任务的设计需求

| 需求 | 来源 | 说明 |
|------|------|------|
| WebSocket 实时进度 | frontend-architecture.md | 替代轮询 |
| SQLite + FTS5 存储 | system-architecture.md | 替代 JSON 存储 |
| 角色关系图 | frontend-architecture.md | ECharts 展示 |
| TXT/EPUB/PDF 导出 | frontend-architecture.md | 多格式支持 |

