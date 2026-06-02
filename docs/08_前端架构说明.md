# NovelFactory 前端技术方案

> 版本: v1.0 | 日期: 2026-05-28 | 作者: 墨 (Frontend Architect Subagent)
> 2026-05-29 | 补充实现状态追踪

---

## 📊 实现状态总览

| 模块 | 设计状态 | 实现状态 | 偏差说明 |
|------|---------|---------|----------|
| 技术选型 | Vue3+Vite+AntDesign+Pinia | ✅ 一致 | 无 TailwindCSS |
| 路由设计 | 10+ 路由 | **3 个路由** | Dashboard/ProjectCreate/ProjectDetail |
| API 层 | 分文件 client/project/pipeline/... | **单文件 api/index.ts** | 未拆分 |
| 状态管理 | 3 个 store | **1 个 store** | 只有 project.ts |
| WebSocket | 设计完成 | **❌ 未实现** | 使用轮询 |
| 项目列表 | ProjectCard + 筛选 | ✅ 基础版 | 无筛选 |
| 项目创建 | 5 步 Tab 向导 | ✅ 完成 | 26 个参数 |
| 大纲编辑器 | 树形+拖拽+详情面板 | **基础版** | 无拖拽，无详情面板 |
| 章节列表 | Table + 批量操作 | ⚠️ 部分 | 在 ProjectDetail 中 |
| 正文阅读器 | 阅读+编辑模式 | **只读模式** | 无编辑器 |
| 角色管理 | 卡片+关系图+CRUD | ⚠️ 基础版 | 无关系图 |
| 世界观设定 | 卡片+编辑抽屉 | ⚠️ 基础版 | — |
| 审校报告 | 评分+问题列表+对比视图 | **基础版** | 无对比视图 |
| 流水线控制台 | 时间线+日志流+控制 | **基础版** | 无日志流，用轮询 |
| 导出管理 | 格式选择+预览 | **❌ 未实现** | 只有后端 Markdown 导出 |
| 全局设置 | LLM 配置 | **❌ 未实现** | — |
| 角色关系图 | ECharts 力导向图 | **❌ 未实现** | — |

---

## 1. 现状分析

### 现有后端结构

```
NovelFactory/
├── src/novel_factory/
│   ├── cli.py              # Typer CLI 入口
│   ├── pipeline.py         # 流水线编排器（7 个阶段）
│   ├── export.py           # 导出模块
│   ├── config.py           # 配置
│   ├── db/
│   │   ├── models.py       # DDL（projects, chapters, scenes, characters...）
│   │   ├── schema.py       # SQLite schema
│   │   └── project_store.py # 文件系统 JSON 存储（实际存储层）
│   ├── engine/
│   │   ├── planner.py      # 选题评估
│   │   ├── worldbuilder.py # 世界观搭建
│   │   ├── character.py    # 角色设计
│   │   ├── outliner.py     # 大纲编剧
│   │   ├── scene.py        # 场景细纲
│   │   ├── writer.py       # 正文生成
│   │   ├── editor.py       # 编辑审校
│   │   └── memory.py       # 上下文记忆
│   └── llm/
│       ├── gateway.py      # LLM 调用网关
│       └── prompts.py      # Prompt 模板
├── data/                   # 项目数据（JSON 文件系统）
│   ├── projects.json       # 项目索引
│   └── <project_id>/
│       ├── project.json
│       ├── world.json
│       ├── characters.json
│       ├── outline.json
│       ├── scenes/ch01.json
│       ├── drafts/ch01.md
│       └── review.json
└── output/                 # 导出文件
```

### 关键发现

| 发现 | 影响 |
|------|------|
| **存储层是文件系统 JSON，非 SQLite** | API 层直接读写 JSON 文件即可，无需 ORM |
| **Pipeline 是 async** | FastAPI 天然兼容，WebSocket 推送进度很自然 |
| **无现有 API 层** | 需要从零构建 REST API + WebSocket |
| **7 阶段流水线** | 每个阶段需要独立 API 端点 + 进度推送 |
| **LLM 调用是异步的** | 生成任务需要后台任务队列 + 进度回调 |

---

## 2. 技术选型

### 推荐方案：Vue 3 + Vite + Ant Design Vue

```
┌─────────────────────────────────────────────────────┐
│                    推荐方案                          │
├─────────────────────────────────────────────────────┤
│  框架:     Vue 3 (Composition API + <script setup>) │
│  构建:     Vite 6                                   │
│  语言:     TypeScript                                │
│  UI 库:    Ant Design Vue 4.x                       │
│  状态:     Pinia                                    │
│  路由:     Vue Router 4                             │
│  HTTP:     Axios                                    │
│  样式:     TailwindCSS 3 + Ant Design 变量覆盖      │
│  Markdown: markdown-it + @vueup/vue-quill           │
│  图表:     ECharts (角色关系图)                      │
│  拖拽:     vuedraggable (SortableJS)                │
└─────────────────────────────────────────────────────┘
```

