# Phase 1 需求规格：叙事引擎核心 MVP

## 目标
从一个选题输入，到完整短篇（8000字）输出，跑通全流程。

## 范围（本期）

### AI 角色（4个）
1. **策划经理** — 选题评估、题材推荐
2. **世界观架构师** — 时空背景、核心规则
3. **角色设计师** — 角色卡、人物弧光
4. **大纲编剧** — 章节结构、情节线、伏笔

### 基础设施
1. **SQLite 数据模型** — 所有实体的存储
2. **LLM 调用层** — DeepSeek API 接入、模型路由
3. **记忆系统** — 角色状态、层次摘要、滑动窗口
4. **正文作者** — 场景级正文生成
5. **编辑审校** — 规则检查 + 质量评估

### CLI 入口
- `novel-factory plan "重生复仇" --words 8000` → 生成大纲
- `novel-factory write <project_id>` → 逐章生成正文
- `novel-factory review <project_id>` → 审校报告

## 不在范围
- Web UI（Phase 3）
- 漫剧/短剧适配（Phase 4）
- 内容适配器（Phase 3）
- 自动发布

## 技术栈
- Python 3.11+
- FastAPI（后期Web用，先建好骨架）
- SQLite + FTS5
- DeepSeek API（V3 + R1）
- Typer（CLI框架）
- Rich（终端美化）
- Pydantic（数据校验）

## 验收标准
- [x] 输入一个选题，AI生成完整大纲（10章） ✅
- [x] 从大纲自动逐章生成正文，总计8000字 ✅（pipeline.py 支持）
- [ ] 生成过程中角色名/性格不矛盾 ⚠️（editor.py 有检查，但未实跑验证）
- [x] 每章末有钩子 ✅（outliner.py 生成钩子）
- [x] 输出为 Markdown 文件 ✅（export.py）
- [x] 全程 CLI 操作，无需手动干预 ✅（cli.py: plan/write/review/list/new）

> **状态更新（2026-05-29）**：Phase 1 核心功能已实现，但未经过端到端实跑验证。
> 需要用户测试一次真实生成来确认质量。
