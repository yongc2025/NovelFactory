# ACCEPTANCE — 流程回正

## 必须满足

- [ ] `tasks/0007-process-realignment/` 包含 `CONTEXT.md`、`PLAN.md`、`ACCEPTANCE.md`、`STATUS.md`、`TODO.md`。
- [ ] `tasks/INDEX.md` 新增 0007，并标记为当前 P0 流程回正任务。
- [ ] `docs/TASKS.md` 与 `tasks/INDEX.md` 同步，能够看到 0007 当前状态。
- [ ] `docs/process-realignment-audit.md` 记录当前 P0/P1 偏离点和后续任务建议。
- [ ] 本任务不修改前后端生产代码。

## 后续门禁

- [ ] 任何前后端修复必须先创建或更新对应任务包。
- [ ] 已标记完成但存在回归的任务，需要在新任务中重新验收或修订状态。
- [ ] 任务完成后必须同步 `STATUS.md`、`TODO.md`、`tasks/INDEX.md`、`docs/TASKS.md`。