### 选型对比

| 维度 | Vue 3 + Vite | React + Next.js | Streamlit/Gradio |
|------|-------------|-----------------|------------------|
| **开发效率** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **中文生态** | ⭐⭐⭐⭐⭐ (Ant Design Vue) | ⭐⭐⭐⭐ (Ant Design React) | ⭐⭐⭐ |
| **复杂交互** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **自定义程度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **后期扩展** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **学习成本** | ⭐⭐⭐⭐ (你熟悉) | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **SSR 需求** | 不需要 (SPA) | Next.js 过重 | N/A |

### 为什么选 Vue 3 + Ant Design Vue？

1. **你是个人创作者**：不需要 Next.js 的 SSR/SEO，SPA 足够
2. **中文生态最强**：Ant Design Vue 文档完善，组件丰富，表格/表单/树组件开箱即用
3. **复杂编辑器场景**：大纲树、拖拽排序、富文本编辑 — Vue 3 的 Composition API 处理这类逻辑很清晰
4. **后期开放**：如果别人也要用，Vue 3 的学习曲线比 React 平缓
5. **Ant Design Pro Vue**：有现成的后台管理模板，可以快速搭建布局

### 后端补充

```
后端新增:
├── api/
│   ├── main.py            # FastAPI app 入口
│   ├── routers/
│   │   ├── projects.py    # 项目 CRUD
│   │   ├── pipeline.py    # 流水线控制
│   │   ├── chapters.py    # 章节管理
│   │   ├── characters.py  # 角色管理
│   │   └── export.py      # 导出
│   ├── ws/
│   │   └── progress.py    # WebSocket 进度推送
│   ├── schemas/
│   │   └── *.py           # Pydantic 模型
│   └── deps.py            # 依赖注入
```

---

## 3. 前端架构设计

### 3.1 状态管理 — Pinia

```typescript
// stores/project.ts
export const useProjectStore = defineStore('project', () => {
  // ── State ──
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  // ── Getters ──
  const activeProjects = computed(() =>
    projects.value.filter(p => p.status !== 'complete')
  )

  // ── Actions ──
  async function fetchProjects() { ... }
  async function fetchProject(id: string) { ... }
  async function createProject(data: CreateProjectInput) { ... }
  async function deleteProject(id: string) { ... }
})
```

```typescript
// stores/pipeline.ts — 流水线状态（WebSocket 驱动）
export const usePipelineStore = defineStore('pipeline', () => {
  const currentStage = ref<string>('')
  const progress = ref<Record<string, StageProgress>>({})
  const logs = ref<PipelineLog[]>([])
  const isRunning = ref(false)

  // WebSocket 连接管理
  function connectWs(projectId: string) { ... }
  function disconnectWs() { ... }
})
```

```typescript
// stores/editor.ts — 编辑器状态
export const useEditorStore = defineStore('editor', () => {
  const outline = ref<OutlineData | null>(null)
  const characters = ref<Character[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const reviewReport = ref<ReviewReport | null>(null)
})
```

### 3.2 API 对接层

```typescript
// api/client.ts — Axios 实例
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 30000,
})

// 请求/响应拦截器
client.interceptors.response.use(
  res => res.data,
  err => {
    // 统一错误处理：message.error()
    return Promise.reject(err)
  }
)
```

```typescript
// api/project.ts — 项目相关 API
export const projectApi = {
  list: () => client.get('/api/projects'),
  get: (id: string) => client.get(`/api/projects/${id}`),
  create: (data: CreateProjectInput) => client.post('/api/projects', data),
  update: (id: string, data: Partial<Project>) => client.patch(`/api/projects/${id}`, data),
  delete: (id: string) => client.delete(`/api/projects/${id}`),
}
```

```typescript
// api/pipeline.ts — 流水线 API
export const pipelineApi = {
  // 启动完整流水线
  runFull: (projectId: string, params: PipelineParams) =>
    client.post(`/api/projects/${projectId}/pipeline/full`, params),

  // 只生成大纲
  planOnly: (projectId: string, params: PlanParams) =>
    client.post(`/api/projects/${projectId}/pipeline/plan`, params),

  // 从大纲生成正文
  writeFromOutline: (projectId: string) =>
    client.post(`/api/projects/${projectId}/pipeline/write`),

  // 运行审校
  review: (projectId: string) =>
    client.post(`/api/projects/${projectId}/pipeline/review`),

  // 获取流水线状态
  getStatus: (projectId: string) =>
    client.get(`/api/projects/${projectId}/pipeline/status`),
}
```

