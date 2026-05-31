# 后端契约审计报告

> 范围：`src/novel_factory/api/app.py`（1737 行）、`schemas.py`（308 行）、`task_registry.py`（198 行）、`db/project_store.py`、`db/context_store.py`、前端 `web/src/api/index.ts`、`web/src/types/index.ts`。审计方式：纯静态、只读。

## 1. 整体评分 + 一句话结论

**评分：5.5 / 10（C）。**

一句话：路由覆盖较全且 TaskRegistry 设计合理，但**前后端字段契约严重不对齐**（响应被两层 ApiResponse + 自定义 `XxxResponse{project_id, xxx}` 包裹却被前端当作 ApiResponse 解构，世界观/角色/大纲/审校全部依赖运行时 `_normalize_*` 把后端格式硬拗成前端 type），加上 `pipeline_stage`、`pipeline/confirm`、`stages` 三套并存且语义重叠，命名 snake/camel/双别名混用，已经事实上是 “能跑但脆弱” 的状态。

---

## 2. API 端点清单

> 路径全部以 `/api` 为前缀。状态列：✅ 正常 / ⚠️ 与前端不对齐或有歧义 / ❌ 重复/废弃/缺失。

| 方法 | 路径 | 作用 | 状态 |
|---|---|---|---|
| POST | `/projects` | 创建项目（5 级参数 `ProjectCreate`） | ✅（app.py:211） |
| GET | `/projects` | 项目列表 | ⚠️ 无分页（app.py:263） |
| GET | `/projects/{id}` | 项目详情 | ✅（app.py:271） |
| DELETE | `/projects/{id}` | 删除项目（直接 rmtree） | ⚠️ 无确认/回收站（app.py:281） |
| POST | `/projects/{id}/pipeline/start` | 跑完整 8 阶段流水线 | ⚠️ 与 stage 端点语义重叠（app.py:463） |
| POST | `/projects/{id}/pipeline/plan` | 只跑到大纲（前 4 阶段） | ⚠️ 前端未调用（app.py:491） |
| POST | `/projects/{id}/pipeline/stage/{stage}` | 跑单阶段（TaskRegistry 管理） | ⚠️ 入参 schema 不统一（app.py:525） |
| POST | `/projects/{id}/pipeline/write` | 从大纲生成正文 | ⚠️ 前端未调用（app.py:730） |
| GET | `/projects/{id}/pipeline/status` | 流水线状态 | ⚠️ 与 TaskRegistry 双轨（app.py:753） |
| POST | `/projects/{id}/pipeline/confirm` | 阶段确认（adopt/edit/regenerate） | ⚠️ 与下面 `stages/{stage}/confirm` 重复（app.py:808） |
| GET | `/projects/{id}/pipeline/stages` | 流水线阶段列表 | ⚠️ 与 `/stages` 重复（app.py:871） |
| POST | `/projects/{id}/pipeline/stages/{stage}/confirm` | 简化确认 | ❌ 与 `/pipeline/confirm` 和 `/stages/{stage}/confirm` 三重重复（app.py:882） |
| GET | `/projects/{id}/pipeline/active-task` | 取项目当前活跃任务 | ✅（app.py:1617） |
| GET | `/projects/{id}/topic` | 选题方案 | ⚠️ 包装两层（app.py:916） |
| PUT | `/projects/{id}/topic` | 更新选题 | ⚠️ body 无 schema（app.py:1293） |
| GET | `/projects/{id}/world` | 世界观 | ⚠️ `_normalize_world` 硬拗（app.py:929） |
| PUT | `/projects/{id}/world` | 更新世界观 | ⚠️ body 无 schema（app.py:1318） |
| GET | `/projects/{id}/characters` | 角色列表 | ⚠️ `_normalize_character` 硬拗（app.py:974） |
| PUT | `/projects/{id}/characters` | 更新角色 | ⚠️ body 无 schema（app.py:1329） |
| GET | `/projects/{id}/outline` | 大纲 | ⚠️ `_normalize_outline` 硬拗（app.py:1001） |
| PUT | `/projects/{id}/outline` | 更新大纲 | ⚠️（app.py:1359） |
| POST | `/projects/{id}/outline/generate` | 分批生成大纲 | ⚠️ 与 `pipeline/stage/outline` 行为重叠（app.py:1013） |
| GET | `/projects/{id}/drafts/status` | 各章正文状态 | ✅（app.py:1145） |
| GET | `/projects/{id}/scenes/{ch}` | 取场景细纲 | ✅（app.py:1177） |
| PUT | `/projects/{id}/scenes/{ch}` | 存场景细纲 | ⚠️ body 无 schema（app.py:1187） |
| GET | `/projects/{id}/chapters/{ch}` | 章节正文+场景 | ⚠️ chapter_num/chapter_number 双字段（app.py:1197） |
| PUT | `/projects/{id}/chapters/{ch}` | 更新正文 | ✅（app.py:1370） |
| POST | `/projects/{id}/chapters/{ch}/revise` | 按反馈重写 | ✅（app.py:1383） |
| GET | `/projects/{id}/review` | 审校汇总报告 | ⚠️ `_normalize_review` 硬拗（app.py:1239） |
| GET | `/projects/{id}/review/{ch}` | 某章审校 | ✅（app.py:1228） |
| GET | `/projects/{id}/metadata` | 书籍元数据 | ✅（app.py:1452） |
| POST | `/projects/{id}/metadata` | 合并写入元数据 | ⚠️ POST 用于更新，非标准（app.py:1464） |
| PUT | `/projects/{id}/metadata` | 替换元数据 | ✅（app.py:1478） |
| POST | `/projects/{id}/metadata/regenerate` | 重新生成元数据 | ⚠️ 同步阻塞，未走 TaskRegistry（app.py:1489） |
| GET | `/projects/{id}/stages` | 项目阶段追踪 | ⚠️ 与 `/pipeline/stages` 同名不同义（app.py:1425） |
| POST | `/projects/{id}/stages/{stage}/confirm` | 阶段状态确认 | ⚠️ 与 `/pipeline/...confirm` 重复（app.py:1435） |
| GET | `/pipeline/tasks/{task_id}` | 任务查询 | ✅（app.py:1594） |
| POST | `/pipeline/tasks/{task_id}/cancel` | 任务取消 | ⚠️ 错误时无 4xx（app.py:1603） |
| GET | `/config` | 系统配置 | ✅（app.py:1514） |
| PUT | `/config` | 更新默认 provider | ⚠️ 仅内存级（app.py:1540） |
| GET | `/config/genres` | 题材矩阵 | ✅（app.py:1579） |
| POST | `/generate/inspiration` | AI 灵感生成 | ⚠️ 同步阻塞 LLM（app.py:1658） |

