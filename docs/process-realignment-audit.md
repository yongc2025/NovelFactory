# 流程回正审计

> 日期：2026-05-30  
> 任务：`tasks/0007-process-realignment/`

## 审计范围

- 根目录 `AGENTS.md` 与父级 `d:/workspace/vibe-coding-cn/AGENTS.md`。
- `tasks/INDEX.md`、`docs/TASKS.md`、现有任务包结构。
- 当前工作树状态。
- 前端审计中发现的前后端契约偏离。

## P0 偏离

| 偏离 | 证据 | 影响 | 回正动作 |
|------|------|------|----------|
| 当前改动未绑定活跃任务包 | `git status --short` 显示大量前后端、文档、任务文件改动 | 无法按验收标准判断变更边界 | 以 0007 作为流程回正入口，后续代码修复必须拆任务 |
| 任务完成状态不可信 | `0003-inline-editing` 标记完成，但前端审计发现章节保存、阶段确认、角色编辑等 P0/P1 问题 | 已完成任务可能继续产生运行时错误 | 创建专门契约修复任务重新验收 |
| 前后端流水线状态契约不一致 | 前端读取 `pipelineStatus.stages`，后端返回 `progress_percent/completed_stages/status` | 项目详情页存在运行时报错风险 | P0 修复 API adapter 或统一后端响应 |
| 阶段确认协议不一致 | 前端发送 `approve`，后端只接受 `adopt/edit/regenerate` | 阶段确认不可用 | P0 统一 `ConfirmAction` 和请求体 |
| 阶段状态接口路径不一致 | 前端请求 `/pipeline/stages`，后端实现 `/stages` | 阶段状态追踪不可用 | P0 统一路由封装 |

## P1 偏离

| 偏离 | 证据 | 影响 | 回正动作 |
|------|------|------|----------|
| 任务包结构不完整 | `0003` 缺少 `CONTEXT/ACCEPTANCE/TODO`，`0004-0006` 仅有 README | 任务验收不可复现 | 建立任务包补全任务 |
| `tasks/INDEX.md` 与 `docs/TASKS.md` 分叉 | `docs/TASKS.md` 记录未入索引的伪任务 | 人和 Agent 看到的优先级不同 | 每次任务状态变更同步两处 |
| 设计文档与实现状态过时 | `docs/gap-analysis.md` 中部分路由描述已与当前路由不一致 | 后续规划会基于旧事实 | 新建文档同步任务 |
| 前端超出代码规范 | `ProjectDetail.vue`、`ProjectCreate.vue` 等超过 350 行 | 后续修复容易继续扩大巨型组件 | 拆分应在独立 refactor 任务中执行 |
| `any` 使用超出规范 | `web/src/api/index.ts`、`web/src/stores/project.ts`、视图组件中广泛存在 `any` | 类型系统无法保护接口契约 | 在契约修复任务中引入响应类型和类型守卫 |

## 已执行回正

- 创建 `tasks/0007-process-realignment/` 完整任务包。
- 新增本审计文档，作为后续任务拆分依据。
- 将 0007 同步到任务索引和任务清单。

## 建议后续任务

| 建议 ID | 任务 | 优先级 | 目标 |
|--------|------|--------|------|
| 0008 | frontend-api-contract-repair | P0 | 修复前端 API adapter、流水线状态、阶段确认、章节/角色保存 |
| 0009 | task-bundle-normalization | P1 | 补齐 0001-0006 的任务包结构与真实状态 |
| 0010 | architecture-doc-sync | P1 | 同步设计文档、实现现状和延后项 |
| 0011 | frontend-component-split | P1 | 拆分超限 Vue 文件，降低后续修复风险 |

## 执行原则

- 先任务包，后代码。
- 先契约修复，后功能扩写。
- 先验证真实状态，后标记完成。
- 不回滚用户改动，只把边界和验收标准补齐。
