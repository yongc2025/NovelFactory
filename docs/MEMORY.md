# 项目记忆

> 记录架构决策、踩坑经验、关键上下文。AI 每次启动时读取此文件恢复记忆。

## 架构决策

### 存储层：JSON 文件而非 SQLite
- **决策**：使用 `ProjectStore` 管理 JSON 文件（`data/<project_id>/project.json` 等）
- **原因**：初期快速迭代，JSON 文件直观、易调试
- **代价**：无全文检索、无事务、无并发安全
- **计划**：设计文档中规划了 SQLite + FTS5，尚未迁移

### LLM 网关：三模型路由
- **决策**：`gateway.py` 统一调用，角色自动路由到不同模型
- **模型**：DeepSeek V4 Pro（推理）/ Flash（正文）/ MiMo（备选）
- **映射**：大纲/世界观 → Pro，正文/场景/审校 → Flash
- **注意**：设计文档写的是 DeepSeek-V3/R1，实际用的是 V4 Pro/Flash（火山引擎 Ark API）

### 流水线状态：内存存储
- **决策**：`_pipeline_states` 和 `_stage_states` 是进程内 dict
- **代价**：重启丢失，不支持断点续跑
- **计划**：需要持久化到 project.json 或 SQLite

### 前端：单 store 架构
- **决策**：只用一个 Pinia store（`project.ts`），而非设计文档中的 3 个（project/pipeline/editor）
- **原因**：初期功能简单，单 store 够用
- **代价**：后期功能增多后会臃肿

### API 路由：扁平结构
- **决策**：所有路由在 `app.py` 中，不拆分 routers
- **原因**：初期端点不多，单文件更简单
- **计划**：设计文档规划了 `routers/` 拆分，端点增多后拆分

## 踩坑记录

### Windows PowerShell 编码问题
- PowerShell `Set-Content` 会损坏中文字符（57 处）
- **解决**：永远用 Python + `encoding='utf-8'` 修改含中文的文件

### 流水线状态管理
- 后台异步运行流水线时，状态更新和前端轮询的时序问题
- 需要注意 `_update_state` 和 `_update_stage_state` 的调用时机

### LLM JSON 解析
- DeepSeek 返回的 JSON 可能包裹在 markdown code block 中
- `complete_json()` 已处理 ` ```json ``` ` 包裹的情况

### CORS 配置
- 开发环境需要允许 `localhost:5173` 和 `localhost:3001`
- 已配置 `allow_credentials=True`

## 关键上下文

### 项目定位
- 不是"AI 写小说工具"，是"一个人的 MCN 内容生产线"
- 10 个 AI 角色 = 虚拟编辑部 + 制作部
- 用户只做三件事：选题、审核、发布

### 当前阶段
- 叙事引擎核心已完成（8 阶段 + 9 个 engine 模块）
- Web UI 基础可用（创建/查看/启动流水线）
- 尚未跑通真实端到端生成（需要用户测试验证）

### 技术栈
- 后端：Python 3.11+ + FastAPI + Pydantic
- 前端：Vue 3 + Vite + Ant Design Vue 4.x + Pinia
- LLM：DeepSeek V4 Pro/Flash（火山引擎 Ark）+ MiMo V2.5 Pro（小米）
- 存储：JSON 文件（计划迁移到 SQLite + FTS5）
