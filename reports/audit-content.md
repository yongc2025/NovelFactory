# 内容生产闭环审计报告

> 审计时间：2026-05-31 | 审计范围：NovelFactory 内容生产闭环 | 样本项目：20260529_231841_d80484（100章）

## 1. 整体评分 + 一句话结论

**整体评分：3.5/10**

**一句话结论**：Prompt 设计框架优秀、风格控制精细，但**闭环断裂**——角色卡不生效、伏笔无追踪、摘要未生成、审校结果未反哺修订，导致100章样本中主角名漂移3次、大纲关键字段（core_event/foreshadow_ops/plot_lines_progress）全部脱轨。

---

## 2. Prompt 设计评价（每阶段简评）

| 阶段 | 评分 | 评价 |
|------|------|------|
| 策划经理 | 8/10 | 字段完整（title/logline/theme/conflict/hook/score/reasoning），JSON Schema 清晰，含市场约束。缺：评分校准标准（1-100无锚点） |
| 世界观 | 9/10 | 七维度覆盖（era/geography/power_system/social_structure/key_locations/rules/constraints），字数约束120-200字/维度。优秀 |
| 角色设计 | 8/10 | 12字段角色卡含 arc_description + twist_point。缺：角色间关系图（仅 relationship_to_protagonist 一个动词） |
| 大纲 | 8/10 | 含 foreshadow_ops + plot_lines_progress + 10章节奏模板。缺：foreshadow_ops 无 ID 字段，无法跨章引用 |
| 场景 | 7/10 | 11字段场景卡，含 character_goals/conflict/turning_point。**严重**：character_states 硬编码为占位符（scene.py:36） |
| 正文 | 7/10 | STYLE_INSTRUCTION + CONTENT_RED_LINES 精细；tone/style_sample/chapter_word_range 参数化注入。**缺**：无强制角色名约束指令 |
| 审校 | 7/10 | 双轮（规则+质量），6维度评估。缺：无"必须使用角色卡中的名字"规则检查；质量评估无修订指令传递 |
| 元数据 | 7/10 | 3级简介/5候选书名/5标签/分类路径。缺：分类匹配未与 CATEGORY_TREE 做校验 |

### Prompt 问题清单

1. **模糊指令**：writer_system 中"适当使用短段落""情绪过渡要自然"——缺少量化标准
2. **缺失关键约束**：writer_user 中没有"必须使用角色卡中的名字，禁止自行创造角色名"的硬约束
3. **foreshadow_ops 无结构**：仅 {action, content}，缺 id/plant_chapter/esolve_chapter，导致无法追踪
4. **无 JSON Schema 强制**：所有 prompt 仅文本描述 JSON 格式，未使用 esponse_format: {"type": "json_object"}

---

## 3. 跨章节连贯性机制评估

### 3.1 ContextStore 摘要机制

**机制**：context_store.py 提供 save_summary/get_recent_summaries，窗口默认3章。

**致命问题**：样本项目 20260529_231841_d80484 的 data/ 目录下**不存在 context/ 目录**，即100章全部生成后，**零条摘要被保存**。

原因分析（app.py:657-669）：
- draft 阶段确实调用了 generate_summary + save_summary
- 但该逻辑在 app.py 的 stage=draft 分支中，而 pipeline.py 的 un_full 路径（用于全自动流程）**不经过此分支**

### 3.2 上下文窗口管理

| 机制 | 实现 | 问题 |
|------|------|------|
| 全局记忆 | memory.py:58 仅角色名+personality+current_state | **current_state 从未被更新** |
| 近期摘要 | get_recent_summaries(window=3) | window=3 对长篇不足；50章后只看3章摘要严重丢失 |
| 滑动窗口 | memory.py:69 取最近2个场景原文 | **writer.py 未调用 build_context()**，滑动窗口硬编码为"无前文" |
| 摘要压缩 | generate_summary(max_words=100) | 100字摘要丢失太多细节；且 app.py 中实际用 150 |

### 3.3 Token 风险

