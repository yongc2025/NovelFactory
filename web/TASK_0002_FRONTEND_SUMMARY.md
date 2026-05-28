# Task 0002: 书籍元数据生成 — 前端部分 实现总结

## 已完成的修改

### 1. `web/src/types/index.ts` — 新增类型 ✅

**新增 BookMetadata 接口：**
```typescript
export interface BookMetadata {
  title: string
  title_candidates: string[]
  synopsis_short: string
  synopsis_medium: string
  synopsis_long: string
  tags: string[]
  category: string
  category_path: string
}
```

**更新 Project 接口：**
```typescript
export interface Project {
  // ... 原有字段
  book_title?: string
  book_synopsis?: string
  book_tags?: string[]
  book_category?: string
}
```

### 2. `web/src/api/index.ts` — 新增 API 函数 ✅

**新增三个元数据 API 函数：**
- `getMetadata(projectId: string)` - 获取书籍元数据
- `updateMetadata(projectId: string, metadata: Partial<BookMetadata>)` - 更新书籍元数据
- `regenerateMetadata(projectId: string)` - 重新生成书籍元数据

### 3. `web/src/views/ProjectCreate.vue` — Tab 1 添加书名字段 ✅

**在"基本信息"Tab 中添加书名输入框：**
- 位置：在"灵感/前提"输入框之后
- 组件：`<a-input>` 带字数统计（最大30字）
- 提示：留空则由AI为您起名
- 表单数据已更新为支持 `book_title` 字段

### 4. `web/src/components/project/MetadataEditor.vue` — 新建组件 ✅

**功能实现：**
- **书名区域**：显示当前书名 + "修改"按钮，点击弹出5个候选书名供选择
- **简介区域**：3个Tab切换（50字/150字/300字版本），每个都可编辑
- **标签区域**：Tag列表，可增删，支持动态添加
- **分类区域**：级联选择器，AI预选，用户可改
- **重新生成按钮**：整体重新生成（带确认对话框）
- **确认按钮**：确认元数据

**使用组件：**
- `<a-input>` 书名
- `<a-textarea>` 简介
- `<a-tag>` 标签（动态添加）
- `<a-cascader>` 分类选择
- `<a-tabs>` 简介版本切换
- `<a-button>` 重新生成

### 5. `web/src/views/ProjectDetail.vue` — 集成元数据面板 ✅

**新增内容：**
- 导入 `MetadataEditor` 组件
- 添加 `metadata` 到阶段名称映射
- 添加 `metadata` 到侧边导航菜单
- 添加 `metadata` Tab 的数据加载逻辑
- 添加元数据事件处理函数：
  - `onMetadataUpdate` - 更新元数据
  - `onMetadataRegenerate` - 重新生成元数据
  - `onMetadataConfirm` - 确认元数据
- 在大纲阶段之后、场景/正文阶段之前显示 MetadataEditor 组件

### 6. `web/src/stores/project.ts` — 扩展 store ✅

**新增状态：**
```typescript
const metadata = ref<BookMetadata | null>(null)
```

**新增操作：**
```typescript
async function fetchMetadata(projectId: string) { ... }
async function updateMetadata(projectId: string, data: Partial<BookMetadata>) { ... }
async function regenerateMetadata(projectId: string) { ... }
```

**更新 clearCurrent 函数：**
- 重置 `metadata.value = null`

### 7. `web/src/router/index.ts` — 新增路由 ✅

**新增路由：**
```typescript
{
  path: '/projects/:id/metadata',
  name: 'ProjectMetadata',
  component: () => import('@/views/ProjectDetail.vue'),
  meta: { title: '书籍元数据', tab: 'metadata' },
}
```

## 样式要求 ✅

- ✅ 使用 Ant Design Vue 组件
- ✅ 中文界面
- ✅ 暗色模式支持（通过 CSS 变量和 data-theme 选择器）
- ✅ `<script setup lang="ts">`

## TypeScript 类型检查

所有新增代码通过 TypeScript 类型检查。构建时出现的错误均为其他组件的预存问题，与本次修改无关。

## 测试建议

1. **创建项目时**：验证书名字段可以正常输入和保存
2. **项目详情页**：验证元数据 Tab 可以正常显示和切换
3. **元数据编辑**：验证所有功能：
   - 书名修改和候选选择
   - 简介三个版本的编辑和保存
   - 标签的添加和删除
   - 分类的级联选择
   - 重新生成功能（需后端支持）
   - 确认功能
4. **响应式布局**：验证在不同屏幕尺寸下的显示效果
5. **暗色模式**：验证在暗色主题下的显示效果

## 后端接口需求

前端实现依赖以下后端接口：

1. `GET /api/projects/{projectId}/metadata` - 获取书籍元数据
2. `PUT /api/projects/{projectId}/metadata` - 更新书籍元数据
3. `POST /api/projects/{projectId}/metadata/regenerate` - 重新生成书籍元数据

## 文件清单

```
web/src/types/index.ts                    # 类型定义
web/src/api/index.ts                      # API 函数
web/src/views/ProjectCreate.vue           # 创建项目页面
web/src/components/project/MetadataEditor.vue  # 元数据编辑组件（新建）
web/src/views/ProjectDetail.vue           # 项目详情页面
web/src/stores/project.ts                 # 项目状态管理
web/src/router/index.ts                   # 路由配置
```

## 实现时间

2026-05-28

## 状态

✅ 已完成