### 3.3 WebSocket 进度推送

```typescript
// composables/usePipelineWs.ts
export function usePipelineWs(projectId: Ref<string>) {
  const ws = ref<WebSocket | null>(null)
  const pipelineStore = usePipelineStore()

  function connect() {
    const url = `ws://localhost:8000/ws/pipeline/${projectId.value}`
    ws.value = new WebSocket(url)

    ws.value.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      switch (msg.type) {
        case 'stage_start':
          pipelineStore.currentStage = msg.stage
          break
        case 'stage_progress':
          pipelineStore.progress[msg.stage] = msg.data
          break
        case 'stage_complete':
          pipelineStore.progress[msg.stage] = { ...msg.data, done: true }
          break
        case 'log':
          pipelineStore.logs.push(msg.data)
          break
        case 'error':
          // 错误处理
          break
        case 'pipeline_complete':
          pipelineStore.isRunning = false
          break
      }
    }
  }

  onMounted(() => { if (projectId.value) connect() })
  onUnmounted(() => ws.value?.close())

  return { connect, disconnect: () => ws.value?.close() }
}
```

---

## 4. 路由设计

> **实际实现**：仅 3 个路由（Dashboard / ProjectCreate / ProjectDetail），远少于设计。

### 设计路由（完整）

```
/                                    → 重定向到 /projects
/projects                            → 项目列表（首页 Dashboard）
/projects/:id                        → 项目详情概览
/projects/:id/outline                → 大纲编辑器
/projects/:id/chapters               → 章节列表
/projects/:id/chapters/:num          → 章节正文阅读/编辑
/projects/:id/characters             → 角色管理
/projects/:id/world                  → 世界观设定
/projects/:id/review                 → 审校报告
/projects/:id/pipeline               → 流水线控制台（实时进度）
/projects/:id/export                 → 导出管理
/projects/:id/publish                → 发布管理（后期）
/settings                            → 全局设置（LLM 配置等）
```

### 实际路由

```typescript
// router/index.ts — 实际实现
const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard },           // 项目列表
  { path: '/project/create', component: ProjectCreate },  // 创建向导
  { path: '/project/:id', component: ProjectDetail },     // 项目详情（所有数据在一个页面）
]
```

### 偏差说明
- 所有项目数据（topic/world/characters/outline/chapters/review）都放在 ProjectDetail 页面中
- 未拆分为独立路由页面
- 无大纲编辑器、正文阅读器等独立页面

```typescript
// router/index.ts
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/projects',
  },
  {
    path: '/projects',
    component: BasicLayout,
    children: [
      { path: '', name: 'ProjectList', component: () => import('@/views/projects/ProjectList.vue') },
      {
        path: ':id',
        component: ProjectLayout,  // 项目内侧边栏布局
        children: [
          { path: '', name: 'ProjectDetail', component: () => import('@/views/project/ProjectDetail.vue') },
          { path: 'outline', name: 'Outline', component: () => import('@/views/project/OutlineEditor.vue') },
          { path: 'chapters', name: 'Chapters', component: () => import('@/views/project/ChapterList.vue') },
          { path: 'chapters/:num', name: 'ChapterDetail', component: () => import('@/views/project/ChapterReader.vue') },
          { path: 'characters', name: 'Characters', component: () => import('@/views/project/CharacterManager.vue') },
          { path: 'world', name: 'WorldSettings', component: () => import('@/views/project/WorldSettings.vue') },
          { path: 'review', name: 'Review', component: () => import('@/views/project/ReviewReport.vue') },
          { path: 'pipeline', name: 'Pipeline', component: () => import('@/views/project/PipelineConsole.vue') },
          { path: 'export', name: 'Export', component: () => import('@/views/project/ExportManager.vue') },
        ],
      },
    ],
  },
  { path: '/settings', name: 'Settings', component: () => import('@/views/Settings.vue') },
]
```

---

## 5. API 接口设计

### 5.1 项目管理

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects` | 项目列表 | - | `Project[]` |
| `POST` | `/api/projects` | 创建项目 | `{title, inspiration, genre?, target_words?}` | `Project` |
| `GET` | `/api/projects/{id}` | 项目详情 | - | `Project` |
| `PATCH` | `/api/projects/{id}` | 更新项目 | `Partial<Project>` | `Project` |
| `DELETE` | `/api/projects/{id}` | 删除项目 | - | `204` |
| `GET` | `/api/projects/{id}/stats` | 项目统计 | - | `{chapters, words, progress}` |