- WRITER_SYSTEM 模板约 1500 字符，含 style_instruction + content_red_lines
- 若 prev_summary 正常注入（3章x150字=450字）+ sliding_window（2场景x~2000字），总计约 6000 字符
- 50+ 章后摘要不压缩，3章窗口尚可控，但若 window 放大到 5+，可能逼近 8K token
- **无分层摘要机制**：缺少"全书摘要->近10章摘要->近3章摘要"的层级结构

---

## 4. 角色/伏笔/世界观一致性追踪能力

### 4.1 角色一致性 — 严重断裂

**实测结果**（样本项目 d80484）：

| 章节 | 主角名 | 出现次数 | 角色卡指定 |
|------|--------|---------|-----------|
| ch01 | 李明 | 35 | 雷恩·温斯特 |
| ch30 | 林夜 | 133 | 雷恩·温斯特 |
| ch50 | 林逸 | 80 | 雷恩·温斯特 |

**角色卡指定主角在100章中0次出现。**

断裂根因链：
1. scene.py:36 — character_states="（暂无角色状态信息）"，场景规划时 LLM 无角色约束
2. scene.py prompt 仅传 characters_present（名字列表），不传角色卡详情
3. writer.py:48-51 — char_info 只取 name/personality/speaking_style，忽略 core_desire/core_fear/fatal_flaw/arc_description
4. writer.py WRITER_SYSTEM 无"必须使用以下角色名"的硬约束
5. pipeline._step_draft() 不传 prev_summary 参数，write_scene 收到空摘要

### 4.2 伏笔追踪 — 形同虚设

- outline.json 的 foreshadow_ops 有 {action, content}，但**无 ID**
- oreshadows 顶层数组在 outline 中存在，但 status 字段**从未被更新**（editor.py:49 读取 f.get('status')，但无代码写入 status）
- 伏笔回收验证：editor 仅检查"前文伏笔是否被遗忘"，但**无法知道哪个伏笔应在哪章回收**
- 实测：样本项目中伏笔 黑油矿脉 和 加密账册 在 ch01 埋设后，后续章节无任何回收

### 4.3 世界观一致性

- outliner 接收世界观摘要（7维度），但 writer **不接收**世界观信息
- worldbuilder 的 constraints 和 rules 仅在 outliner prompt 中出现
- 分批大纲（generate_outline_batch）传 existing_foreshadows，但不传已有章节的事件摘要

---

## 5. 审校->修订闭环有效性

### 5.1 审校流程

- 双轮审校：规则检查（editor_rules）+ 质量评估（editor_quality）
- app.py review 阶段：逐章审校 + 保存到 context_store
- _step_review()（pipeline.py:346）：**仅审校第一章**，其余章节跳过

### 5.2 审校->修订回路

- evise_with_feedback() 存在但需**手动触发**（API /chapters/{num}/revise）
- **无自动修订**：review 阶段完成后不会自动调用 revise
- **review 结果不传递**：revise 的 review_issues 来自 API 请求 body，而非自动从 context_store 读取
- **无质量阈值**：缺少"score < 7 则自动修订"的机制

### 5.3 JSON 解析容错

- 所有模块均有 json.JSONDecodeError 兜底
- 处理了 triple-backtick json markdown 包裹
- editor.py:84-91：解析失败时 checks["character_consistency"] = "待检查"，不中断流程
- **缺**：无重试机制；LLM 返回非法 JSON 时直接降级，无 prompt 修正重试

---

## 6. 关键风险

### P0 — 生产级阻断

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P0-1 | **角色名漂移** | scene.py:36 + writer.py WRITER_SYSTEM | 100章中主角名3次变化，角色卡完全失效 | 1) scene.py 注入角色卡 2) writer_system 加"必须使用以下角色名"硬约束 3) editor_rules 加角色名校验 |
| P0-2 | **摘要未生成** | pipeline.py _step_draft 不传 prev_summary | 长篇无上下文连贯性，writer 收到空摘要 | 1) pipeline._step_draft 传 prev_summary 2) 全流程统一摘要生成入口 |
| P0-3 | **build_context 未被调用** | writer.py 不使用 memory.build_context() | sliding_window 永远是"无前文" | writer.py 内部调用 build_context() 获取三层上下文 |

