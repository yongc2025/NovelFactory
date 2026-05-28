# Copilot Instructions

本文件由 vibe-init 自动生成。Skills 来自母机 vibe-coding-cn。

## 通用规则

- 先读 .skills/ 下的 SKILL.md 再动手
- 遵循 AGENTS.md 中的行为准则
- 文档先行，接口先行，实现后补
- Debug 只给：预期 vs 实际 + 最小复现

## 已加载 Skills

### canvas-dev

---
name: canvas-dev
description: "Canvas白板驱动开发技能：Canvas白板作为唯一真相源，代码是其序列化形式。AI架构总师角色，自动生成富有洞察力的架构图。使用场景：生成架构白板、白板驱动编码、白板驱动重构、Code Review、团队协作、接手遗留项目。"
---


详细文档: .skills/canvas-dev/SKILL.md

### ddd-doc-steward

name: ddd-doc-steward
description: "文档驱动开发（DDD）文档管家：以仓库真实证据为准，盘点 ~/project 与 docs 目录，生成/更新 SSOT 文档（计划→补丁/全文→摘要→一致性检查）。触发：需要让文档与代码/配置/运行方式同步、补齐 guides/integrations/features/architecture/incidents/archive、无法推导时标注【待确认】并给验证路径。"
---

# DDD 文档管家 Skill

详细文档: .skills/ddd-doc-steward/SKILL.md

### headless-cli

---
name: headless-cli
description: "无头模式 AI CLI 调用技能：支持 Gemini/Claude/Codex CLI 的无交互批量调用，包含 YOLO 模式和安全模式。用于批量翻译、代码审查、多模型编排等场景。"
---


详细文档: .skills/headless-cli/SKILL.md

### skills-skills

---
name: skills-skills
description: "Claude Skills meta-skill: extract domain material (docs/APIs/code/specs) into a reusable Skill (SKILL.md + references/scripts/assets), and refactor existing Skills for clarity, activation reliability, and quality gates."
---


详细文档: .skills/skills-skills/SKILL.md

### snapdom

---
name: snapdom
description: snapDOM is a fast, accurate DOM-to-image capture tool that converts HTML elements into scalable SVG images. Use for capturing HTML elements, converting DOM to images (SVG, PNG, JPG, WebP), preserving styles, fonts, and pseudo-elements.
---


详细文档: .skills/snapdom/SKILL.md

### sop-generator

---
name: sop-generator
description: "标准作业程序（SOP）生成与规范化：将输入资料/需求/历史记录整理为可执行 SOP（结构化章节、步骤、控制点、异常处理、记录）。当用户要求“写 SOP/作业指导书/操作规程/流程说明”，或给出零散资料需要“整理成 SOP/流程”，或要求“按标准结构输出 SOP/质量检查”时使用。"
---


详细文档: .skills/sop-generator/SKILL.md

### workflow-engine

---
name: workflow-engine
description: "工作流引擎设计与实现。覆盖 Activiti、Flowable、Camunda、Temporal，支持 BPMN 流程建模、任务管理、表单引擎、流程监听、版本管理。适用于 Java/Go 企业级审批流、业务流程自动化。"
---


详细文档: .skills/workflow-engine/SKILL.md

