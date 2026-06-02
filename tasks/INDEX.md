# Tasks Index

| ID | Slug | Status | Priority | Objective | Link |
|---:|---|---|---|---|---|
| 0001 | repair-ci-lint-and-paths | ✅ Done | P0 | 修复迁移后 CI lint 失效 | `tasks/0001-repair-ci-lint-and-paths/` |
| 0002 | book-metadata-generation | ✅ 完成 | P0 | 书名+简介+标签+分类 自动生成 | `tasks/0002-book-metadata-generation/` |
| 0003 | inline-editing | ✅ 完成 | P0 | 二次编辑功能 | `tasks/0003-inline-editing/` |
| 0004 | cover-generation | 🟡 待开始 | P0 | 封面生成（AI绘图） | `tasks/0004-cover-generation/` |
| 0005 | publish-packaging | 🟡 待开始 | P0 | 发布打包（TXT/图文/视频导出） | `tasks/0005-publish-packaging/` |
| 0006 | platform-taxonomy | 🟡 待开始 | P0 | 番茄/小红书分类体系对接 | `tasks/0006-platform-taxonomy/` |
| 0007 | process-realignment | 🟡 进行中 | P0 | 审计并回正任务包驱动开发流程 | `tasks/0007-process-realignment/` |
| 0008 | frontend-api-contract-repair | ✅ 完成 | P0 | 修复详情页阶段确认与前后端契约 | `tasks/0008-frontend-api-contract-repair/` |
| 0009 | project-detail-action-bar-polish | ✅ 完成 | P0 | 修复详情页顶部操作栏行为与按钮样式 | `tasks/0009-project-detail-action-bar-polish/` |
| 0010 | world-generation-contract-repair | ✅ 完成 | P0 | 修复世界观生成与前端展示契约 | `tasks/0010-world-generation-contract-repair/` |
| 0011 | pipeline-task-registry | ✅ 完成 | P0 | 异步任务注册表（幂等+互斥+状态机） | `tasks/0011-pipeline-task-registry/` |
| 0012 | context-store | ✅ 完成 | P0 | 上下文存储（前文摘要+审校结果） | `tasks/0012-context-store/` |
| 0013 | draft-batch-generation | ✅ 完成 | P0 | 正文批量生成（10章/批+上下文+进度） | `tasks/0013-draft-batch-generation/` |
| 0014 | scene-tab | ✅ 完成 | P0 | 前端场景细纲 Tab | `tasks/0014-scene-tab/` |
| 0015 | review-per-chapter | ✅ 完成 | P0 | 逐章审校+上下文 | `tasks/0015-review-per-chapter/` |
| 0016 | post-review-workflow | ✅ 完成 | P0 | 审校后调整流程 | `tasks/0016-post-review-workflow/` |
| 0017 | frontend-task-status | ✅ 完成 | P0 | 前端任务状态展示（useTaskPoller+右侧面板） | `tasks/0017-frontend-task-status/` |
| 0018 | full-flow-functional-audit | 🟡 待开始 | P0 | 全流程功能审计 | `tasks/0018-full-flow-functional-audit/` |
| 0019 | context-pipeline-fix | ✅ 完成 | P0 | 修复 prev_summary 传递链 + build_context + 摘要统一入口 | `tasks/0019-context-pipeline-fix/` |
| 0020 | character-consistency-fix | ✅ 完成 | P0 | 角色名硬约束 + 角色卡完整传递 + scene 角色状态注入 | `tasks/0020-character-consistency-fix/` |
| 0021 | api-contract-unify | ✅ 完成 | P0+P1 | ApiResponse 统一 + 消除双层嵌套 + 合并确认接口 | `tasks/0021-api-contract-unify/` |
| 0022 | frontend-decompose | ✅ 完成 | P0+P1 | ProjectDetail.vue 1223→<300 行拆分 + Loading 精细化 | `tasks/0022-frontend-decompose/` |
| 0023 | foreshadow-tracking | 🟡 PENDING | P1 | 伏笔结构化（id+status）+ editor 写回 + 自动修订闭环 | `tasks/0023-foreshadow-tracking/` |
| 0024 | state-unify-persist | 🟡 PENDING | P0+P1 | 废弃 _pipeline_states + TaskRegistry SQLite + confirming 超时 | `tasks/0024-state-unify-persist/` |

## 执行顺序

```
Phase 1：基础设施
  0011 (TaskRegistry) → 0012 (ContextStore)

Phase 2：正文生成改造
  0013 (批量正文) ← 依赖 0011 + 0012

Phase 3：场景+审校
  0014 (Scene Tab) → 0015 (逐章审校) → 0016 (审校后调整)

Phase 4：前端统一
  0017 (前端任务状态) ← 依赖 0011

============================================================
2026-05-31 综合审计后新增（详见 docs/architecture-audit-2026-05-31.md）：

Phase A 紧急止血（修 P0 数据流断裂 + 角色名漂移）
  0019 (context-pipeline-fix) → 0020 (character-consistency-fix)

Phase B 架构修复（契约统一 + 前端拆分）
  0021 (api-contract-unify) → 0022 (frontend-decompose)
  注：0021 与 0022 涉及前后端类型契约，必须 0021 先于 0022

Phase C 内容质量
  0023 (foreshadow-tracking)
  注：依赖 0019（摘要生成已通）

Phase D 工程加固
  0024 (state-unify-persist)
  注：可独立于其他任务进行
============================================================

全部完成后：
  0006 (分类体系) → 0004 (封面) → 0005 (发布打包)
```

## Phase 工时估算

| Phase | 任务 | 工时 |
|-------|------|------|
| A | 0019 + 0020 | 6h |
| B | 0021 + 0022 | 16h |
| C | 0023 | 5h |
| D | 0024 | 8h |
| **合计** | **6 个包** | **35h** |