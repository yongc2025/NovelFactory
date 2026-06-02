# NovelFactory — 一个人的自动化小说工厂

> **🤖 AI 注意 (CRITICAL)**：在执行任何任务前，请务必先查阅 [**docs/00_项目入口.md**](docs/00_项目入口.md)。
> 该文档包含项目宪法、AI 人格配置及最新的任务动态。

---

## 🚀 快速启动

1. **环境准备**：
   ```powershell
   # 后端启动 (Python 3.11+)
   python -m uvicorn novel_factory.api.app:app --reload --port 8000

   # 前端启动 (Vue 3/Vite)
   cd web
   npm install
   npm run dev
   ```

2. **从文档开始控制项目**：
   - 打开 [**docs/00_项目入口.md**](docs/00_项目入口.md) 获取全局导航。
   - 打开 [**docs/02_任务看板.md**](docs/02_任务看板.md) 查看当前进度（当前重点：Task 0020 角色一致性修复）。

---

## 📂 项目结构

```text
D:/workspace/NovelFactory
├── docs/                   # 核心文档中枢 (Source of Truth)
│   ├── 00_项目入口.md       # 系统总览与导航
│   ├── 01_项目蓝图.md       # 愿景、痛点与核心流程
│   ├── 02_任务看板.md       # 实时任务状态追踪 (P0/P1/P2)
│   ├── 03_开发决策集.md      # 关键技术决策与踩坑记录
│   ├── 04_架构审计报告.md    # 系统一致性与健康度体检
│   ├── 05_编码规范.md       # Python/Vue 编码及质量准则
│   └── 06_创作方法论.md      # 叙事引擎核心知识库
├── src/                    # 叙事引擎后端 (FastAPI/SQLAlchemy)
├── web/                    # 创作工厂前端 (Vue 3/Ant Design)
├── data/                   # 本地持久化存储 (JSON/SQLite)
├── tasks/                  # 结构化任务包
└── .github/                # AI 门禁与指令规范
```

---

## 🤖 AI 协作准则

本项目采用 **“文档驱动开发”** 模式：
1. **修改前**：必须同步更新 `docs/` 下的对应文档。
2. **执行时**：遵循 `docs/02_任务看板.md` 的步骤，一次只做一个任务。
3. **完成时**：更新 `docs/03_开发决策集.md` 固化上下文记忆。

---

## 🛠️ 技术栈清单

- **后端**: Python / FastAPI / SQLite (FTS5) / DeepSeek API
- **前端**: Vue 3 / Vite / Pinia / Ant Design Vue 4.x
- **角色**: 10 角色分工体系（编剧、场景、正文、审校等）

---

> 当前状态：**紧急止血中**（修复角色名字漂移及管道一致性风险）。
