# 前端 UI 审计报告

## 1. 整体评分 + 一句话结论

**综合评分：6.5 / 10**

功能骨架完整、核心流程闭环，但 ProjectDetail.vue 过度膨胀（1223 行 / 49KB）严重违反编码规范，交互一致性不足，批量任务体验粗糙，多个 UX 细节需补齐。

---

## 2. 页面/组件结构概览

| 视图 | 行数 | 职责 | 评价 |
|------|------|------|------|
| Dashboard.vue | 584 | 项目列表+统计+筛选 | OK 结构清晰，响应式完整 |
| ProjectDetail.vue | 1223 | 项目详情+9个Tab+流水线 | FAIL 严重超限，应拆分 |
| ProjectCreate.vue | 886 | 引导式创建 | WARN 偏大但可接受 |
| TopicCard.vue | ~200 | 选题卡片 | OK 内聚合理 |
| WorldPanel.vue | ~180 | 世界观展示/编辑 | OK 内聚合理 |
| CharacterCard.vue | ~210 | 角色卡片 | OK 内聚合理 |
| OutlineEditor.vue | 406 | 大纲编辑 | WARN 略超 350 行上限 |
| MetadataEditor.vue | 482 | 元数据编辑 | FAIL 超过 350 行上限 |
| ChapterReader.vue | ~160 | 章节阅读 | OK 精简 |
| ReviewReport.vue | ~120 | 审校报告 | OK 精简 |
| PipelineProgress.vue | ~160 | 流水线进度 | OK 设计良好 |
| StageConfirm.vue | ~70 | 阶段确认 | OK 最小化 |
| useTaskPoller.ts | ~130 | 任务轮询 | OK 逻辑清晰 |

**关键结构问题**：
- `ProjectDetail.vue` 1223 行 >> AGENTS.md 规定的 `.vue` 上限 350 行（超标 3.5 倍）
- 9 个 Tab 的内容全部内联在同一文件，应拆为独立组件或 composable
- `script setup` 约 420 行 >> 上限 250 行

---

## 3. 交互一致性问题

| # | 场景 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| C1 | 选题采用 | 点击「采用此方案」后自动走 approve 流程 | OK 实现 handleTopicSelect -> approve | TopicCard.vue:58 / ProjectDetail.vue:316 |
| C2 | 世界观编辑 | 顶部操作栏「编辑」切换编辑态 | OK 一致 | ProjectDetail.vue:172 |
| C3 | 角色编辑 | 卡片内置编辑按钮（无顶部编辑按钮） | FAIL 与世界观交互不一致 | CharacterCard.vue / ProjectDetail.vue:188 |
| C4 | 大纲编辑 | 两套编辑入口（顶部「编辑全部」+ 表格内联） | WARN 操作模式差异大 | OutlineEditor.vue / ProjectDetail.vue:206 |
| C5 | 场景细纲 | 缺少编辑/确认能力，只读展示 | FAIL 无法交互，与其他 Tab 不一致 | ProjectDetail.vue:230-243 |
| C6 | 元数据编辑 | 卡片内直接编辑（书名/简介/标签/分类） | OK 但无顶部操作栏的「采用」按钮依赖 StageConfirm | MetadataEditor.vue |
| C7 | 正文阅读 | 顶部有「采用」+「AI生成」 | OK 一致 | ProjectDetail.vue:254 |
| C8 | 审校报告 | 顶部有「采用」+「AI生成」 | OK 但「采用审校报告」语义不明 | ProjectDetail.vue:269 |
| C9 | StageConfirm 位置 | 固定在内容底部 | OK sticky top:80px | ProjectDetail.vue CSS |
| C10 | Tab 切换数据加载 | 每个 Tab 切换自动加载 | OK watch activeTab 触发 | ProjectDetail.vue:124 |
| C11 | 表单取消语义 | 统一「取消」返回查看态 | OK 所有组件一致 | 各组件 |

---

## 4. 关键 UX 风险

### P0 -- 必须修复

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P0-1 | **ProjectDetail.vue 1223 行** | ProjectDetail.vue | 严重违反编码规范，维护成本极高，任何修改可能引入回归 | 拆分：每个 Tab 抽独立组件 + composable 提取逻辑 |
| P0-2 | **场景细纲 Tab 无编辑/确认** | ProjectDetail.vue:230-243 | 场景数据只读展示，无 StageConfirm、无「采用」按钮，用户无法完成场景阶段流程 | 补充 StageConfirm + 编辑/确认交互 |
| P0-3 | **场景细纲逐章串行加载** | ProjectDetail.vue:131-134 | `for (const ch of ...) { await loadSceneData(ch) }` 大纲 50+ 章时极慢 | 改为并行加载或按需加载 |

