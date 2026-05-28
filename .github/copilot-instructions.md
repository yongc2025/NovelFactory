# Copilot Instructions — vibe-coding-cn 孵化项目

> 本文件由 vibe-init.sh 自动生成，供 GitHub Copilot 读取。

---

## ⛔ 门禁规则（最高优先级，不可跳过，不可覆盖）

违反任何一条 = 立即停止当前操作，等待用户指令。

1. **禁止问开放性问题**（"你想怎么做？"）→ 必须给 2-4 个选项，标注推荐（✅）和理由
2. **禁止跳过确认** → 严格执行门禁流程：需求确认 → 设计确认 → 任务确认 → 逐个实施 → 测试验证 → 用户验收
3. **禁止一口气写完所有代码** → 每次只做一个任务，完成后等用户确认再继续
4. **禁止在上一步未锁定时进入下一步** → 需求未确认不得做设计，设计未确认不得拆任务，任务未确认不得写代码
5. **禁止跳过测试** → 所有任务完成后必须跑测试，对照需求逐条验收，未通过不得进入验收
6. **禁止未经用户验收就交付** → 输出交付清单，用户确认后才算完成

### 门禁流程（每步产出文件后停下，等用户确认）

```
读 PROJECT_BRIEF.md → 复述理解 → 标模糊点 → 给选项（推荐✅）→ 列默认假设
用户确认 → 需求锁定 → 输出技术方案 → 用户确认 → 产出 docs/DESIGN.md
→ 拆任务 P0/P1/P2 → 用户确认 → 产出 docs/TASKS.md
→ 逐个实施（一次一个，完成即确认）→ 测试验证（跑测试 + 对照需求验收）
→ 用户验收 → 产出 docs/TEST-REPORT.md → 项目完成 🎉
```

**每一步都要停下等用户确认。上一步未锁定 = 下一步禁止开始。**
**测试不通过 = 回去修，不能跳到验收。用户不通过 = 回到对应阶段。**

## 通用规则

1. 先读 .skills/ 下的 SKILL.md 再动手
2. 文档先行，接口先行，实现后补
3. 一次只改一个模块
4. Debug 只给：预期 vs 实际 + 最小复现

## 开发顺序

```
接口定义 → 配置管理 → 核心实现 → 数据集成 → 测试验证
```

## 工作流（必须遵守）

### 启动时（每次对话开始）

1. 读取 `docs/TASKS.md` — 了解当前进度
2. 读取 `docs/MEMORY.md` — 恢复上下文记忆
3. 读取 `docs/PROJECT_BRIEF.md` — 理解项目目标
4. 从 TASKS.md 中第一个未完成任务继续

### 执行时（每个任务）

1. **拆任务**：将 PROJECT_BRIEF.md 拆解为可执行的子任务，写入 `docs/TASKS.md`
2. **打勾**：完成一个任务就标记 `[x]`，附上完成时间和关键决策
3. **记记忆**：重要决策、踩坑经验、架构变更写入 `docs/MEMORY.md`
4. **写代码**：按开发顺序执行，一次只改一个模块

### 中断后恢复

1. 读 TASKS.md → 找到第一个 `[ ]` → 继续
2. 读 MEMORY.md → 恢复之前的决策上下文
3. 不要重新开始，接着上次的进度往下走

### TASKS.md 格式

```markdown
# 任务清单

## 阶段 1：基础架构
- [ ] 定义核心接口
- [ ] 配置管理模块
- [ ] 数据库连接

## 阶段 2：核心功能
- [ ] 功能 A 实现
- [ ] 功能 B 实现

## 已完成
- [x] 项目初始化（2024-01-01）
```

### MEMORY.md 格式

```markdown
# 项目记忆

## 架构决策
- 选择 PostgreSQL 因为需要时序数据支持（2024-01-01）

## 踩坑记录
- API 限流：需要加缓存层

## 关键上下文
- 目标用户：量化交易者
- 核心指标：信号捕获延迟 < 1s
```

## 已加载 Skills

- **canvas-dev**: Canvas白板驱动开发技能：Canvas白板作为唯一真相源，代码是其序列化形式。AI架构总师角色，自动生成富有洞察力的架构图。使用场景：生成架构白板、白板驱动编码、白板驱动重构、Code Review、团队协作、接手遗留项目。
- **ddd-doc-steward**: 
- **headless-cli**: 无头模式 AI CLI 调用技能：支持 Gemini/Claude/Codex CLI 的无交互批量调用，包含 YOLO 模式和安全模式。用于批量翻译、代码审查、多模型编排等场景。
- **postgresql**: PostgreSQL database documentation - SQL queries, database design, administration, performance tuning, and advanced features. Use when working with PostgreSQL databases, writing SQL, or managing database systems.
- **skills-skills**: Claude Skills meta-skill: extract domain material (docs/APIs/code/specs) into a reusable Skill (SKILL.md + references/scripts/assets), and refactor existing Skills for clarity, activation reliability, and quality gates.
- **snapdom**: snapDOM is a fast, accurate DOM-to-image capture tool that converts HTML elements into scalable SVG images. Use for capturing HTML elements, converting DOM to images (SVG, PNG, JPG, WebP), preserving styles, fonts, and pseudo-elements.
- **sop-generator**: 标准作业程序（SOP）生成与规范化：将输入资料/需求/历史记录整理为可执行 SOP（结构化章节、步骤、控制点、异常处理、记录）。当用户要求“写 SOP/作业指导书/操作规程/流程说明”，或给出零散资料需要“整理成 SOP/流程”，或要求“按标准结构输出 SOP/质量检查”时使用。
- **telegram-dev**: Telegram 生态开发全栈指南 - 涵盖 Bot API、Mini Apps (Web Apps)、MTProto 客户端开发。包括消息处理、支付、内联模式、Webhook、认证、存储、传感器 API 等完整开发资源。
