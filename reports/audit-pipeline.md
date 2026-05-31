# 流程架构审计报告

## 1. 整体评分（1-10）+ 一句话结论

**评分：5/10**

> NovelFactory 的流水线核心骨架已搭建，TaskRegistry 和 ContextStore 的设计意图正确，但存在一个 P0 级数据流断裂（prev_summary 计算了但未传入 writer）、两套并行状态系统互相冲突、以及多处进程内状态导致重启后不可恢复。

---

## 2. 状态机分析

### 2.1 实际状态机（TaskRegistry）

`
pending ──→ running ──→ success
   │           │
   │           ├──────→ failed
   │           │
   └──────→ cancelled  ←── (running)
`

转换表定义于 `task_registry.py:16-20`，终态 success/failed/cancelled 无出边，设计清晰。

### 2.2 隐式状态机（_pipeline_states 内存字典）

`
idle → running → confirming → idle (adopt/regenerate)
                    │
                    ├→ failed
                    └→ 编辑回 idle
`

定义于 `app.py:96-112`，confirming 状态无超时/重试机制。

### 2.3 两套系统冲突

| 维度 | TaskRegistry | _pipeline_states |
|------|-------------|-----------------|
| 存储 | _tasks 字典 | _pipeline_states 字典 |
| 状态 | pending/running/success/failed/cancelled | idle/running/confirming/complete/error |
| 生命周期 | task 级别 | project 级别 |
| confirm | 无概念 | confirming → idle |
| 重启恢复 | 内存 | 内存 |

**风险点：**
1. pipeline_stage 端点同时写入两套系统（app.py:727-729 先 transition 再 _update_state），若 transition 成功但 _update_state 异常，状态不一致。
2. confirming 状态无超时，若前端不回复则永久卡死。
3. 进程重启后所有内存状态丢失，但文件系统数据（topic.json 等）已持久化，导致状态与数据脱节。
---

## 3. TaskRegistry 设计评价

### 3.1 幂等性 OK

submit() (task_registry.py:76-104)：同 project+stage 在跑时返回已有 task，is_new=False。设计正确。

### 3.2 互斥性 部分正确

- 同 project 只能一个 running task —— 内存锁保证 OK
- **但** pipeline_start / pipeline_plan / pipeline_write 三个端点**绕过** TaskRegistry，直接操作 _pipeline_states + _run_in_background，不经过 registry.submit()，不受互斥保护
- 两套系统可以同时运行：registry.submit 拒绝但 _pipeline_states 不拒绝

### 3.3 取消机制 协作式

- cancel() 只设 cancel_requested=True，不主动中断协程
- 执行方需在循环中检查 task.cancel_requested（draft/review 阶段已做 OK）
- **问题**：若当前正在 await LLM 调用，cancel 要等 LLM 返回后才能生效，可能数分钟延迟
- 无 cancel 超时兜底

### 3.4 状态转换原子性 OK

transition() 受 asyncio.Lock 保护，单点写入。终态自动释放 _running 互斥。

### 3.5 缺失

- 无 GET /api/pipeline/tasks 列表端点（只能按 task_id 查单个）
- 无任务 TTL/过期清理，_tasks 字典无限增长
- 无持久化，进程重启全部丢失

---

## 4. ContextStore 评价

### 4.1 存储模型

文件结构清晰（context/ch{N}_summary.md + context/ch{N}_review.json），实现仅 77 行，简洁。

### 4.2 P0: prev_summary 计算了但未使用

app.py:657 读取了 prev_summary = ctx_store.get_recent_summaries(...)，但紧接着 app.py:661：

    draft = await pipeline._step_draft(project_id, ch, single_scene, characters, params)

_step_draft 签名 (project_id, chapter, scene, characters, params) 没有 prev_summary 参数。
writer.write_scene() 接受 prev_summary='' 但 pipeline 层从未传入。

**结论：跨章节上下文完全失效。每章写作如同无前文，是最大质量隐患。**

### 4.3 摘要失效/重建