### 5.2 流水线控制

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `POST` | `/api/projects/{id}/pipeline/full` | 完整流水线 | `{genre_hint?, target_words?}` | `{task_id}` |
| `POST` | `/api/projects/{id}/pipeline/plan` | 只生成大纲 | `{genre_hint?, target_chapters?}` | `{task_id}` |
| `POST` | `/api/projects/{id}/pipeline/write` | 从大纲生成正文 | - | `{task_id}` |
| `POST` | `/api/projects/{id}/pipeline/review` | 运行审校 | - | `{task_id}` |
| `POST` | `/api/projects/{id}/pipeline/stage/{stage}` | 运行单个阶段 | `{params?}` | `{task_id}` |
| `GET` | `/api/projects/{id}/pipeline/status` | 流水线状态 | - | `PipelineStatus` |
| `POST` | `/api/projects/{id}/pipeline/cancel` | 取消流水线 | - | `200` |

### 5.3 大纲管理

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects/{id}/outline` | 获取大纲 | - | `OutlineData` |
| `PUT` | `/api/projects/{id}/outline` | 更新大纲 | `OutlineData` | `OutlineData` |
| `PATCH` | `/api/projects/{id}/outline/chapters/{num}` | 更新单章大纲 | `Partial<Chapter>` | `Chapter` |
| `POST` | `/api/projects/{id}/outline/chapters` | 新增章节 | `ChapterCreate` | `Chapter` |
| `DELETE` | `/api/projects/{id}/outline/chapters/{num}` | 删除章节 | - | `204` |
| `PUT` | `/api/projects/{id}/outline/reorder` | 章节排序 | `{chapters: {num, sort_order}[]}` | `200` |

### 5.4 章节 & 正文

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects/{id}/chapters` | 章节列表 | - | `ChapterSummary[]` |
| `GET` | `/api/projects/{id}/chapters/{num}` | 章节详情（含正文） | - | `ChapterDetail` |
| `PATCH` | `/api/projects/{id}/chapters/{num}` | 更新章节正文 | `{draft: string}` | `ChapterDetail` |
| `GET` | `/api/projects/{id}/chapters/{num}/scenes` | 场景细纲 | - | `Scene[]` |
| `PUT` | `/api/projects/{id}/chapters/{num}/scenes` | 更新场景细纲 | `Scene[]` | `Scene[]` |

### 5.5 角色管理

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects/{id}/characters` | 角色列表 | - | `Character[]` |
| `POST` | `/api/projects/{id}/characters` | 新增角色 | `CharacterCreate` | `Character` |
| `PATCH` | `/api/projects/{id}/characters/{char_id}` | 更新角色 | `Partial<Character>` | `Character` |
| `DELETE` | `/api/projects/{id}/characters/{char_id}` | 删除角色 | - | `204` |
| `GET` | `/api/projects/{id}/characters/relations` | 角色关系图 | - | `RelationGraph` |

### 5.6 世界观

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects/{id}/world` | 世界观设定 | - | `WorldSettings` |
| `PUT` | `/api/projects/{id}/world` | 更新世界观 | `WorldSettings` | `WorldSettings` |

### 5.7 审校 & 导出

| Method | Endpoint | 说明 | Request Body | Response |
|--------|----------|------|-------------|----------|
| `GET` | `/api/projects/{id}/review` | 审校报告 | - | `ReviewReport` |
| `POST` | `/api/projects/{id}/review` | 重新审校 | - | `{task_id}` |
| `GET` | `/api/projects/{id}/export` | 导出列表 | - | `ExportFile[]` |
| `POST` | `/api/projects/{id}/export` | 生成导出 | `{format: 'txt'\|'epub'\|'pdf'}` | `ExportFile` |
| `GET` | `/api/projects/{id}/export/{file_id}/download` | 下载导出文件 | - | `File` |

### 5.8 全局

| Method | Endpoint | 说明 |
|--------|----------|------|
| `GET` | `/api/settings` | 获取全局设置 |
| `PUT` | `/api/settings` | 更新全局设置 |
| `GET` | `/api/health` | 健康检查 |

### 5.9 WebSocket

```
WS /ws/pipeline/{project_id}

服务端推送消息格式:
{
  "type": "stage_start" | "stage_progress" | "stage_complete" | "log" | "error" | "pipeline_complete",
  "stage": "topic" | "world" | "character" | "outline" | "scene" | "draft" | "review",
  "data": { ... },
  "timestamp": "2026-05-28T20:00:00Z"
}
```

---

## 6. 核心页面组件设计

### 6.1 组件树总览