### P1 -- 重要改进

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P1-1 | **全局 Loading 遮罩过重** | ProjectDetail.vue:148 | 任何加载（含切换 Tab、fetch 数据）都会遮住全部内容，用户无法浏览已加载内容 | 区分首次加载 vs 增量加载；Tab 切换时仅对新内容区域加载 |
| P1-2 | **store.loading 共享状态** | stores/project.ts:27 | 所有 fetch 函数共享同一个 loading ref，并发请求会互相覆盖 | 每个 fetch 维护独立 loading 状态，或使用请求级 loading |
| P1-3 | **大纲批量生成无进度反馈** | ProjectDetail.vue:248-268 | 仅显示 "正在生成第 N-M 章大纲..."，实际进度依赖 taskPoller，进度文本不够细 | 增加章级别进度（"正在生成第 X 章..."） |
| P1-4 | **大纲删除操作无确认** | ProjectDetail.vue:197 `deleteOutlineChapter` | 单章删除无 Popconfirm，误触风险 | 添加 Popconfirm |
| P1-5 | **操作日志硬编码** | ProjectDetail.vue:367 | `operationLogs` 为模拟数据，无实际功能 | 接入真实日志或移除此卡片 |
| P1-6 | **正文导航只支持上一章/下一章** | ChapterReader.vue + ProjectDetail.vue | 无法跳转到指定章节，50+ 章时体验差 | 添加章节选择器（下拉/抽屉列表） |
| P1-7 | **MetadataEditor.vue 482 行** | MetadataEditor.vue | 超过 .vue 上限 350 行 | 拆分：书名编辑、简介编辑、标签编辑为子组件 |

### P2 -- 体验优化

| # | 风险 | 位置 | 影响 | 建议 |
|---|------|------|------|------|
| P2-1 | **大纲编辑器与 ProjectDetail 大纲表格功能重叠** | OutlineEditor.vue vs ProjectDetail.vue:206-230 | 两套大纲展示/编辑模式，用户可能混淆 | 统一为一套，或明确场景区分 |
| P2-2 | **审校报告「采用」语义不清** | ProjectDetail.vue:271 | 审校报告的「采用」含义是什么？标记审校通过？ | 明确按钮文案为「确认通过」或移除 |
| P2-3 | **响应式断点时右侧面板直接隐藏** | ProjectDetail.vue CSS `@media (max-width: 1024px)` | 窄屏时任务状态、操作日志完全不可见 | 改为底部面板或可折叠侧栏 |
| P2-4 | **Tab 切换路由驱动但无缓存** | ProjectDetail.vue:115 onTabChange | 每次切回 Tab 都重新 fetch，大纲/正文等大数据频繁加载 | 引入 KeepAlive 或组件级缓存 |
| P2-5 | **章节列表无虚拟滚动** | ProjectDetail.vue:218 | 100+ 章大纲表格虽已分页 pageSize=10，切换页面仍需重新渲染 | 当前分页方案可接受，50+ 章时考虑虚拟滚动 |
| P2-6 | **Dashboard 统计卡片总字数计算不准确** | Dashboard.vue:61-68 | 未完成项目字数硬算 80%，完全不准确 | 改为后端返回实际字数统计 |
| P2-7 | **API 拦截器全局 message.error** | api/index.ts:29 | 所有 API 错误弹出全局 message，与组件内 catch 的 message.error 双重提示 | 拦截器仅标记 error，由调用方决定是否展示 |
| P2-8 | **大纲分页控件原始** | ProjectDetail.vue:226-229 | 手动实现上一页/下一页，无页码跳转 | 使用 Ant Design Pagination 组件 |
| P2-9 | **TopicCard platforms 兼容逻辑散落** | TopicCard.vue:28-33 + ProjectDetail.vue fetchTopic | 多处兼容旧数据字符串格式 | 在 API 层或 store 层统一适配 |

---

## 5. 视觉规范遵守度

### 按钮配色

