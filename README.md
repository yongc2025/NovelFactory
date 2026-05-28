# 🏭 NovelFactory — 自动化小说工厂

> 一个人的内容工厂 — 从一个想法，到全平台分发的多形态内容。

## 快速开始

```bash
# 1. 安装依赖
pip install -e ".[dev]"

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 3. 生成一个完整故事
novel-factory new "被渣男和闺蜜联手害死后重生到被害前3天" --words 8000

# 4. 或者分步操作
novel-factory plan "重生复仇打脸" --genre 重生 --chapters 10
novel-factory write <project_id>
novel-factory review <project_id>
```

## 项目结构

```
NovelFactory/
├── src/novel_factory/
│   ├── cli.py           # CLI 入口
│   ├── config.py        # 配置管理
│   ├── pipeline.py      # 编排器
│   ├── export.py        # 导出工具
│   ├── db/              # 数据层
│   ├── llm/             # LLM 调用层
│   └── engine/          # 叙事引擎（10个AI角色）
├── docs/                # 文档
├── data/                # SQLite 数据库
└── output/              # 生成的小说输出
```

## 技术栈

- Python 3.11+ / DeepSeek API / SQLite / Typer+Rich / Pydantic / Jinja2

## License

MIT