```
App
├── BasicLayout (Ant Design Pro Layout)
│   ├── Header
│   │   ├── Logo
│   │   ├── NavMenu
│   │   └── UserActions (Settings)
│   └── Content (router-view)
│
├── ProjectList (首页 Dashboard)
│   ├── ProjectCard[]
│   ├── CreateProjectModal
│   └── ProjectFilter (genre, status)
│
├── ProjectLayout (项目内布局)
│   ├── ProjectSider (项目导航)
│   │   ├── ProjectInfo (标题、状态、进度)
│   │   └── ProjectMenu (大纲/章节/角色/世界观/审校/流水线/导出)
│   └── Content (router-view)
│
│   ├── ProjectDetail (概览)
│   │   ├── StageProgressCard (7 阶段进度条)
│   │   ├── StatsCards (章节数/字数/角色数)
│   │   ├── RecentActivity
│   │   └── QuickActions (一键生成/继续写作)
│   │
│   ├── OutlineEditor (大纲编辑器)
│   │   ├── OutlineToolbar (添加/折叠/展开/筛选)
│   │   ├── ChapterTree (树形结构，可拖拽)
│   │   │   └── ChapterTreeNode
│   │   │       ├── ChapterHeader (编号 + 标题 + 状态标签)
│   │   │       ├── ChapterMeta (情感位置/钩子/出场角色)
│   │   │       └── InlineEdit (双击编辑)
│   │   └── ChapterDetailPanel (右侧详情面板)
│   │       ├── ChapterForm (标题/核心事件/情感弧线)
│   │       ├── SceneList (场景列表)
│   │       └── ForeshadowTags (伏笔标记)
│   │
│   ├── ChapterList (章节列表)
│   │   ├── ChapterTable (Ant Design Table)
│   │   │   columns: 编号, 标题, 字数, 状态, 操作
│   │   └── BatchActions (批量生成/批量审校)
│   │
│   ├── ChapterReader (章节正文)
│   │   ├── ChapterNav (上一章/下一章 + 章节选择)
│   │   ├── ReadingMode (纯阅读，Markdown 渲染)
│   │   ├── EditMode (富文本编辑器 / Markdown 编辑器)
│   │   ├── ScenePanel (场景细纲侧栏)
│   │   └── WordCountBar (字数统计)
│   │
│   ├── CharacterManager (角色管理)
│   │   ├── CharacterCardGrid (卡片式展示)
│   │   │   └── CharacterCard
│   │   │       ├── Avatar
│   │   │       ├── Name + Role
│   │   │       ├── PersonalityTags
│   │   │       └── QuickStats (核心欲望/恐惧/秘密)
│   │   ├── CharacterDetailDrawer (抽屉式详情)
│   │   │   ├── BasicInfo
│   │   │   ├── PersonalitySection (表面/深层/欲望/恐惧)
│   │   │   ├── ArcSection (人物弧线)
│   │   │   └── RelationList (与其他角色的关系)
│   │   └── RelationGraph (ECharts 力导向图)
│   │
│   ├── WorldSettings (世界观设定)
│   │   ├── WorldCardList (分类卡片: 时空/势力/规则)
│   │   └── WorldEditDrawer
│   │
│   ├── ReviewReport (审校报告)
│   │   ├── ReviewSummary (总分/总字数/问题数)
│   │   ├── IssueList (问题分类列表)
│   │   │   └── IssueItem
│   │   │       ├── SeverityTag (严重/中等/轻微)
│   │   │       ├── CategoryTag (角色一致性/时间线/伏笔...)
│   │   │       └── Description
│   │   └── CompareView (原文 vs 建议修改对比)
│   │       ├── OriginalText (左侧)
│   │       └── SuggestedText (右侧)
│   │
│   ├── PipelineConsole (流水线控制台)
│   │   ├── PipelineControls (启动/暂停/取消)
│   │   ├── StageTimeline (7 阶段时间线)
│   │   │   └── StageNode (状态: pending/running/done/error)
│   │   ├── ProgressDetail (当前阶段详细进度)
│   │   └── LogStream (实时日志流)
│   │
│   └── ExportManager (导出管理)
│       ├── ExportFormatSelector (TXT/EPUB/PDF)
│       ├── ExportPreview
│       └── ExportHistory
│
└── Settings (全局设置)
    ├── LLMConfig (模型选择/API Key)
    └── GeneralConfig
```

### 6.2 大纲编辑器 — 详细设计