小计：**42 个端点**，其中 “阶段确认” 类 3 个、“大纲生成” 类 2 个、“流水线阶段列表” 类 2 个 ——**至少 5 处端点存在职责重叠**。

---

## 3. 前后端契约不一致清单

### 3.1 响应包装层不对齐

前端 `ApiResponse<T>` 期望 `{code, message, data}`，但后端**绝大多数端点直接返回 Pydantic model 或 dict**，未包装 ApiResponse。前端 `http` 拦截器读 `response.data` 即 Axios 的 data（HTTP body），实际拿到的就是 `ProjectResponse` 本身而非 `{code, message, data: ProjectResponse}`。

| 端点 | 前端期望 | 后端实际 | 影响 |
|---|---|---|---|
| GET `/projects` | `ApiResponse<Project[]>` | `list[ProjectListItem]`（无包裹） | 前端 `res.data.data` 为 undefined |
| GET `/projects/{id}` | `ApiResponse<Project>` | `ProjectResponse`（直接返回） | 同上 |
| POST `/projects` | `ApiResponse<Project>` | `ProjectResponse` | 同上 |
| GET `/pipeline/status` | `ApiResponse<PipelineStatus>` | `PipelineStatus` | 同上 |
| POST `/pipeline/stage/{s}` | `ApiResponse<PipelineTask> 或 PipelineTask` | `dict`（task_id/message/project_id/stage） | 联合类型说明前端也不确定 |
| GET `/pipeline/tasks/{t}` | `ApiResponse<PipelineTask> 或 PipelineTask` | `dict`（PipelineTask.to_dict()） | 同上 |
| GET `/topic` | `ApiResponse<TopicPlan[]>` | `TopicResponse{project_id, topic}` | **双层嵌套** |
| GET `/world` | `ApiResponse<WorldSetting>` | `WorldSettingResponse{project_id, world}` | 同上 |
| GET `/characters` | `ApiResponse<Character[]>` | `CharacterResponse{project_id, characters}` | 同上 |
| GET `/outline` | `ApiResponse<Outline>` | `OutlineResponse{project_id, outline}` | 同上 |
| GET `/review` | `ApiResponse<ReviewReport>` | `ReviewResponse{project_id, review}` | 同上 |
| GET `/metadata` | `ApiResponse<BookMetadata>` | `BookMetadata`（直接返回） | **唯一对齐**的 |

