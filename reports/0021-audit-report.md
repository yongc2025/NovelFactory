# 0021-API 契约对齐审计报告

## 1. 核心矛盾：角色 12 维属性丢失

目前后端 `engine/character.py` 已经能生成含有 12 维属性（伤口、欲望、恐惧等）的角色，但由于 API 接口和前端类型的“契约”还是旧的，导致这些灵魂数据无法在 UI 上展示。

### 1.1 发现的断裂点
- **数据存储 (`db/models.py`)**: `Character` 模型已有 `personality_deep`, `core_desire`, `core_fear`, `voice_style`, `arc_start`, `arc_end` 等字段，但没有 `traits` 或 12 维属性的结构化字段。
- **API 转换 (`api/app.py`)**: `_normalize_character` 函数目前只做了简单的字段映射，且把 `core_desire` 塞进了前端的 `background` 字段，造成了语义混淆。
- **前端定义 (`web/src/types/index.ts`)**: `Character` 类型严重滞后，仅包含 `traits`, `personality`, `appearance` 等基础字段，完全没有体现“伤口/欲望/恐惧/弧光”等核心方法论字段。

## 2. 待对齐字段对照表 (角色篇)

| 语义维度 (12层系统) | 后端字段 (Engine) | 数据库字段 (Character) | 前端字段 (Character TS) | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| 核心欲望 | `core_desire` | `core_desire` | `background` (错位) | ❌ 需修正为 `core_desire` |
| 核心恐惧/伤口 | `core_fear` | `core_fear` | (缺失) | ❌ 需新增 |
| 致命弱点 | `fatal_flaw` | (缺失) | (缺失) | ❌ 需双端新增 |
| 说话风格 | `speaking_style` | `voice_style` | (缺失) | ❌ 需统一名并新增 |
| 灵魂弧光 | `arc_description` | `arc_start`/`arc_end` | `arc` | 🟡 需理顺映射关系 |

## 3. 其它重点审计项

- [ ] **项目创建**: 前端 `CreateProjectParams` 中的 `platforms` 字段与后端 `ProjectCreate` 的 `target_platforms` 字段名不统一。
- [ ] **流水线状态**: 前端 `PipelineTask` 和后端 `PipelineStatus` 对于进度标识（`percent` vs `progress`）存在拼写差异。
- [ ] **章节列表**: 后端 `Chapter` 使用 `chapter_num`，前端模板常用 `chapter_number`。

## 4. 修复路径图

1. **后端数据库模型升级**: 同步 `models.py` 补齐 12 维关键字段。
2. **前端类型定义升级**: 按照创作方法论重组 `types/index.ts`。
3. **API 适配器重构**: 优化 `api/app.py` 中的 `_normalize` 逻辑，确保数据透传。
4. **UI 组件适配**: 在角色详情页展示这些新属性。