```
┌─────────────────────────────────────────────────────────┐
│ [+] 添加章节  [▼] 折叠全部  [▶] 展开全部  🔍 搜索      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─ 📖 第1章: 重生之夜 ───────────── [铺垫] [✓已生成]  │
│  │   核心事件: 主角重生回到三年前                         │
│  │   钩子: 发现前世的仇人竟是...                         │
│  │                                                      │
│  ├─ 📖 第2章: 暗流涌动 ───────────── [铺垫] [⏳生成中]  │
│  │   核心事件: 主角开始布局                               │
│  │                                                      │
│  ├─ 📖 第3章: 第一次交锋 ─────────── [过渡] [○待生成]   │
│  │   核心事件: 与反派首次正面冲突                         │
│  │                                                      │
│  ├─ 📖 第4章: ...                  ── [过渡] [○待生成]   │
│  │                                                      │
│  └─ 📖 第10章: 最终对决 ─────────── [高潮] [○待生成]    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 右侧详情面板 (选中章节时展开):                           │
│ ┌─────────────────────────────────┐                     │
││ 编辑章节大纲                       │                     │
││ 标题: [重生之夜              ]     │                     │
││ 核心事件: [                    ]   │                     │
││ 情感位置: [铺垫 ▼]                 │                     │
││ 钩子: [                         ]  │                     │
││ 出场角色: [主角] [反派] [+]        │                     │
││ 伏笔: [前世的信物 → 第8章揭晓]     │                     │
││                                    │                     │
││ 场景列表:                          │                     │
││  1. 医院病房 - 主角醒来            │                     │
││  2. 手机查看日期 - 确认重生        │                     │
││                                    │                     │
││ [保存] [重新生成本章大纲]          │                     │
│└────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

**交互要点:**

- **拖拽排序**: 使用 `vuedraggable` 实现章节拖拽，排序后调用 `PUT /api/projects/{id}/outline/reorder`
- **内联编辑**: 双击章节标题进入编辑模式，失焦或 Enter 保存
- **状态标签**: 颜色区分 — 灰色(待生成) / 蓝色(生成中) / 绿色(已生成) / 红色(有错误)
- **情感位置**: 用颜色条表示 — 铺垫(蓝) / 过渡(黄) / 高潮(红) / 结局(紫)

### 6.3 正文阅读器 — 详细设计

```
┌─────────────────────────────────────────────────────────┐
│ ← 第1章  第2章: 暗流涌动  第3章 →        [📖阅读] [✏编辑] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  # 第2章: 暗流涌动                                       │
│                                                         │
│  清晨的阳光透过窗帘缝隙洒进来，林远睁开眼睛，             │
│  昨晚的记忆如潮水般涌来。他知道，从今天开始，             │
│  一切都将不同。                                          │
│                                                         │
│  "你醒了？"门外传来母亲的声音，带着几分小心翼翼。         │
│                                                         │
│  林远深吸一口气，压下心中的复杂情绪。                     │
│  "妈，我没事。"                                         │
│                                                         │
│  ...                                                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 字数: 1,234  |  场景: 3个  |  状态: 已生成               │
└─────────────────────────────────────────────────────────┘

右侧可折叠面板:
┌──────────────┐
│ 场景细纲      │
│              │
│ 场景1: 卧室   │
│ 冲突: 内心挣扎│
│ 情绪: 平静→紧张│
│              │
│ 场景2: 客厅   │
│ ...          │
└──────────────┘
```

**编辑模式:**

- 使用 `@vueup/vue-quill` 或 `milkdown` (Markdown-first 编辑器)
- 侧边栏显示场景细纲作为参考
- 自动保存（debounce 2s）
- 显示字数统计

### 6.4 角色卡展示 — 详细设计

```
┌─────────────────────────────────────────────────────────┐
│ [+] 新增角色  [📊] 关系图  [📋] 列表视图                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   [Avatar]   │  │   [Avatar]   │  │   [Avatar]   │     │
│  │              │  │              │  │              │     │
│  │   林远       │  │   陈峰       │  │   苏晴       │     │
│  │   主角       │  │   反派       │  │   女主       │     │
│  │              │  │              │  │              │     │
│  │ 隐忍·果断   │  │ 虚伪·贪婪   │  │ 聪慧·善良   │     │
│  │              │  │              │  │              │     │
│  │ 欲望: 复仇   │  │ 欲望: 权力   │  │ 欲望: 真相   │     │
│  │ 恐惧: 失去   │  │ 恐惧: 暴露   │  │ 恐惧: 背叛   │     │
│  │              │  │              │  │              │     │
│  │ [编辑] [详情]│  │ [编辑] [详情]│  │ [编辑] [详情]│     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ── 角色关系图 ──────────────────────────────────────    │
│                                                         │
│       林远 ──仇恨──▶ 陈峰                                │
│        │               │                                │
│       恋人            合谋                               │
│        │               │                                │
│        ▼               ▼                                │
│       苏晴 ◀──利用── 赵雪                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**关系图实现:**

- 使用 ECharts graph 类型
- 节点 = 角色，大小按重要性缩放
- 边 = 关系，颜色/粗细按关系类型区分
- 支持拖拽、缩放、点击高亮相连节点

### 6.5 审校报告 — 详细设计