| 规范 | 期望 | 实际 | 评价 |
|------|------|------|------|
| 「AI生成」按钮 | 紫色/黄色 | 黄色 (btn-generate: #ffd666) | WARN 规范说紫色/绿色/蓝色，实际用了黄色系 |
| 「采用」按钮 | 绿色 | 绿色 (btn-adopt: #f6ffed + #b7eb8f) | OK 符合 |
| 「编辑」按钮 | 蓝色 | 蓝色 (btn-edit: #e6f4ff + #91caff) | OK 符合 |
| 「取消」按钮 | 灰色 | 灰色 (btn-cancel: #ffffff + #d9d9d9) | OK 符合 |
| StageConfirm 「编辑反馈」 | 蓝色 | 默认样式（无特殊配色） | FAIL 未遵循 btn-edit 配色 |
| StageConfirm 「重新生成」 | 危险红色 | danger 红色 | OK 符合 |

**结论**：配色体系基本建立，但「AI生成」按钮用黄色而非规范中的紫色，StageConfirm 内按钮未统一配色。

### 空状态

| Tab | 实现 | 评价 |
|-----|------|------|
| 选题 | 虚线卡片占位 x3 | OK 符合规范 |
| 世界观 | 虚线卡片占位 x2 | OK 符合规范 |
| 角色 | 虚线头像+卡片占位 x3 | OK 符合规范 |
| 大纲 | Ant Empty 组件 | FAIL 不符合虚线卡片规范 |
| 场景 | Ant Empty 组件 | FAIL 不符合虚线卡片规范 |
| 元数据 | 虚线卡片占位 x1 | OK 符合规范 |
| 正文 | 虚线占位 x5 | OK 符合规范 |
| 审校 | 虚线卡片占位 x1 | OK 符合规范 |

### Loading 状态

| 场景 | 实现 | 评价 |
|------|------|------|
| 全局加载 | `<Spin :spinning="globalLoading">` 遮罩 | WARN 过重，阻止交互 |
| 组件内加载 | WorldPanel/ChapterReader 等 `<Spin :spinning="loading">` | OK 合理但与全局遮罩叠加 |
| 顶部操作栏 | 顶部按钮 loading 状态 | OK 良好 |
| TaskPoller 进度 | 右侧面板 Progress + 文字 | OK 良好 |

### 三层结构遵守度

| Tab | 顶部操作栏 | 内容区 | StageConfirm | 评价 |
|-----|-----------|--------|-------------|------|
| 选题 | OK 有 | OK TopicCard | OK 有 | OK 完整 |
| 世界观 | OK 有 | OK WorldPanel | OK 有 | OK 完整 |
| 角色 | OK 有 | OK CharacterCard | OK 有 | OK 完整 |
| 大纲 | OK 有 | OK Table + OutlineEditor | OK 有 | WARN 两套内容展示 |
| 场景 | OK 有（仅AI生成） | OK Collapse | FAIL 无 | FAIL 不完整 |
| 元数据 | OK 有 | OK MetadataEditor | OK 有 | OK 完整 |
| 正文 | OK 有 | OK ChapterReader | OK 有 | OK 完整 |
| 审校 | OK 有 | OK ReviewReport | OK 有 | OK 完整 |

---

## 6. 改进建议（优先级排序，可立即落地）

### [RED] 立即修复（1-2 天）

1. **拆分 ProjectDetail.vue**：将 9 个 Tab 的内容抽为独立组件（如 TopicTab.vue、WorldTab.vue 等），核心逻辑提取到 useProjectDetail.ts composable
   - 目标：ProjectDetail.vue < 300 行，每个 Tab 组件 < 200 行
   - 预期收益：可维护性大幅提升，符合编码规范

2. **场景细纲 Tab 补全**：添加 StageConfirm + 采用按钮，与其他 Tab 对齐

3. **场景数据并行加载**：将串行 `for await` 改为 Promise.all + 限流（如 p-limit 5 并发）

4. **大纲单章删除添加 Popconfirm**：deleteOutlineChapter 函数调用前添加确认

### [YELLOW] 本周完成（3-5 天）

5. **拆分 store.loading**：引入 per-request loading（如 topicLoading、worldLoading），Tab 切换仅显示当前 Tab 的 loading

6. **减少全局 Loading 遮罩范围**：首次进入显示全局 Spin，Tab 切换时仅在内容区域显示 skeleton/spin

7. **添加章节跳转选择器**：在正文阅读 Tab 添加章节下拉选择

8. **统一「AI生成」按钮配色**：将 btn-generate 改为紫色系（#6C5CE7 -> #A29BFE），与 Dashboard 统计卡片主色一致

9. **StageConfirm 按钮配色统一**：编辑反馈用 btn-edit，重新生成用 danger

10. **统一空状态组件**：大纲/场景 Tab 的空状态改为虚线卡片占位

### [GREEN] 后续迭代（1-2 周）

11. **Tab 切换缓存**：使用 KeepAlive 缓存已加载的 Tab 组件

12. **移除操作日志硬编码**：接入后端日志 API 或删除此卡片

13. **大纲分页改用 Ant Pagination**：替换手动分页控件

14. **API 拦截器优化**：移除全局 message.error，由调用方控制错误提示

15. **MetadataEditor 拆分**：将书名/简介/标签/分类拆为子组件

16. **窄屏响应式优化**：右侧面板改为可折叠/底部抽屉

17. **Dashboard 总字数统计**：改为后端返回真实数据

18. **TypeScript 类型覆盖率提升**：移除 any 用法（如 onTopicUpdate(data: any)、onWorldUpdate(data: any) 等），使用具体类型

---

## 附录：代码指标快照

| 文件 | 行数 | AGENTS 限制 | 超标倍数 |
|------|------|------------|---------|
| ProjectDetail.vue | 1223 | 350 | 3.5x |
| ProjectCreate.vue | 886 | 350 | 2.5x |
| MetadataEditor.vue | 482 | 350 | 1.4x |
| OutlineEditor.vue | 406 | 350 | 1.2x |
| Dashboard.vue | 584 | 350 | 1.7x |

**TypeScript `any` 用法统计**（关键文件）：
- ProjectDetail.vue：onTopicUpdate(data: any)、onWorldUpdate(data: any)、onCharacterUpdate(data: any)、onOutlineUpdate(data: any)、onChapterUpdate(data: any)、outlineDrawerChapter = ref<any>(null)
- stores/project.ts：updateTopicData(projectId, data: any)、updateWorldData(projectId, data: any) 等
- api/index.ts：多个 ApiResponse<any> 返回类型

**国际化/可访问性**：无 i18n 支持，无 ARIA 标签，无键盘导航优化。
