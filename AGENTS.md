# NovelFactory AI Agent 操作手册

> **强制引用**: 本项目严格遵循 [d:/workspace/vibe-coding-cn/AGENTS.md](d:/workspace/vibe-coding-cn/AGENTS.md)。
> 在未阅读父级指南前，严禁执行任何实质性操作。

---

## 1. 项目定位

**NovelFactory — 自动化小说工厂**

一个人的内容工厂：从一个想法，到全平台分发的多形态内容。

当前阶段以：
- 叙事引擎（选题→世界观→角色→大纲→正文→审校）
- 多模型调用（DeepSeek V4 Pro/Flash + MiMo）
- 参数化创建（26个创建参数）
- CLI + Web UI
  为核心目标。

当前阶段**不做**：
- 自动发布到平台（先手动发布）
- 多用户/团队协作
- 付费系统

---

## 2. 允许的操作

- 修改 `src/novel_factory/` 下的 Python 代码（必须包含 Type Hints）。
- 修改 `web/src/` 下的 Vue/TypeScript 代码。
- 在 `tasks/` 下创建新的 Task Bundle（CONTEXT/PLAN/ACCEPTANCE/STATUS/TODO）。
- 增量更新 `docs/` 下的文档。
- 接入并维护 `.workflow/auto-dev-loop/` 全自动化开发流程。
- 编写研究、设计、验证类文档。

## 3. 禁止的操作

- 禁止在仓库中提交任何明文 API Key / Secret / Token（使用 .env）。
- 禁止删除或大规模重写 `docs/` 历史记录。
- 禁止在没有任务包与明确验收标准时扩写核心引擎。
- 禁止"顺手重构/大范围改动"除非任务明确要求。

## 4. 黄金路径

- 读取 `tasks/INDEX.md` 锁定当前任务上下文。
- 使用 `tasks` 作为默认自动化开发主流程。
- 每个实质性任务都先创建或更新任务包。
- 先写规格，再写代码，再做验证，再同步进度。

## 5. 技术准则

### 后端 (Python)
- Python 3.11+
- 强制 Type Hints
- Google Style Docstring（中文）
- Ruff lint
- 行宽 120 列
- 异步优先（async/await）

### 前端 (Vue)
- Vue 3 + Vite + TypeScript
- Ant Design Vue 4.x
- Pinia 状态管理
- `<script setup lang="ts">`

### 数据存储
- SQLite + FTS5（结构化数据）
- JSON 文件（项目存储，ProjectStore）

### LLM 调用
- DeepSeek V4 Pro（推理/复杂任务）
- DeepSeek V4 Flash（正文/校审，默认）
- MiMo V2.5 Pro（备选）
- 通过 gateway.py 统一调用，角色自动路由

## 6. 存储架构

```
NovelFactory/
├── src/novel_factory/    # 后端生产代码
│   ├── api/              # FastAPI 路由
│   ├── db/               # 数据层
│   ├── llm/              # LLM 调用层
│   └── engine/           # 叙事引擎（8个AI角色）
├── web/src/              # 前端代码
├── tasks/                # 任务包
├── docs/                 # 项目文档
├── data/                 # SQLite + 项目数据（gitignore）
└── output/               # 生成的小说输出（gitignore）
```

## 7. AI 编辑部（10个角色）

| 角色 | 模型 | 职责 |
|------|------|------|
| 🎯 策划经理 | flash | 选题评估 |
| 🌍 世界观架构师 | pro | 时空背景、核心规则 |
| 👤 角色设计师 | flash | 角色卡、人物弧光 |
| 📋 大纲编剧 | pro | 章节结构、伏笔 |
| 🎬 场景编剧 | flash | 场景级细纲 |
| ✍️ 正文作者 | flash | 正文生成 |
| 🔍 编辑审校 | flash | 规则检查+质量评估 |
| 📝 内容适配师 | flash | 多平台格式转换 |
| 🎬 剧本改编编剧 | flash | 漫剧/短剧剧本 |
| 🎥 漫剧制作人 | — | 分镜+绘图+配音+合成 |