```
┌─────────────────────────────────────────────────────────┐
│ 审校报告                                    [重新审校]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 总分 82  │ │ 问题  12 │ │ 字数 8.2k│ │ 章节  10 │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                         │
│  ── 问题列表 ──────────────────────────────────────────  │
│                                                         │
│  [严重] 角色一致性: 第3章林远的性格描写与前文矛盾         │
│         前文: "林远从不轻易动怒"                         │
│         第3章: "林远怒不可遏地拍桌而起"                  │
│         [查看原文] [忽略]                                │
│                                                         │
│  [中等] 伏笔遗漏: 第1章埋下的"神秘信物"在第8章未回收     │
│         [跳转到第1章] [标记为已处理]                     │
│                                                         │
│  [轻微] 时间线: 第5章到第6章的时间跳跃不明确              │
│         [查看上下文] [忽略]                              │
│                                                         │
│  ── 对比视图 (选中问题时展开) ──────────────────────────  │
│  ┌─────────────────────┐ ┌─────────────────────┐       │
│ │ 原文                 │ │ 建议修改             │       │
│ │                     │ │                     │       │
│ │ 林远怒不可遏地拍桌   │ → │ 林远深吸一口气，     │       │
│ │ 而起...              │ │ 强压下心中的怒火...   │       │
│  │                     │ │                     │       │
│  │ [采纳] [拒绝] [编辑]│ │                     │       │
│  └─────────────────────┘ └─────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.6 流水线控制台 — 详细设计

```
┌─────────────────────────────────────────────────────────┐
│ 流水线控制台          [▶ 启动完整流水线] [⏸ 暂停] [⏹ 取消]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ── 进度时间线 ────────────────────────────────────────  │
│                                                         │
│  ✓ 选题评估 ── ✓ 世界观 ── ✓ 角色设计 ── ⏳ 大纲编剧   │
│       │            │            │            │          │
│     00:12        00:34        01:02        进行中...    │
│                                                         │
│  ○ 场景细纲 ── ○ 正文生成 ── ○ 编辑审校                 │
│                                                         │
│  ── 当前阶段详情 ──────────────────────────────────────  │
│                                                         │
│  大纲编剧 - 第3/10章                                    │
│  ████████████░░░░░░░░░░  30%                           │
│  预计剩余: ~3 分钟                                      │
│                                                         │
│  ── 实时日志 ──────────────────────────────────────────  │
│                                                         │
│  [20:30:01] 开始大纲编剧...                             │
│  [20:30:05] LLM 请求: 生成第1章大纲                     │
│  [20:30:12] 第1章大纲完成                               │
│  [20:30:13] LLM 请求: 生成第2章大纲                     │
│  [20:30:20] 第2章大纲完成                               │
│  [20:30:21] LLM 请求: 生成第3章大纲  ← 当前             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. MVP 范围与排期

### Phase 1: MVP (2-3 周)

**目标**: 能跑通完整流程，基础可用

| 页面 | 功能 | 优先级 | 估时 |
|------|------|--------|------|
| 项目列表 | 创建/查看/删除项目 | P0 | 1d |
| 项目详情 | 基本信息 + 阶段进度展示 | P0 | 0.5d |
| 流水线控制台 | 启动流水线 + 实时进度 + 日志 | P0 | 3d |
| 大纲编辑器 | 树形展示 + 内联编辑（不含拖拽） | P0 | 2d |
| 章节列表 | 表格展示 + 状态筛选 | P1 | 0.5d |
| 正文阅读器 | 只读模式 + 章节导航 | P1 | 1d |
| 角色管理 | 卡片展示 + 基本 CRUD | P1 | 1.5d |
| 全局设置 | LLM 配置 | P1 | 0.5d |
| 后端 API | REST 端点 + WebSocket | P0 | 5d |

**MVP 总估时**: ~15 天（1 人全栈）

### Phase 2: 增强 (2 周)

| 功能 | 估时 |
|------|------|
| 大纲拖拽排序 | 1d |
| 正文编辑模式（Markdown 编辑器） | 2d |
| 审校报告页面 | 2d |
| 角色关系图（ECharts） | 1.5d |
| 世界观设定编辑 | 1d |
| 导出功能（TXT/EPUB） | 1.5d |

### Phase 3: 完善 (1-2 周)

| 功能 | 估时 |
|------|------|
| 导出 PDF | 1d |
| 单阶段独立运行 | 1d |
| 发布管理（对接平台 API） | 3d |
| 暗色主题 | 1d |
| 响应式适配 | 2d |

### 开发顺序建议

```
Week 1:  后端 API 骨架 → 项目 CRUD → 流水线 API + WebSocket
Week 2:  前端脚手架 → 项目列表 → 流水线控制台（核心体验）
Week 3:  大纲编辑器 → 章节列表 → 正文阅读器 → 角色管理
Week 4:  审校报告 → 导出 → 打磨 → 测试
```

