# TODO — 待办事项

## 后端
- [ ] schemas.py: 新增 book_title/book_synopsis/book_tags/book_category
- [ ] engine/metadata.py: 实现 generate_metadata()
- [ ] pipeline.py: outline 后插入 metadata 阶段
- [ ] project_store.py: 新增 save_metadata/get_metadata
- [ ] api/app.py: 新增 3 个 metadata API
- [ ] llm/prompts.py: 新增 METADATA prompt 模板

## 前端
- [ ] ProjectCreate.vue: Tab 1 添加书名输入框
- [ ] MetadataEditor.vue: 新建元数据编辑组件
- [ ] ProjectDetail.vue: 集成元数据面板
- [ ] api/index.ts: 新增 metadata API 函数
- [ ] types/index.ts: 新增 Metadata 类型