- 无失效标记：大纲修改后摘要不会自动重建
- 无版本号：无法判断摘要是否对应最新正文
- 摘要生成失败仅 warning，不影响主流程（合理），但跳过后下一章取到的 prev_summary 可能为空

### 4.4 window=3 硬编码

get_recent_summaries 默认 window=3，对长篇小说（50+ 章）可能不足，且不可配置。

---

## 5. 关键风险

### P0-1: prev_summary 未传入 writer（数据流断裂）
- **现象**：每章生成无前文上下文
- **位置**：app.py:657-661、pipeline.py:335
- **影响**：角色名不一致、情节重复、矛盾；这是生成质量的核心问题
- **建议**：_step_draft 增加 prev_summary 参数，透传到 write_scene()

### P0-2: 两套状态系统并存，互斥失效
- **现象**：pipeline_start / pipeline_plan / pipeline_write 绕过 TaskRegistry
- **位置**：app.py:488-557（三个老端点）
- **影响**：可同时触发同一 project 的多个任务，产生竞态写文件
- **建议**：统一走 TaskRegistry，废弃 _pipeline_states 或仅作只读视图

### P0-3: 进程重启状态全丢
- **现象**：所有任务状态、pipeline 进度存内存
- **位置**：task_registry.py:64-65、app.py:96-97
- **影响**：重启后无法恢复进行中的任务，已生成数据与状态脱节
- **建议**：TaskRegistry 持久化到 SQLite；pipeline 状态从文件系统重建

### P1-1: confirming 状态无超时
- **现象**：阶段完成后进入 confirming 等待用户确认，无超时兜底
- **位置**：app.py:727-729
- **影响**：前端断线/不响应 → 项目永久卡在 confirming
- **建议**：加 confirm_timeout（如 30min），超时自动设为 idle

### P1-2: _run_in_background 创建新事件循环
- **现象**：_run_in_background 在线程池中创建新 event loop 运行协程
- **位置**：app.py:474-479
- **影响**：与主事件循环隔离，asyncio.Lock 不跨线程有效；registry.lock 在子线程中可能失效
- **建议**：改用 asyncio.create_task + BackgroundTasks，或使用 loop.run_in_executor

### P1-3: review 批量不跳过已审校章节
- **现象**：draft 阶段有 existing and not force -> skip，review 阶段只检查 draft 是否存在
- **位置**：app.py:688-691
- **影响**：重复审校浪费 token；已有审校结果被覆盖
- **建议**：review 阶段也加 if ctx_store.get_chapter_review(...) and not force: skip

### P1-4: scene 阶段不检查 cancel
- **现象**：draft/review 阶段循环检查 task.cancel_requested，scene 阶段不检查
- **位置**：app.py:624-631
- **影响**：scene 阶段无法取消
- **建议**：加 cancel 检查

### P1-5: review_chapter 不接收 prev_summary/prev_issues
- **现象**：app.py:697-704 计算 prev_summary 和 prev_issues 但 review_chapter() 签名不接受
- **位置**：app.py:706、editor.py:23
- **影响**：审校上下文同样失效，与 P0-1 同因
- **建议**：review_chapter 增加 prev_summary、prev_issues 参数并在 prompt 里使用

### P2-1: _tasks 字典无清理
- **现象**：已完成任务永不清理
- **位置**：task_registry.py:64
- **影响**：长期运行内存泄漏
- **建议**：定期清理 N 小时前的终态任务

### P2-2: 摘要与正文无版本关联
- **现象**：正文被 revise 后摘要更新，但无版本号关联
- **位置**：context_store.py 全文
- **影响**：无法判断摘要是否过期
- **建议**：摘要文件头部加注释 based_on / generated_at

### P2-3: world 格式双重标准
- **现象**：后端返回 [{category, content}]，前端期望 {era, geography, ...}，需 _normalize_world 转换
- **位置**：app.py:838-867
- **影响**：新增世界观字段时两端需同步维护映射表
- **建议**：统一为一个 schema

---

## 6. 与任务包 0011-0017 设计的差异