---

## 8. 目录结构

### 前端

```
NovelFactory/web/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── .env.development              # VITE_API_BASE=http://localhost:8000
├── .env.production               # VITE_API_BASE=
│
├── src/
│   ├── main.ts                   # 入口
│   ├── App.vue                   # 根组件
│   ├── env.d.ts                  # 类型声明
│   │
│   ├── api/                      # API 层
│   │   ├── client.ts             # Axios 实例
│   │   ├── project.ts            # 项目 API
│   │   ├── pipeline.ts           # 流水线 API
│   │   ├── outline.ts            # 大纲 API
│   │   ├── chapter.ts            # 章节 API
│   │   ├── character.ts          # 角色 API
│   │   ├── world.ts              # 世界观 API
│   │   └── review.ts             # 审校 API
│   │
│   ├── stores/                   # Pinia 状态
│   │   ├── project.ts
│   │   ├── pipeline.ts
│   │   └── editor.ts
│   │
│   ├── composables/              # 组合式函数
│   │   ├── usePipelineWs.ts      # WebSocket 连接
│   │   ├── useAutoSave.ts        # 自动保存
│   │   └── useMarkdown.ts        # Markdown 渲染
│   │
│   ├── router/                   # 路由
│   │   └── index.ts
│   │
│   ├── layouts/                  # 布局
│   │   ├── BasicLayout.vue       # 主布局（顶栏 + 内容区）
│   │   └── ProjectLayout.vue     # 项目布局（侧边栏 + 内容区）
│   │
│   ├── views/                    # 页面
│   │   ├── projects/
│   │   │   └── ProjectList.vue
│   │   ├── project/
│   │   │   ├── ProjectDetail.vue
│   │   │   ├── OutlineEditor.vue
│   │   │   ├── ChapterList.vue
│   │   │   ├── ChapterReader.vue
│   │   │   ├── CharacterManager.vue
│   │   │   ├── WorldSettings.vue
│   │   │   ├── ReviewReport.vue
│   │   │   ├── PipelineConsole.vue
│   │   │   └── ExportManager.vue
│   │   └── Settings.vue
│   │
│   ├── components/               # 通用组件
│   │   ├── StageProgress.vue     # 阶段进度条
│   │   ├── StatusTag.vue         # 状态标签
│   │   ├── MarkdownRenderer.vue  # Markdown 渲染
│   │   ├── CharacterCard.vue     # 角色卡片
│   │   ├── RelationGraph.vue     # 关系图
│   │   └── LogStream.vue         # 日志流
│   │
│   ├── types/                    # TypeScript 类型
│   │   ├── project.ts
│   │   ├── outline.ts
│   │   ├── chapter.ts
│   │   ├── character.ts
│   │   └── pipeline.ts
│   │
│   └── utils/                    # 工具函数
│       ├── format.ts             # 格式化（日期/字数）
│       └── constants.ts          # 常量定义
│
└── public/
    └── favicon.ico
```

### 后端新增

```
NovelFactory/src/novel_factory/api/
├── __init__.py
├── main.py                     # FastAPI app, CORS, mount routers
├── deps.py                     # 依赖注入 (get_store, get_ws_manager)
├── schemas/
│   ├── project.py              # Pydantic 模型
│   ├── outline.py
│   ├── chapter.py
│   ├── character.py
│   └── pipeline.py
├── routers/
│   ├── __init__.py
│   ├── projects.py
│   ├── pipeline.py
│   ├── outline.py
│   ├── chapters.py
│   ├── characters.py
│   ├── world.py
│   ├── review.py
│   └── export.py
└── ws/
    ├── __init__.py
    └── manager.py              # WebSocket 连接管理器
```

---

## 附录: 关键技术决策记录

| # | 决策 | 理由 |
|---|------|------|
| D1 | SPA 而非 SSR | 个人工具，不需要 SEO；部署简单（静态文件 + API） |
| D2 | Ant Design Vue 而非 Element Plus | 表格/树组件更强大，Pro 模板可用，更适合复杂后台 |
| D3 | Pinia 而非 Vuex | Vue 3 官方推荐，类型推导更好，更轻量 |
| D4 | WebSocket 而非 SSE | 需要双向通信（取消/暂停流水线） |
| D5 | JSON 文件存储保持不变 | 现有架构已验证，API 层包装即可；后期可迁移 SQLite |
| D6 | TailwindCSS + Ant Design | Tailwind 处理自定义样式，Ant Design 处理通用组件，互补 |
| D7 | 前后端同仓库 | 个人项目，简化部署和版本管理 |
