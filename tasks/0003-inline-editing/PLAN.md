# PLAN — 二次编辑功能

## 核心问题

当前系统是"单向管线"：AI 生成 → 存储 → 下一阶段。用户无法修改任何中间结果。

## 设计方案

### 每个阶段的编辑模式

```
AI 生成 → 用户预览 → [采用] / [编辑] / [重新生成]
                          ↓
                     编辑器打开 → 修改 → 保存 → 才进入下一阶段
```

### 需要编辑的阶段

| 阶段 | 数据 | 编辑方式 |
|------|------|---------|
| 选题 | title/premise/score | 表单编辑 |
| 世界观 | world_settings 列表 | 卡片编辑（每项可改） |
| 角色 | characters 列表 | 角色卡编辑（每项可改） |
| 大纲 | chapters 列表 | 最重要！章节标题/事件/钩子可改，可拖拽排序 |
| 元数据 | title/synopsis/tags | MetadataEditor 已实现 |
| 正文 | chapter draft | 富文本编辑器 |

### 后端 API

```
PUT /api/projects/{id}/topic          — 更新选题
PUT /api/projects/{id}/world          — 更新世界观
PUT /api/projects/{id}/characters     — 更新角色
PUT /api/projects/{id}/outline        — 更新大纲
PUT /api/projects/{id}/chapters/{num} — 更新章节正文
```

### 前端组件

每个阶段的展示组件需要支持"编辑模式"切换：
- 查看模式：只读展示
- 编辑模式：表单/文本框可编辑
- 底部：[取消] [保存] 按钮

### 状态机

```
stage_status: generated → editing → saved → confirmed
                              ↓
                          (可反复编辑)
```
