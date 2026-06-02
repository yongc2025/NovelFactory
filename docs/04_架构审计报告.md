# NovelFactory 架构审计综合报告

> 日期：2026-05-31 | 审计方式：4 个只读专家并行（流程架构 / 后端契约 / 前端 UI / 内容生产闭环）
> 样本项目：20260529_231841_d80484（100 章）
> 详细子报告：`reports/audit-{pipeline,backend,frontend,content}.md`

---

## 1. 端到端主流程

```
用户创建项目 → [topic] 选题策划 → [world] 世界观 → [character] 角色 → [outline] 大纲
    → [scene] 场景细纲 → [draft] 正文生成 → [review] 审校 → [revise] 修订 → [metadata] 元数据
```

### 1.1 数据流全景

```
topic.json ─→ worldbuilder ─→ world.json ─→ character ─→ characters.json
                                                 │
                                                 ▼
              outliner ←── world.json + characters.json ─→ outline.json
                  │                                           │
                  ▼                                           ▼
              scene.py ←── outline.json ─→ scene/{ch}.json
                  │
                  ▼
              writer.py ←── scene + characters + outline + prev_summary(★断裂)
                  │
                  ▼
              drafts/{ch}.txt ─→ editor.py ←── characters + outline
                  │                         │
                  ▼                         ▼
              context/{ch}_summary.md    context/{ch}_review.json
                  │                         │
                  ▼                         ▼
              下一章 prev_summary(★)     revise_with_feedback(★断裂)
```

### 1.2 状态机

```
项目级：  created → planned → generating → reviewing → completed
Task级：  pending → running → success / failed / cancelled
阶段级：  idle → running → confirming → idle(adopt) / idle(regenerate)
```

**关键问题**：项目级状态（内存 dict）与 Task 级状态（TaskRegistry）双轨并行，互斥不统一。

### 1.3 数据持久化点

| 阶段 | 文件 | 持久化 | 备注 |
|------|------|--------|------|
| topic | topic.json | ? | |
| world | world.json | ? | |
| character | characters.json | ? | |
| outline | outline.json | ? | |
| scene | scenes/{ch}.json | ? | |
| draft | drafts/{ch}.txt | ? | |
| summary | context/{ch}_summary.md | ★ 实际未生成 | pipeline.run_full 不走 draft 分支 |
| review | context/{ch}_review.json | ? | |
| metadata | metadata.json | ? | |

---

## 2. 四维评分汇总

| 维度 | 评分 | 一句话 |
|------|------|--------|
| 流程架构 | **5/10** | 骨架在但数据流断裂（prev_summary）、双状态系统冲突、进程重启全丢 |
| 后端契约 | **5.5/10** | 端点覆盖全但前后端字段严重不对齐、ApiResponse 形同虚设、三套确认接口并存 |
| 前端 UI | **6.5/10** | 功能闭环但 ProjectDetail 1223 行超标 3.5 倍、场景 Tab 交互残缺、Loading 过重 |
| 内容闭环 | **3.5/10** | Prompt 框架优秀但闭环全断：角色名漂移、摘要未生成、伏笔假追踪、审校不反哺 |

**综合：5.1/10 — 能跑但脆弱，内容质量是最大短板**

---

## 3. P0 风险矩阵（阻断级）

| # | 风险 | 维度 | 位置 | 影响 | 工时 |
|---|------|------|------|------|------|
| P0-1 | **prev_summary 未传入 writer** | 流程+内容 | app.py:657-661, pipeline.py:335 | 跨章节上下文完全失效，每章无前文 | 1h |
| P0-2 | **角色名漂移** | 内容 | scene.py:36, writer.py WRITER_SYSTEM | 100 章主角名变化 3 次，角色卡全废 | 2h |
| P0-3 | **ReviewIssue.chapter_number 全为 0** | 后端 | app.py:1272 _normalize_review | 审校问题无法定位章节 | 0.5h |
| P0-4 | **错误消息字段不匹配** | 后端+前端 | 后端返回 detail，前端读 message | 所有 API 错误只显示"请求失败" | 0.5h |
| P0-5 | **双状态系统互斥失效** | 流程 | app.py:488-557 绕过 TaskRegistry | 可并发触发同一项目多任务 | 4h |
| P0-6 | **ProjectDetail.vue 1223 行** | 前端 | ProjectDetail.vue | 超标 3.5 倍，维护成本极高 | 6h |
| P0-7 | **build_context 从未被调用** | 内容 | writer.py 不用 memory.build_context() | sliding_window 永远"无前文" | 1h |
| P0-8 | **摘要实际未生成** | 流程+内容 | pipeline.run_full 不走 draft 分支 | 100 章项目零条摘要 | 1h |

---

## 4. P1 风险矩阵（高）

