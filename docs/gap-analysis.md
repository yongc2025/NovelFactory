# 设计 vs 实现偏差分析

> 2026-05-29 | 对照 system-architecture.md、frontend-architecture.md、phase1/2 设计文档与实际代码

---

## 一、存储层（最大偏差）

| 维度 | 设计 | 实现 | 影响 |
|------|------|------|------|
| 结构化存储 | SQLite + FTS5 | JSON 文件（ProjectStore） | 无全文检索、无事务、无并发安全 |
| 数据目录 | `data/novel.db` | `data/<project_id>/*.json` | 文件系统遍历即可访问 |
| 迁移难度 | — | 中等 | 需要重写 project_store.py + schema.py |

**实际数据文件**：
```
data/
├── projects.json              # 项目索引
└── <project_id>/
    ├── project.json           # 项目元数据 + 26 个创建参数
    ├── topic.json             # 选题评估（3-5 个方案）
    ├── world.json             # 世界观设定
    ├── characters.json        # 角色数据
    ├── outline.json           # 大纲（章节列表）
    ├── metadata.json          # 书名/简介/标签/分类（Task 0002）
    ├── scenes/ch01.json       # 场景细纲
    ├── drafts/ch01.md         # 正文
    └── review.json            # 审校报告
```

---

## 二、实时通信

| 维度 | 设计 | 实现 |
|------|------|------|
| 进度推送 | WebSocket（`ws/pipeline/{id}`） | HTTP 轮询（`GET /pipeline/status`） |
| 日志流 | WebSocket 实时推送 | 无 |
| 取消/暂停 | WebSocket 双向通信 | 无 |

**影响**：前端无法实时看到流水线进展，只能定时轮询状态。

---

## 三、前端路由与页面

| 设计路由 | 实际实现 | 状态 |
|----------|---------|------|
| `/projects` (Dashboard) | `/dashboard` | ✅ |
| `/projects/create` | `/project/create` | ✅ |
| `/projects/:id` (详情) | `/project/:id` | ✅ 但所有数据在一个页面 |
| `/projects/:id/outline` (大纲编辑器) | — | ❌ 未实现 |
| `/projects/:id/chapters` (章节列表) | — | ❌ 未实现 |
| `/projects/:id/chapters/:num` (正文阅读器) | — | ❌ 未实现 |
| `/projects/:id/characters` (角色管理) | — | ❌ 未实现 |
| `/projects/:id/world` (世界观) | — | ❌ 未实现 |
| `/projects/:id/review` (审校报告) | — | ❌ 未实现 |
| `/projects/:id/pipeline` (流水线控制台) | — | ❌ 未实现 |
| `/projects/:id/export` (导出管理) | — | ❌ 未实现 |
| `/settings` (全局设置) | — | ❌ 未实现 |

**实际结构**：3 个路由（Dashboard / ProjectCreate / ProjectDetail），所有项目数据在 ProjectDetail 页面中以 Tab 形式展示。

---

## 四、前端组件

| 设计组件 | 实际组件 | 偏差 |
|----------|---------|------|
| ProjectCard（卡片式项目列表） | Dashboard.vue（简单列表） | 基础版 |
| 5 步 Tab 创建向导 | ProjectCreate.vue | ✅ 一致 |
| StageProgressCard | PipelineProgress.vue | ✅ 基础版 |
| OutlineEditor（树形+拖拽+详情面板） | OutlineEditor.vue | 无拖拽，无详情面板 |
| ChapterReader（阅读+编辑模式） | ChapterReader.vue | 只读，无编辑器 |
| CharacterCardGrid + 关系图 | CharacterCard.vue | 无关系图 |
| ReviewReport（评分+问题+对比视图） | ReviewReport.vue | 无对比视图 |
| PipelineConsole（时间线+日志流） | PipelineProgress.vue | 无日志流 |
| WorldPanel | WorldPanel.vue | ✅ 基础版 |
| MetadataEditor | MetadataEditor.vue | ✅ Task 0002 新增 |
| StageConfirm | StageConfirm.vue | ✅ 但确认逻辑是否阻塞流水线待验证 |

---

## 五、API 端点

