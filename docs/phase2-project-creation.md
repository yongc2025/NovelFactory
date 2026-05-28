# Phase 2：项目创建参数详细设计

> 核心原则：最少输入启动，最多可选配置，为扩展留空间

---

## 一、参数分层设计

### Level 1：必填参数（3个字段即可启动）

| 参数 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| 灵感/前提 | `premise` | textarea | 一句话描述故事核心冲突，50-200字 |
| 目标平台 | `platforms` | multi-select | xiaohongshu / fanqie / comic_drama / short_drama |
| 篇幅定位 | `length_type` | radio | short(短篇) / medium(中篇) / long(长篇) |

### Level 2：题材定位（选填，影响模板和风格）

| 参数 | 字段名 | 类型 | 选项 | 说明 |
|------|--------|------|------|------|
| 大类 | `genre_major` | select | 古言/现代/玄幻/科幻/都市/年代/仙侠/末日 | 决定世界观基调 |
| 细分题材 | `genre_minor` | select | 根据大类动态变化 | 见题材矩阵表 |
| 目标读者 | `target_audience` | radio | female(女频)/male(男频)/general(通用) | 影响文风和爽点设计 |
| 内容基调 | `tone` | select | 爽文/虐文/甜文/悬疑/热血/治愈 | 影响情绪曲线设计 |

### Level 3：角色预设（选填，给AI约束）

| 参数 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| 主角名 | `protagonist_name` | input | 留空则AI命名 |
| 主角人设 | `protagonist_desc` | textarea | 一句话描述，如"被抛弃的真千金" |
| 反派名 | `antagonist_name` | input | 留空则AI设计 |
| 反派人设 | `antagonist_desc` | textarea | 一句话描述 |
| CP线 | `has_romance` | radio | yes/no/flexible |
| CP设定 | `romance_desc` | textarea | 可选，如"先婚后爱" |
| 配角数量 | `supporting_count` | number | 默认2-3，可调1-5 |

### Level 4：世界观约束（选填，限制AI发挥范围）

| 参数 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| 时空背景 | `world_setting` | select | 古代王朝/现代都市/架空世界/修仙界/末日/未来/自定义 |
| 自定义世界观 | `world_custom` | textarea | world_setting=自定义时启用 |
| 参考作品 | `reference_works` | textarea | 如"类似《知否》的宅斗+权谋" |
| 禁忌元素 | `forbidden_elements` | tag-input | 如"不要系统流/不要穿越" |

### Level 5：生成策略（高级，可全部用默认值）

| 参数 | 字段名 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| 目标字数 | `target_words` | number | 根据length_type自动 | 短篇5000/中篇50000/长篇200000 |
| 目标章节数 | `target_chapters` | number | 自动计算 | 可手动覆盖 |
| 每章字数范围 | `chapter_word_range` | range | [2000, 3000] | 短篇可设[1500, 2000] |
| 爽点密度 | `climax_density` | radio | medium | high/medium/low |
| 每几章一个小爽点 | `climax_interval` | number | 3 | 影响节奏设计 |
| 伏笔数量 | `foreshadow_count` | number | 5 | 大纲阶段埋设 |
| AI模型 | `model_provider` | radio | flash | flash/pro/mimo |
| 风格样本 | `style_sample` | textarea/file | 无 | 提供范文让AI学风格 |

---

## 二、题材矩阵（大类→细分动态联动）

```yaml
古言:
  - 重生复仇
  - 宅斗权谋
  - 甜宠宫斗
  - 穿书逆袭
  - 种田经商
  - 古言仙侠

现代:
  - 总裁豪门
  - 娱乐圈
  - 职场逆袭
  - 都市情感
  - 悬疑推理
  - 医疗/法律

玄幻:
  - 系统流
  - 重生修仙
  - 异世大陆
  - 灵异悬疑
  - 末日生存

科幻:
  - 星际
  - 赛博朋克
  - 时间循环
  - 末日废土

年代:
  - 70-80年代
  - 90年代经商
  - 年代重生

都市:
  - 校园
  - 职场
  - 家庭伦理
  - 情感婚姻
```

---

## 三、篇幅→参数自动映射

```yaml
short:  # 短篇（小红书为主）
  target_words: 5000
  target_chapters: 3
  chapter_word_range: [1500, 2000]
  climax_density: high
  foreshadow_count: 2
  platforms_default: [xiaohongshu]

medium:  # 中篇（番茄为主）
  target_words: 50000
  target_chapters: 20
  chapter_word_range: [2000, 3000]
  climax_density: medium
  foreshadow_count: 5
  platforms_default: [fanqie]

long:  # 长篇（番茄连载）
  target_words: 200000
  target_chapters: 80
  chapter_word_range: [2500, 4000]
  climax_density: medium
  foreshadow_count: 10
  platforms_default: [fanqie]

comic:  # 漫剧
  target_words: 80000
  target_episodes: 80
  episode_duration: [60, 120]  # 秒
  climax_density: high
  platforms_default: [comic_drama]
```

---

## 四、数据模型扩展

```python
# project 表新增字段
class ProjectCreate(BaseModel):
    # Level 1: 必填
    premise: str                    # 灵感/前提
    platforms: list[str]            # 目标平台
    length_type: str                # short/medium/long/comic

    # Level 2: 题材
    genre_major: str | None = None  # 大类
    genre_minor: str | None = None  # 细分
    target_audience: str = "female" # female/male/general
    tone: str | None = None         # 基调

    # Level 3: 角色预设
    protagonist_name: str | None = None
    protagonist_desc: str | None = None
    antagonist_name: str | None = None
    antagonist_desc: str | None = None
    has_romance: str = "flexible"   # yes/no/flexible
    romance_desc: str | None = None
    supporting_count: int = 3

    # Level 4: 世界观
    world_setting: str | None = None
    world_custom: str | None = None
    reference_works: str | None = None
    forbidden_elements: list[str] = []

    # Level 5: 策略
    target_words: int | None = None
    target_chapters: int | None = None
    chapter_word_range: list[int] = [2000, 3000]
    climax_density: str = "medium"
    climax_interval: int = 3
    foreshadow_count: int = 5
    model_provider: str = "flash"
    style_sample: str | None = None
```

---

## 五、Prompt 注入策略

创建项目后，这些参数需要注入到每个 AI 角色的 prompt 中：

```
策划经理：premise + platforms + genre + tone + target_audience
世界观架构师：world_setting + genre_major + world_custom + forbidden_elements
角色设计师：protagonist_desc + antagonist_desc + has_romance + supporting_count
大纲编剧：target_chapters + climax_density + climax_interval + foreshadow_count
正文作者：chapter_word_range + tone + style_sample + target_audience
编辑审校：platforms + forbidden_elements + target_audience
```

---

## 六、前端页面流程

```
Dashboard
  └── [新建项目] 按钮
        ↓
     创建向导（5步 Tab 页）
        ├── Tab 1: 必填（灵感 + 平台 + 篇幅）
        ├── Tab 2: 题材（大类 + 细分 + 读者 + 基调）
        ├── Tab 3: 角色（主角/反派/CP，可跳过）
        ├── Tab 4: 世界观（时空/参考/禁忌，可跳过）
        └── Tab 5: 策略（字数/章节/爽点/模型，全部可跳过）
        ↓
     [开始生成] → 进入项目详情页
```

**Tab 1 必填，Tab 2-5 可跳过用默认值。高级用户可以展开全部配置。**
