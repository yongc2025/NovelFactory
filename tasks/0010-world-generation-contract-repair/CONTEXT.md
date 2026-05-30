# CONTEXT

现象：点击世界观页顶部“AI生成”后，世界观设定、关键地点、世界规则、约束条件没有有效内容。

初步原因：
- 世界观生成提示词要求 LLM 输出 `[{ category, content }]`。
- 前端 `WorldPanel` 读取扁平结构：`era/geography/power_system/social_structure/key_locations/rules/constraints`。
- 后端兼容转换只映射了 4 个文本字段，数组字段默认空数组。
- LLM 失败时占位世界观也只有 2 项，进一步造成页面内容缺失。
