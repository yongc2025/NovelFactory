# CONTEXT — 背景与上下文

## 业务背景

用户（个人创作者）要把小说发布到番茄/小红书等平台。每个平台都需要书籍元数据：
- **书名**：决定点击率的第一要素
- **简介**：50-500字，决定读者是否点进去看
- **标签**：3-5个，影响平台推荐算法
- **分类**：番茄有60+个分类标签

## 当前状态

- ProjectCreate 模型有 26 个参数，但**没有书名、简介、标签、分类**
- pipeline 生成完大纲后直接进入场景/正文，没有元数据生成步骤
- 前端 ProjectCreate.vue 没有书名输入框
- 番茄分类体系（GENRE_MATRIX）已定义但没有用于元数据生成

## 技术上下文

- 后端：`src/novel_factory/api/schemas.py` 定义 ProjectCreate
- 引擎：`src/novel_factory/engine/` 各角色模块
- 管线：`src/novel_factory/pipeline.py` 编排器
- 前端：`web/src/views/ProjectCreate.vue` 创建向导