| # | 风险 | 维度 | 位置 | 工时 |
|---|------|------|------|------|
| P1-1 | ApiResponse 包装层名存实亡 | 后端 | 全端点 vs types/index.ts | 4h |
| P1-2 | 内容端点双层嵌套 | 后端 | topic/world/characters/outline/review | 2h |
| P1-3 | confirming 状态无超时 | 流程 | app.py:727-729 | 1h |
| P1-4 | _run_in_background 创建新事件循环 | 流程 | app.py:474-479 | 2h |
| P1-5 | review 不跳过已审章节 | 流程 | app.py:688-691 | 0.5h |
| P1-6 | review 阶段 prev_summary/prev_issues 未传入 | 流程+内容 | app.py:697-706 | 0.5h |
| P1-7 | scene 阶段不检查 cancel | 流程 | app.py:624-631 | 0.5h |
| P1-8 | Character.id 非持久（f"char_{index}"） | 后端 | app.py:990 | 1h |
| P1-9 | OutlineChapter 字段丢失 5 个 | 后端 | app.py:1119-1131 | 1h |
| P1-10 | 伏笔无 ID/无状态更新 | 内容 | outliner + editor | 3h |
| P1-11 | 角色卡仅传 3 字段 | 内容 | writer.py:48-51 | 1h |
| P1-12 | 审校不自动修订 | 内容 | app.py review 阶段 | 2h |
| P1-13 | store.loading 共享状态 | 前端 | stores/project.ts:27 | 1h |
| P1-14 | 全局 Loading 遮罩过重 | 前端 | ProjectDetail.vue:148 | 1h |
| P1-15 | 场景 Tab 无编辑/确认 | 前端 | ProjectDetail.vue:230-243 | 2h |
| P1-16 | 场景逐章串行加载 | 前端 | ProjectDetail.vue:131-134 | 0.5h |

---

## 5. 可落地改进清单（按收益/工时排序）

### Phase A：紧急止血（1-2 天，8h）

| # | 任务 | 工时 | 影响面 | 具体改动 |
|---|------|------|--------|----------|
| A1 | **修复 prev_summary 传递链** | 1h | 核心 | pipeline._step_draft 加 prev_summary 参数 → write_scene(prev_summary=...)；app.py:661 传入 |
| A2 | **修复 build_context 集成** | 1h | 核心 | writer.py 内部调用 memory.build_context()，替代硬编码占位符 |
| A3 | **修复角色名硬约束** | 2h | 核心 | writer_system 加"必须使用以下角色名"指令；scene.py 注入角色卡；editor_rules 加角色名校验 |
| A4 | **修复 ReviewIssue.chapter_number** | 0.5h | 后端 | _normalize_review 从 issue 中提取章节号而非硬编码 0 |
| A5 | **修复错误消息字段** | 0.5h | 全栈 | 统一后端错误格式为 {code, message, data}；或前端改读 detail |
| A6 | **摘要生成统一入口** | 1h | 核心 | pipeline.run_full 的 draft 步骤也走 app.py draft 分支，确保 generate_summary 被调用 |
| A7 | **review 阶段跳过已审+传上下文** | 1h | 流程 | 加 ctx_store.get_chapter_review skip + 传 prev_summary/prev_issues 给 editor |
| A8 | **scene 阶段加 cancel 检查** | 0.5h | 流程 | 循环内加 task.cancel_requested 检查 |

### Phase B：架构修复（3-5 天，16h）

| # | 任务 | 工时 | 影响面 | 具体改动 |
|---|------|------|--------|----------|
| B1 | **统一状态管理** | 4h | 架构 | 废弃 _pipeline_states，全部走 TaskRegistry；老端点改用 registry.submit() |
| B2 | **拆分 ProjectDetail.vue** | 6h | 前端 | 9 个 Tab 抽独立组件 + useProjectDetail composable；目标 <300 行 |
| B3 | **统一 ApiResponse 格式** | 4h | 全栈 | 后端统一包装 {code, message, data}；消除双层嵌套；前端类型对齐 |
| B4 | **合并三套确认接口** | 2h | 后端 | 统一为 /pipeline/stages/{stage}/confirm + ConfirmRequest schema |

### Phase C：内容质量提升（1 周，12h）

| # | 任务 | 工时 | 影响面 | 具体改动 |
|---|------|------|--------|----------|
| C1 | **伏笔系统结构化** | 3h | 内容 | foreshadow_ops 加 id/plant_chapter/resolve_chapter/status；editor 写回 status |
| C2 | **角色卡完整传递** | 1h | 内容 | writer char_info 扩展到 core_desire/core_fear/arc_description/speaking_style |
| C3 | **自动修订闭环** | 2h | 内容 | review 后 score<7 自动触发 revise_with_feedback |
| C4 | **scene 角色状态注入** | 1h | 内容 | character_states 传入角色摘要而非占位符 |
| C5 | **角色 current_state 追踪** | 2h | 内容 | 每章生成后用 LLM 更新角色 current_state |
| C6 | **分层摘要机制** | 3h | 内容 | 全书摘要→卷摘要→近 3 章摘要 |