### P1 — 质量显著影响

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P1-1 | **伏笔无 ID、无状态更新** | outliner foreshadow_ops + editor | 伏笔埋设后无法追踪回收 | 给伏笔加 id + plant_chapter + resolve_chapter + status；editor 写回 status |
| P1-2 | **角色卡字段未传递** | writer.py:48-51 仅取 3 字段 | core_desire/core_fear/fatal_flaw/arc_description 全部浪费 | char_info 扩展到6+字段 |
| P1-3 | **审校不自动修订** | app.py review 阶段 | review 发现问题但不修复 | 加 auto_revise 阈值（score<7 自动修订1轮） |
| P1-4 | **scene 角色状态占位** | scene.py:36 | 场景规划无角色约束，LLM 自行创造 | 传入角色卡摘要 |
| P1-5 | **current_state 永不更新** | memory.py:58 | 角色全局记忆中的"当前状态"永远"未知" | 每章生成后用 LLM 更新角色 current_state |
| P1-6 | **metadata 生成失败无兜底** | 样本项目 metadata.json 仅含 category | 书名/简介/标签全部缺失 | _parse_metadata 加字段补全兜底 |

### P2 — 优化建议

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P2-1 | **无分层摘要** | context_store | 50+ 章后3章窗口不足 | 实现"全书摘要->卷摘要->近3章摘要"层级 |
| P2-2 | **无 response_format** | gateway.py | LLM 可能输出非 JSON | 对结构化输出角色启用 response_format: json_object |
| P2-3 | **无重试机制** | gateway.py/editor.py | JSON 解析失败直接降级 | 加 1-2 次 prompt 修正重试 |
| P2-4 | **_step_review 仅审第1章** | pipeline.py:346-360 | 全自动流程只审1章 | 改为逐章审校 |
| P2-5 | **无重复生成检测** | 无 | 同一章反复重生成成本高 | 加哈希/相似度检测，跳过无变化重生成 |
| P2-6 | **writer 温度 0.85** | writer.py:101 | 正文温度偏高可能导致风格漂移 | 对长篇后段降低温度（如 0.75） |
| P2-7 | **分批大纲缺前文摘要** | outliner.py:generate_outline_batch | 新批次大纲与已有正文脱节 | 传入已有章节摘要 |

---

## 7. 内容质量改进建议（优先级排序）

### 紧急（1-2 天）

1. **修复角色名注入**：在 scene.py 和 writer.py 的 prompt 中加入"必须使用以下角色名：{name_list}，禁止创造新角色名"的硬约束
2. **修复 prev_summary 传递**：pipeline._step_draft 调用 write_scene 时传入 prev_summary
3. **修复 build_context 集成**：writer.py 使用 memory.build_context() 替代硬编码占位符

### 重要（3-5 天）

4. **伏笔系统结构化**：foreshadow_ops 加 id + resolve_chapter；editor 写回 status
5. **角色卡完整传递**：writer char_info 扩展到 core_desire/core_fear/speaking_style/arc_description
6. **自动修订闭环**：review 后 score<7 自动触发 revise_with_feedback
7. **scene.py 注入角色卡**：character_states 传入角色摘要而非占位符

### 改进（1-2 周）

8. **分层摘要机制**：全书摘要（200字）+ 卷摘要（100字/卷）+ 近3章摘要（150字/章）
9. **角色状态追踪**：每章生成后用 LLM 更新角色 current_state
10. **JSON Schema 强制**：对结构化输出角色启用 response_format
11. **LLM 重试机制**：JSON 解析失败后带修正提示重试 1-2 次
12. **metadata 兜底**：生成失败时用 topic.logline 作为 synopsis_short 兜底

### 长期优化

13. **全书一致性校验**：生成完成后做全量角色名/世界观/时间线扫描
14. **重复生成检测**：哈希去重 + 相似度比对，避免无效重生成
15. **温度自适应**：长篇后段降低 writer 温度，减少漂移
16. **敏感词内容审核**：在 editor_rules 中接入敏感词库检查

---

> 审计方法：静态代码分析 + 样本数据（d80484 项目 100 章）验证
> 审计范围：src/novel_factory/llm/prompts.py, engine/{writer,editor,memory,outliner,scene,character,metadata}.py, db/context_store.py, api/app.py, pipeline.py

REPORT: D:\workspace\NovelFactory\reports\audit-content.md