| 任务包 | 设计要求 | 实际代码 | 偏差 |
|--------|---------|---------|------|
| 0011 | GET /api/pipeline/tasks/{task_id} | OK app.py:1594 | — |
| 0011 | POST /api/pipeline/tasks/{task_id}/cancel | OK app.py:1603 | 仅协作式取消 |
| 0011 | pipeline_stage 返回 task_id | 部分：返回 task_id + message 混合 | 比设计多了 message 字段 |
| 0011 | 移除手动 _update_state | 否：未废弃 | **两套系统并存** |
| 0012 | 正文生成后自动生成摘要 | OK app.py:668-670 | — |
| 0012 | 下一章 prev_summary 非空 | **否：计算了但未传入** | **核心偏差 P0** |
| 0013 | 断点续写跳过已有正文 | OK app.py:654-656 | — |
| 0013 | 取消功能 | 部分：仅协作式 | 需等 LLM 返回 |
| 0013 | 批量最多 10 章 | OK app.py:610 min(batch_size, 10) | — |
| 0013 | 章节间 prev_summary 非空 | **否：同 0012 缺陷** | 与 0012 关联 |
| 0014 | scene tab | 未审计前端 | — |
| 0015 | 逐章审校+上下文 | 部分：app.py:682-716 读了 prev 但未传给 editor | 同类 bug |
| 0015 | 批量审校接入 TaskRegistry | OK 通过 pipeline_stage 走 registry | — |
| 0015 | 审校跳过已审章节 | 否：未实现 | 重复审校 |
| 0016 | revise 端点 | OK app.py:1392-1420 | — |
| 0016 | revise 后摘要重新生成 | OK app.py:1411-1416 | — |
| 0016 | 4 个操作按钮 | 未审计前端 | — |
| 0017 | useTaskPoller | OK 已完成（ACCEPTANCE 全打勾） | — |

---

## 7. 改进建议（优先级排序）

### 立即修复（P0）

1. **修复 prev_summary 传递链**（1h）
   - pipeline._step_draft 增加 prev_summary: str = '' 参数
   - _step_draft 内传给 write_scene(prev_summary=prev_summary)
   - app.py:661 传入 prev_summary
   - review 阶段同步：editor.review_chapter 增加 prev_summary / prev_issues 参数
   - **影响：直接决定跨章节连贯性与审校上下文准确性**

2. **统一状态管理**（4h）
   - pipeline_start / plan / write 改用 registry.submit()
   - _pipeline_states 降级为只读缓存视图
   - 或直接废弃，pipeline status 从 registry + 文件系统重建

3. **TaskRegistry 持久化**（6h）
   - 持久化到 SQLite（复用 db/connection.py）
   - 启动时从 DB 恢复未完成任务
   - 标记 running -> failed（crash recovery）

### 近期修复（P1）

4. **修复 _run_in_background 事件循环问题**（2h）
   - 改用 asyncio.create_task 替代线程池+新事件循环
   - 或用 loop.run_in_executor 包装同步部分

5. **confirming 超时机制**（1h）
   - 加 confirmed_at 时间戳
   - 启动时扫描超过 30min 的 confirming -> 重置为 idle

6. **review 阶段跳过已审章节**（0.5h）
   - if ctx_store.get_chapter_review(project_id, ch_num) and not force: continue

7. **scene 阶段加 cancel 检查**（0.5h）

### 后续优化（P2）

8. **_tasks 定期清理** —— 终态任务 24h 后清理
9. **摘要版本标记** —— 正文修改后标记摘要需重建
10. **world 格式统一** —— 去掉 _normalize_world，engine 直接输出 dict
11. **window 可配置** —— ContextStore.get_recent_summaries 的 window 由 params 传入
12. **任务列表端点** —— GET /api/pipeline/tasks?project_id=xxx

---

_审计时间：2026-05-31 | 审计范围：src/novel_factory/ 静态分析_

REPORT: D:\workspace\NovelFactory\reports\audit-pipeline.md