**结论：** 前端 ApiResponse 包装基本形同虚设，除 `/metadata` 外所有端点返回结构与前端 type 解构路径不匹配。前端能跑是因为直接用 `res.data.xxx` 访问，跳过了 ApiResponse 抽象层。

### 3.2 字段命名 / 类型不一致

| 字段 | 前端 types/index.ts | 后端 schemas.py / 实际 | 位置 |
|---|---|---|---|
| 章节号 | `chapter_number: number` | `chapter_num` + 别名 `chapter_number` | schemas.py:152 ChapterResponse |
| 正文内容 | `content: string` | `draft` + 别名 `content` | schemas.py:150 ChapterResponse |
| 项目状态 | `'draft'/'generating'/'reviewing'/'completed'/'failed'` | `'created'/'complete'/'planned'` | schemas.py:154 + project_store.py:104 |
| PipelineStage | 前端含 `'characters'` `'chapters'` 复数 | 后端 STAGES 只用 `'character'`/`'draft'` | app.py:90 |
| Project.platform | `platform: string` 单数 | 后端只返回 `platforms: string[]` | types/index.ts:60 |
| Project.word_count_target | `word_count_target` | 后端用 `target_words` | types/index.ts:62 |
| Project.book_title/synopsis/tags/category | 前端有 | `ProjectResponse` 无 | schemas.py:139-167 |
| OutlineChapter.core_event | `core_event` | `_normalize_outline` 映射到 `summary` | app.py:1127 **方向相反** |
| OutlineChapter.foreshadow_ops/emotion_position/hook | 前端有 | `_normalize_outline` 不返回 | app.py:1119-1131 |
| OutlineChapter.plot_lines_progress | 前端有 | 后端不返回 | app.py:1119-1131 |
| ReviewIssue.chapter_number | 前端 `number` | `_normalize_review` 硬编码 `0` | app.py:1272 **章节号丢失** |
| Character.id | 前端 `string` 持久 ID | `_normalize_character` 用 `f"char_{index}"` | app.py:990 **非持久** |
| Character.personality/appearance/arc | 前端有 | 映射链：`arc_description→arc`、`core_desire→background` | app.py:986-989 脆弱 |
| WorldSetting.key_locations/rules/constraints | `string[]` | `_normalize_world` 按中文 category 名映射，遗漏多 | app.py:944-972 |

### 3.3 pipeline_stage 端点参数对齐

| 参数 | outline | draft | review | scene |
|---|---|---|---|---|
| `start_chapter` | ❌ | ✅ | ✅ | ❌（全量） |
| `batch_size` | ❌（走 `/outline/generate`） | ✅ 上限 10 | ✅ 上限 10 | ❌ |
| `force` | ❌ | ✅ | ❌ | ❌ |
| `feedback` | ✅ | ❌ | ❌ | ❌ |