### Phase D：工程加固（2 周，16h）

| # | 任务 | 工时 | 影响面 | 具体改动 |
|---|------|------|--------|----------|
| D1 | **TaskRegistry 持久化** | 6h | 架构 | 持久化到 SQLite；启动恢复 running→failed |
| D2 | **pipeline_stage 入参 Schema 化** | 2h | 后端 | StageRunRequest(base model) + 各阶段子类 |
| D3 | **_normalize_* 消除** | 4h | 后端 | LLM prompt 约束输出格式对齐前端 type；声明式映射替代 if-else 链 |
| D4 | **confirming 超时机制** | 1h | 流程 | 加 confirmed_at；启动扫描超时→idle |
| D5 | **前端体验优化** | 3h | 前端 | Tab 缓存/章节跳转/空状态统一/Loading 精细化 |

---

## 6. 下一阶段任务包提案

基于审计发现，建议新增以下任务包（接 0017 之后）：

### 0018-context-pipeline-fix（Phase A 核心修复）

- **目标**：修复 prev_summary 传递链 + build_context 集成 + 摘要生成统一入口
- **范围**：pipeline.py, writer.py, memory.py, app.py draft/review 分支
- **验收**：生成 10 章项目后，context/ 目录下有 10 条摘要；write_scene 调用日志含非空 prev_summary
- **工时**：3h

### 0019-character-consistency-fix（Phase A 角色修复）

- **目标**：修复角色名漂移 + 角色卡完整传递 + scene 角色状态注入
- **范围**：writer.py, scene.py, editor.py, prompts.py
- **验收**：生成 20 章项目，主角名在每章正确出现；editor_rules 报告角色名一致
- **工时**：3h

### 0020-api-contract-unify（Phase B 契约统一）

- **目标**：统一 ApiResponse + 消除双层嵌套 + 合并确认接口 + 错误格式统一
- **范围**：app.py 全端点, schemas.py, api/index.ts, types/index.ts
- **验收**：vue-tsc 无报错；所有端点返回 {code, message, data}；前端无需 _normalize
- **工时**：8h

### 0021-frontend-decompose（Phase B 前端拆分）

- **目标**：ProjectDetail.vue 拆分 + Loading 精细化 + 场景 Tab 交互补全
- **范围**：ProjectDetail.vue → 9 个 Tab 组件 + composable
- **验收**：ProjectDetail.vue < 300 行；所有 Tab 遵循三层结构
- **工时**：8h

### 0022-foreshadow-tracking（Phase C 伏笔系统）

- **目标**：伏笔结构化（id + status） + editor 写回 + 自动修订闭环
- **范围**：outliner.py, editor.py, context_store.py, app.py review 分支
- **验收**：outline.json 含 foreshadow ID；审校后 score<7 自动修订
- **工时**：5h

### 0023-state-unify-persist（Phase D 状态持久化）

- **目标**：废弃 _pipeline_states + TaskRegistry SQLite 持久化 + confirming 超时
- **范围**：task_registry.py, app.py, db/ 新增 task_store.py
- **验收**：重启后未完成任务标记 failed；无双轨状态
- **工时**：8h

---

## 7. 与现有任务包 0011-0017 的差异总结

| 已完成包 | 设计目标 | 实际偏差 |
|----------|----------|----------|
| 0011 TaskRegistry | 统一任务管理 | ⚠️ 老端点绕过 registry，双轨并存 |
| 0012 ContextStore | 跨章节上下文 | ⚠️ **prev_summary 计算了但未传入 writer**，核心功能未生效 |
| 0013 批量正文 | batch + 断点续写 | ✅ 基本达标 |
| 0014 场景 Tab | 场景细纲展示 | ⚠️ 只读无编辑，交互残缺 |
| 0015 逐章审校 | review + 上下文 | ⚠️ 上下文读了但未传入 editor |
| 0016 审校后调整 | revise API | ✅ 基本达标，但无自动修订 |
| 0017 前端任务状态 | useTaskPoller | ✅ 达标 |

**核心教训**：0012 和 0015 的"上下文传递"虽然代码写了，但**接收方签名不匹配**，数据流实际上断了。未来验收必须包含端到端调用链检查，不能只看单模块。

---

## 8. 风险趋势

```
内容闭环 (3.5) ──→ Phase A 后预期 6.0（止血）
流程架构 (5.0)   ──→ Phase B 后预期 7.5（统一状态）
后端契约 (5.5)   ──→ Phase B 后预期 7.5（契约统一）
前端 UI   (6.5)   ──→ Phase B 后预期 8.0（拆分+精细化）

全部 Phase 后综合预期：7.5/10
```

---

_报告合成：墨 (Mo) | 基于四维只读审计 | 2026-05-31_