# 任务包标准模板 (TASK_TEMPLATE)

每个 P0/P1 级任务包应包含以下结构：

```
tasks/ID-slug/
├── DESIGN.md          # 核心：技术设计方案（方案确认后产出）
├── CHECKLIST.md       # 进度：细化到函数级的开发清单
├── TEST_REPORT.md     # 质量：单元测试、集成测试或视觉验收截图
└── (relevant_assets)  # 其他：该任务相关的 Mock 数据或临时参考
```

## 1. DESIGN.md 必须包含：
- 修改的文件清单
- 核心逻辑变更描述
- 新增的数据结构/接口协议

## 2. 工作流要求：
- **禁止直接在代码中寻找逻辑**：先读任务包内的 DESIGN.md。
- **开发过程同步**：每完成一个函数，更新 CHECKLIST.md。
- **任务结束闭环**：产出 TEST_REPORT.md 后，方可标记任务为 `completed`。