**问题：** `/outline/generate` 和 `/pipeline/stage/outline` 功能重叠但参数体系完全不同；`scene` 阶段不支持任何批量参数（必全量）；`force`/`start_chapter` 只在部分阶段可用。前端需记忆这张表，否则参数会被静默忽略。

---

## 4. 错误处理规范度

### 4.1 HTTP Status Code 使用

| 端点 | 使用场景 | 规范度 | 备注 |
|---|---|---|---|
| POST /projects | 201 Created | ✅ | |
| DELETE /projects/{id} | 204 No Content | ✅ | |
| 项目不存在 | 404 | ✅ | 所有端点一致 |
| 流水线运行中 | 409 Conflict | ✅ | pipeline_start/plan/write |
| TaskRegistry 互斥冲突 | 409 | ✅ | |
| 无效阶段名 | 400 | ✅ | |
| edit 缺少 edits | 400 | ✅ | |
| 无大纲就写正文 | 400 | ✅ | |
| 全局异常 | 500 | ⚠️ | 返回 `{detail, type}` 而非 `{code, message, data}`，与前端 ApiResponse 不一致 |
| 任务已结束取消 | 200 + 消息 | ❌ | 应为 409 或 422，app.py:1610 |
| batch_size 越界 | 400 | ✅ | outline/generate 有校验 |

### 4.2 错误响应格式不一致

- **HTTPException**：FastAPI 默认返回 `{"detail": "..."}` （app.py 全局）
- **全局异常处理器**：返回 `{"detail": "...", "type": "..."}` （app.py:203）
- **前端期望**：`ApiResponse` 格式 `{"code": N, "message": "...", "data": null}`

三种格式，前端拦截器读 `error.response?.data?.message`（api/index.ts:27），但后端返回的字段是 `detail` 而非 `message`，**错误消息无法被前端正确展示**。

### 4.3 缺失的错误场景

| 场景 | 现状 | 建议 |
|---|---|---|
| PUT body 格式错误 | FastAPI 默认 422 | 可，但 422 的 detail 格式与业务错误不统一 |
| 删除正在运行的项目 | 不检查 pipeline 状态 | 应 409 |
| outline/generate 超出总章数 | 400 | ✅ |
| revise 时正文不存在 | 404 | ✅ |
| metadata/regenerate LLM 失败 | 500 | 应区分 LLM 错误和系统错误 |
| generate/inspiration LLM 失败 | 500 | 同上 |

---

## 5. 关键风险

### P0（阻断级）

1. **ReviewIssue.chapter_number 全为 0** — app.py:1272 `_normalize_review` 硬编码 `chapter_number: 0`，审校问题无法定位到具体章节。**前端审校 UI 按章节筛选/展示将完全失效。**

2. **错误消息字段名不匹配** — 后端 HTTPException 返回 `detail`，前端拦截器读 `message`（api/index.ts:27），**所有 API 错误在前端只显示 "请求失败"**，用户无法看到具体原因。

### P1（高）

3. **ApiResponse 包装层名存实亡** — 前端定义了 `ApiResponse<T>{code,message,data}` 但后端从不用。前端若严格按类型解构 `res.data.data` 则全部 undefined。当前能跑是因为前端组件直接用 `res.data.xxx` 绕过类型。**一旦有人按类型正确解构，全站 404。**

4. **内容端点双层嵌套** — topic/world/characters/outline/review 五个端点返回 `{project_id, xxx}` 结构，前端类型期望 `data` 直接是内容数组或对象。需要前端 `.data.topic` / `.data.world` 二次取值，与 `ApiResponse.data` 三层嵌套，极易搞混。

5. **PipelineStatus 与 TaskRegistry 双轨状态** — `_pipeline_states`（内存 dict）和 `registry`（TaskRegistry 单例）并行管理同一件事。`pipeline_start`/`plan`/`write` 用旧状态，`pipeline_stage` 用 TaskRegistry。**状态查询端点 `/pipeline/status` 只看旧状态，忽略 TaskRegistry 的任务状态。**

6. **Project.status 枚举不对齐** — 后端返回 `'created'/'complete'/'planned'`，前端 `ProjectStatus` 无这三个值。前端条件渲染可能失效。

