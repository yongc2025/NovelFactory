# PLAN — 执行路径

## 目标

在创建项目和大纲完成后，自动生成完整的书籍元数据。

## 方案

### Step 1: 后端 — 扩展 ProjectCreate 模型

**文件**: `src/novel_factory/api/schemas.py`

新增字段：
```python
# 书籍元数据（可选，AI可生成）
book_title: str | None = None        # 书名（用户填写或AI生成）
book_synopsis: str | None = None     # 简介（AI生成后用户可编辑）
book_tags: list[str] = []            # 标签（AI推荐）
book_category: str | None = None     # 分类（AI匹配）
```

### Step 2: 后端 — 新增元数据生成 AI 角色

**文件**: `src/novel_factory/engine/metadata.py`（新建）

```python
async def generate_metadata(
    project_id: str,
    topic: dict,
    outline: dict,
    characters: list,
    params: dict,
) -> dict:
    """生成书籍元数据：书名/简介/标签/分类"""
    # 返回 {"title": ..., "synopsis": ..., "tags": [...], "category": ...}
```

Prompt 设计要点：
- 书名：根据题材+主角+冲突生成5个候选，用户选一个
- 简介：根据大纲生成3个版本（50字/150字/300字）
- 标签：根据题材+平台推荐5个标签
- 分类：匹配番茄分类体系

### Step 3: 后端 — Pipeline 集成

**文件**: `src/novel_factory/pipeline.py`

在 outline 阶段后、scene 阶段前插入 metadata 阶段：
```
选题 → 世界观 → 角色 → 大纲 → 🆕 元数据生成 → 场景 → 正文 → 审校
```

### Step 4: 后端 — ProjectStore 扩展

**文件**: `src/novel_factory/db/project_store.py`

新增：
```python
def save_metadata(project_id: str, metadata: dict)
def get_metadata(project_id: str) -> dict | None
```

### Step 5: 后端 — API 路由

**文件**: `src/novel_factory/api/app.py`

新增：
```
GET  /api/projects/{id}/metadata  — 获取元数据
POST /api/projects/{id}/metadata  — 更新元数据（用户编辑后保存）
POST /api/projects/{id}/metadata/regenerate — 重新生成
```

### Step 6: 前端 — 创建向导添加书名字段

**文件**: `web/src/views/ProjectCreate.vue`

在 Tab 1（基本信息）中添加：
- 书名输入框（可选，留空则AI生成）
- "让AI起名" 按钮

### Step 7: 前端 — 元数据展示/编辑组件

**文件**: `web/src/components/project/MetadataEditor.vue`（新建）

展示：
- 书名（可编辑，显示AI推荐的5个候选）
- 简介（可编辑，显示3个版本供选择）
- 标签（可增删，AI推荐5个）
- 分类（下拉选择，AI预选）

### Step 8: 前端 — 项目详情集成

**文件**: `web/src/views/ProjectDetail.vue`

在大纲阶段后显示元数据编辑面板。

## 原子变更清单

1. `src/novel_factory/api/schemas.py` — 新增 4 个字段
2. `src/novel_factory/engine/metadata.py` — 新建元数据生成模块
3. `src/novel_factory/pipeline.py` — 插入 metadata 阶段
4. `src/novel_factory/db/project_store.py` — 新增 save/get_metadata
5. `src/novel_factory/api/app.py` — 新增 3 个 API 路由
6. `web/src/views/ProjectCreate.vue` — 书名输入框
7. `web/src/components/project/MetadataEditor.vue` — 新建
8. `web/src/views/ProjectDetail.vue` — 集成元数据面板

## 回滚协议

1. git revert 相关 commit
2. 确认 pipeline 和 CLI 仍可正常运行