### 已实现（~20 个端点）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/projects` | POST/GET | 创建/列表 |
| `/api/projects/{id}` | GET/DELETE | 详情/删除 |
| `/api/projects/{id}/pipeline/start` | POST | 启动完整流水线 |
| `/api/projects/{id}/pipeline/plan` | POST | 只生成大纲 |
| `/api/projects/{id}/pipeline/write` | POST | 从大纲生成正文 |
| `/api/projects/{id}/pipeline/status` | GET | 流水线状态 |
| `/api/projects/{id}/pipeline/confirm` | POST | 阶段确认 |
| `/api/projects/{id}/topic` | GET/PUT | 选题数据 |
| `/api/projects/{id}/world` | GET/PUT | 世界观数据 |
| `/api/projects/{id}/characters` | GET/PUT | 角色数据 |
| `/api/projects/{id}/outline` | GET/PUT | 大纲数据 |
| `/api/projects/{id}/chapters/{num}` | GET/PUT | 章节数据 |
| `/api/projects/{id}/review` | GET | 审校报告 |
| `/api/projects/{id}/stages` | GET | 阶段状态 |
| `/api/projects/{id}/stages/{stage}/confirm` | POST | 单阶段确认 |
| `/api/projects/{id}/metadata` | GET/POST/PUT | 元数据 |
| `/api/projects/{id}/metadata/regenerate` | POST | 重新生成元数据 |
| `/api/config` | GET/PUT | 全局配置 |
| `/api/config/genres` | GET | 题材列表 |

### 设计中有但未实现

| 端点 | 说明 |
|------|------|
| `PATCH /api/projects/{id}` | 更新项目 |
| `GET /api/projects/{id}/stats` | 项目统计 |
| `POST /api/projects/{id}/pipeline/stage/{stage}` | 单阶段独立运行 |
| `POST /api/projects/{id}/pipeline/cancel` | 取消流水线 |
| `PATCH /api/projects/{id}/outline/chapters/{num}` | 更新单章大纲 |
| `POST /api/projects/{id}/outline/chapters` | 新增章节 |
| `DELETE /api/projects/{id}/outline/chapters/{num}` | 删除章节 |
| `PUT /api/projects/{id}/outline/reorder` | 章节排序 |
| `GET /api/projects/{id}/chapters` | 章节列表 |
| `POST /api/projects/{id}/characters` | 新增角色 |
| `PATCH /api/projects/{id}/characters/{char_id}` | 更新角色 |
| `DELETE /api/projects/{id}/characters/{char_id}` | 删除角色 |
| `GET /api/projects/{id}/characters/relations` | 角色关系图 |
| `POST /api/projects/{id}/review` | 重新审校 |
| `GET/POST /api/projects/{id}/export` | 导出 |
| `WS /ws/pipeline/{id}` | WebSocket 进度推送 |
| `GET/PUT /api/settings` | 全局设置 |
| `GET /api/health` | 健康检查 |

---

## 六、LLM 调用

| 维度 | 设计 | 实现 |
|------|------|------|
| 模型 | DeepSeek-V3 + R1 | DeepSeek-V4 Pro + Flash + MiMo |
| 重试 | 未明确 | ❌ 无重试逻辑 |
| 超时 | 未明确 | 120 秒固定超时 |
| 成本追踪 | 设计有 | ⚠️ 有 `_usage_log` 但未暴露 API |
| 降级 | 设计有 | ❌ 无降级逻辑 |

---

## 七、记忆系统

| 维度 | 设计 | 实现 |
|------|------|------|
| 角色状态追踪 | 设计有 | ❌ |
| 层次摘要 | 设计有 | ❌ |
| 伏笔追踪 | 设计有 | ❌ |
| 滑动窗口 | 设计有 | ⚠️ writer.py 有前文传递但非滑动窗口 |

**engine/memory.py** 存在（2181 字节）但未集成到流水线中。

---

## 八、导出

| 格式 | 设计 | 实现 |
|------|------|------|
| Markdown（整体） | ✅ | ✅ export.py |
| Markdown（分章） | ✅ | ✅ export.py |
| TXT | ✅ | ❌ |
| EPUB | ✅ | ❌ |
| PDF | ✅ | ❌ |

---

## 九、新增功能（不在原始设计中）

| 功能 | 来源 | 说明 |
|------|------|------|
| metadata 阶段 | Task 0002 | 流水线从 7 阶段扩展为 8 阶段 |
| MetadataEditor 组件 | Task 0002 | 前端元数据编辑 |
| StageConfirm 组件 | Task 0003 | 阶段确认 UI |
| Inline Editing | Task 0003 | 二次编辑功能 |
| 题材矩阵 API | 实现 | `/api/config/genres` |

---

## 十、优先修复建议

### P0（阻塞核心体验）
1. **端到端实跑验证** — 跑一次真实生成，发现实际问题
2. **LLM 调用重试** — 指数退避 3 次，避免单次失败整条流水线挂掉
3. **流水线状态持久化** — 内存 dict 重启丢失，写入 project.json

### P1（影响可用性）
4. **WebSocket 进度推送** — 替代轮询，实时看到生成进展
5. **大纲编辑器** — 拖拽排序 + 详情面板
6. **正文阅读器** — 至少有章节导航 + 字数统计
7. **测试** — 核心流程 mock 测试

### P2（增强体验）
8. **审校报告对比视图** — 原文 vs 建议修改并排
9. **角色关系图** — ECharts 力导向图
10. **多格式导出** — TXT（番茄）/ EPUB
11. **流水线日志流** — 实时日志输出