### P2（中）

7. **Character.id 非持久** — `_normalize_character` 用 `f"char_{index}"` 生成 ID（app.py:990），每次请求顺序可能变化。前端 `CharacterRelationship.target_id` 引用会断裂。

8. **OutlineChapter 字段大量丢失** — `foreshadow_ops`、`emotion_position`、`emotion_arc`、`hook`、`plot_lines_progress` 五个字段前端有但 `_normalize_outline` 不返回，**大纲编辑 UI 缺少关键数据**。

9. **阶段确认三套接口并存** — `/pipeline/confirm`（action: adopt/edit/regenerate）、`/pipeline/stages/{stage}/confirm`（简化确认）、`/stages/{stage}/confirm`（StageInfo 确认），职责重叠且语义微妙不同。**前端同时调用 `confirmStage` 和 `confirmStageAction` 两个函数。**

10. **列表 API 无分页** — `/projects` 返回全量列表，project_store.list_projects() 一次性加载索引文件。项目数增长后将成为性能瓶颈。

11. **内存状态无持久化** — `_pipeline_states` 和 `_stage_states` 为进程内 dict，服务重启即丢失。TaskRegistry 同理。前端刷新后流水线状态归零。

12. **pipeline_stage 入参无 schema** — body 为 `dict | None`（app.py:525），`start_chapter`/`batch_size`/`force`/`feedback` 全靠约定，无 Pydantic 校验。非法参数被静默忽略。

---

## 6. API 设计改进建议

### 6.1 统一响应格式（最高优先级）

选择一种，贯彻到底：
- **方案 A**：后端统一包装 `{code, message, data}`，与前端 ApiResponse 对齐
- **方案 B**：前端删掉 ApiResponse，直接用各端点的原生类型

推荐方案 A，因为便于全局错误处理和 HTTP 状态码分离。

### 6.2 消除内容端点双层嵌套

- `/topic` 直接返回 `list[TopicPlan]` 而非 `TopicResponse{project_id, topic}`
- 或在 schemas 中定义 `TopicListResponse(data=list[TopicPlan])` 替代
- 同理处理 world/characters/outline/review

### 6.3 合并阶段确认接口

- 废弃 `/pipeline/confirm` 和 `/stages/{stage}/confirm`
- 统一为 `/pipeline/stages/{stage}/confirm`，body 用 `ConfirmRequest`
- 前端只保留一个确认函数

### 6.4 统一流水线状态管理

- 废弃 `_pipeline_states` / `_stage_states` 内存 dict
- 全部走 TaskRegistry，查询端点从 registry 聚合
- 或引入 SQLite 持久化

### 6.5 pipeline_stage 入参 Schema 化

```python
class StageRunRequest(BaseModel):
    feedback: str | None = None
    start_chapter: int | None = Field(None, ge=1)
    batch_size: int | None = Field(None, ge=1, le=10)
    force: bool = False
```

所有 stage 统一接收同一 schema，不支持的字段在后端忽略而非前端猜测。

### 6.6 消除 _normalize_* 运行时转换

当前后端 LLM 生成的格式与前端 type 不一致，靠 `_normalize_*` 在 API 层硬拗。应：
- 在 LLM prompt 层约束输出格式（与前端 type 对齐）
- 或定义 "后端存储格式" → "API 响应格式" 的声明式映射，替代 if-else 链

### 6.7 补充分页

- `/projects` 加 `page`/`page_size` 参数
- `/chapters` 列表端点（当前只有单章查询）

### 6.8 错误格式统一

- 自定义 `AppException` 基类，统一返回 `{code, message, data}`
- 全局异常处理器同时处理 HTTPException 和 AppException
- 前端拦截器改为读 `error.response?.data?.message` 或 `error.response?.data?.detail`

### 6.9 鉴权 / CORS

- 当前 CORS 硬编码 localhost 端口，生产部署需改为配置化
- 无任何鉴权，任何人可访问所有 API
- 建议至少加 API Key 或 JWT
