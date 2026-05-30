# Tasks Index

| ID | Slug | Status | Priority | Objective | Link |
|---:|---|---|---|---|---|
| 0001 | repair-ci-lint-and-paths | ✅ Done | P0 | 修复迁移后 CI lint 失效 | `tasks/0001-repair-ci-lint-and-paths/` |
| 0002 | book-metadata-generation | ✅ 完成 | P0 | 书名+简介+标签+分类 自动生成 | `tasks/0002-book-metadata-generation/` |
| 0003 | inline-editing | ✅ 完成 | P0 | 二次编辑功能 | `tasks/0003-inline-editing/` |
| 0004 | cover-generation | 🟡 待开始 | P0 | 封面生成（AI绘图） | `tasks/0004-cover-generation/` |
| 0005 | publish-packaging | 🟡 待开始 | P0 | 发布打包（TXT/图文/视频导出） | `tasks/0005-publish-packaging/` |
| 0006 | platform-taxonomy | 🟡 待开始 | P0 | 番茄/小红书分类体系对接 | `tasks/0006-platform-taxonomy/` |
| 0007 | process-realignment | 🟢 进行中 | P0 | 审计并回正任务包驱动开发流程 | `tasks/0007-process-realignment/` |
| 0008 | frontend-api-contract-repair | ✅ 完成 | P0 | 修复详情页阶段确认与前后端契约 | `tasks/0008-frontend-api-contract-repair/` |

## 执行顺序

```
0007 (流程回正) → 0008 (前后端契约修复) → 0006 (分类体系) → 0004 (封面) → 0005 (发布打包)
```
