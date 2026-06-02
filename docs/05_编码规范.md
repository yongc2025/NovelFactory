# NovelFactory 编码规范

> 适用范围：后端 Python + 前端 Vue 3/TypeScript
> 参考来源：Google Python Style Guide、PEP 8、Vue.js Style Guide、Airbnb、SonarQube

---

## 一、通用原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 一个函数做一件事，一个文件管一个领域 |
| **可读性 > 聪明** | 写给半年后的自己看，不是炫技 |
| **显式 > 隐式** | 参数类型要写，魔法数字要命名 |
| **早返回** | 用 guard clause 减少嵌套 |
| **命名即文档** | 看名字就知道干嘛，不用猜 |

---

## 二、后端 Python 规范

### 2.1 文件大小

| 指标 | 警告 | 上限 | 说明 |
|------|------|------|------|
| 文件行数 | 300 行 | 500 行 | 超过就拆模块 |
| 导入数量 | 15 个 | 20 个 | 超过说明职责过多 |

**超标处理**：
- 300-500 行：加 `# TODO: 文件过长，考虑拆分` 注释
- 500+ 行：必须拆分，提取子模块或工具函数

### 2.2 函数/方法大小

| 指标 | 警告 | 上限 | 说明 |
|------|------|------|------|
| 函数行数 | 30 行 | 50 行 | 不算空行和注释 |
| 参数个数 | 4 个 | 6 个 | 超过用 dataclass / Pydantic model |
| 圈复杂度 | 8 | 12 | if/for/while/except 每个分支 +1 |
| 嵌套层级 | 3 层 | 4 层 | 超过用早返回或提取函数 |

**超标处理**：
- 30-50 行：加 `# TODO: 函数过长，考虑拆分` 注释
- 50+ 行：必须拆分，提取子函数

### 2.3 类规范

| 指标 | 警告 | 上限 | 说明 |
|------|------|------|------|
| 类行数 | 200 行 | 400 行 | 不算空行 |
| 方法数量 | 10 个 | 15 个 | 超过说明职责过多 |
| 实例变量 | 6 个 | 10 个 | 超过用组合模式 |

### 2.4 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/文件 | snake_case | `project_store.py` |
| 类 | PascalCase | `ProjectStore` |
| 函数/方法 | snake_case | `get_project()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 私有 | _前缀 | `_internal_method()` |
| 类型变量 | PascalCase + T | `ModelT` |
| 布尔变量 | is_/has_/can_前缀 | `is_running`, `has_error` |

### 2.5 类型注解

```python
# ✅ 强制：函数签名必须有类型注解
async def get_project(project_id: str) -> dict[str, Any] | None:
    ...

# ✅ 强制：返回值不是 None 时必须标注
def calculate_score(values: list[float]) -> float:
    ...

# ✅ 可选：局部变量类型明显时可省略
name = "hello"  # 不需要 name: str = "hello"

# ❌ 禁止：Any 滥用
def process(data: Any) -> Any:  # 太模糊
    ...
```

### 2.6 Docstring

```python
# ✅ Google Style，中文撰写
async def match_markets(
    poly_markets: list[dict],
    kalshi_markets: list[dict],
    threshold: float = 0.6,
) -> list[MatchResult]:
    """匹配两个平台的市场。

    使用向量相似度初筛，再用结构化评分精排。

    Args:
        poly_markets: Polymarket 市场列表
        kalshi_markets: Kalshi 市场列表
        threshold: 匹配阈值，0-1

    Returns:
        匹配结果列表，按分数降序排列

    Raises:
        ValueError: threshold 不在 0-1 范围内
    """
```

**规则**：
- 公开函数/方法必须有 docstring
- 私有函数（`_` 前缀）可以没有
- 一行函数可以用单行 docstring：`"""返回项目列表。"""`
- 参数含义不明显时必须写 Args

### 2.7 异常处理

```python
# ✅ 精确捕获
try:
    result = await call_llm(messages)
except httpx.TimeoutException:
    logger.warning("LLM 调用超时，重试 %d/%d", retry, max_retry)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        await asyncio.sleep(backoff)
    else:
        raise

# ❌ 禁止：裸 except
try:
    result = await call_llm(messages)
except:  # 捕获一切，包括 KeyboardInterrupt
    pass

# ❌ 禁止：吞异常
try:
    result = await call_llm(messages)
except Exception:
    return None  # 静默失败，调试噩梦
```

### 2.8 异步规范

```python
# ✅ 异步函数用 async/await
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()

# ❌ 禁止：异步函数里阻塞调用
async def fetch_data(url: str) -> dict:
    resp = requests.get(url)  # 阻塞！会卡住整个事件循环
    return resp.json()

# ✅ 需要阻塞调用时用 asyncio.to_thread
async def read_file(path: Path) -> str:
    return await asyncio.to_thread(path.read_text, encoding="utf-8")
```

### 2.9 Ruff 配置

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "W",    # pycodestyle warnings
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "C4",   # flake8-comprehensions
    "RET",  # flake8-return
    "PTH",  # flake8-use-pathlib
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # 允许 __init__.py 中的重导出
```

---

## 三、前端 Vue 3 / TypeScript 规范

### 3.1 文件大小

| 指标 | 警告 | 上限 | 说明 |
|------|------|------|------|
| `.vue` 文件总行数 | 200 行 | 350 行 | template + script + style |
| `<script>` 行数 | 150 行 | 250 行 | 逻辑部分 |
| `<template>` 行数 | 80 行 | 150 行 | 模板部分 |
| `.ts` 文件行数 | 200 行 | 400 行 | 纯逻辑文件 |
| 组件内变量/函数 | 10 个 | 15 个 | 超过说明组件过大 |

**超标处理**：
- 提取子组件（拆 template）
- 提取 composable（拆逻辑）
- 提取 store（拆状态）
- 提取 utils（拆工具函数）

### 3.2 函数/方法大小

| 指标 | 警告 | 上限 | 说明 |
|------|------|------|------|
| 函数行数 | 25 行 | 40 行 | 不算空行 |
| 参数个数 | 3 个 | 5 个 | 超过用对象参数 |
| 回调嵌套 | 2 层 | 3 层 | 超过提取函数 |
| watch/computed 行数 | 10 行 | 20 行 | 复杂逻辑提取为函数 |

### 3.3 组件规范

```vue
<!-- ✅ 标准结构顺序 -->
<script setup lang="ts">
// 1. 类型导入
import type { Project } from '@/types'

// 2. 组件导入
import ProjectCard from './ProjectCard.vue'

// 3. Store / composable
const projectStore = useProjectStore()

// 4. Props / Emits
const props = defineProps<{ project: Project }>()
const emit = defineEmits<{ select: [id: string] }>()

// 5. 响应式状态
const loading = ref(false)

// 6. 计算属性
const isActive = computed(() => props.project.status === 'running')

// 7. 方法
function handleClick() {
  emit('select', props.project.id)
}

// 8. 生命周期
onMounted(() => { ... })
</script>

<template>
  <!-- 模板 -->
</template>

<style scoped>
/* 样式 */
</style>
```

### 3.4 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `ProjectCard.vue` |
| composable | use 前缀 | `useProjectStore()` |
| 工具函数 | camelCase | `formatDate()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 类型/接口 | PascalCase | `ProjectCreateParams` |
| Props | camelCase | `projectData` |
| Events | kebab-case | `@update-value` |
| CSS 类 | kebab-case | `.project-card` |
| 布尔变量 | is/has/can 前缀 | `isLoading`, `hasError` |

### 3.5 TypeScript 规范

```typescript
// ✅ 强制：接口定义 Props
const props = defineProps<{
  project: Project
  editable?: boolean
}>()

// ✅ 强制：事件定义用具名元组
const emit = defineEmits<{
  select: [id: string]
  delete: [id: string]
}>()

// ✅ 强制：API 返回值有类型
async function fetchProject(id: string): Promise<Project> {
  const res = await api.getProject(id)
  return res.data.data
}

// ❌ 禁止：any 滥用
function process(data: any): any { ... }

// ✅ 用 unknown + 类型守卫
function process(data: unknown): Result {
  if (typeof data === 'object' && data !== null && 'id' in data) {
    return handleProject(data as Project)
  }
  throw new Error('Invalid data')
}
```

### 3.6 响应式状态

```typescript
// ✅ 简单值用 ref
const count = ref(0)
const name = ref('hello')

// ✅ 复杂对象用 reactive
const form = reactive({
  title: '',
  content: '',
  tags: [] as string[],
})

// ❌ 禁止：解构 reactive（会丢失响应性）
const { title, content } = form  // 失去响应性！

// ✅ 用 toRefs
const { title, content } = toRefs(form)

// ✅ 命名约定：ref 不需要 .value 后缀
const loading = ref(false)  // 不是 isLoadingRef
```

### 3.7 Composable 规范

```typescript
// ✅ 标准 composable 结构
export function useProjectDetail(projectId: Ref<string>) {
  // 状态
  const project = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isActive = computed(() => project.value?.status === 'running')

  // 方法
  async function fetch() {
    loading.value = true
    try {
      project.value = await api.getProject(projectId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  // 生命周期
  onMounted(fetch)
  watch(projectId, fetch)

  // 返回（只暴露需要的）
  return { project, loading, error, isActive, fetch }
}
```

**规则**：
- composable 返回对象，不返回数组（便于解构命名）
- 内部用 ref，外部暴露 ref（不自动 unwrap）
- 复杂 composable 不超过 100 行

### 3.8 模板规范

```vue
<template>
  <!-- ✅ 简单条件 -->
  <div v-if="loading" class="skeleton" />

  <!-- ✅ 列表渲染带 key -->
  <ProjectCard
    v-for="item in projects"
    :key="item.id"
    :project="item"
    @select="handleSelect"
  />

  <!-- ❌ 禁止：模板中写复杂逻辑 -->
  <div>{{ items.filter(i => i.active).sort((a,b) => b.score - a.score).slice(0, 5).map(i => i.name).join(', ') }}</div>

  <!-- ✅ 提取为 computed -->
  <div>{{ topActiveNames }}</div>
</template>
```

### 3.9 样式规范

```vue
<style scoped>
/* ✅ 使用 Less 变量 */
.card {
  background: @surface-color;
  border-radius: @radius-md;
  padding: @spacing-4;
  transition: all @duration-normal;
}

/* ✅ BEM 命名（可选但推荐） */
.card__header { }
.card__body { }
.card--active { }

/* ❌ 禁止：深度选择器滥用 */
:deep(.ant-card) { }  /* 仅在覆盖 Ant Design 时使用 */
</style>
```

---

## 四、API / 数据规范

### 4.1 后端 API 响应格式

```python
# ✅ 统一响应格式
{
    "code": 200,
    "message": "success",
    "data": { ... }
}

# ✅ 错误响应
{
    "code": 400,
    "message": "参数错误: premise 不能为空",
    "data": null
}
```

### 4.2 前端 API 调用

```typescript
// ✅ 统一错误处理
async function safeCall<T>(fn: () => Promise<AxiosResponse<T>>): Promise<T> {
  try {
    const res = await fn()
    return res.data.data
  } catch (e: any) {
    message.error(e.response?.data?.message || e.message)
    throw e
  }
}

// ✅ 使用
const project = await safeCall(() => api.getProject(id))
```

---

## 五、Git 提交规范

```
<type>(<scope>): <description>

类型：
  feat     新功能
  fix      修复
  refactor 重构
  style    样式调整
  docs     文档
  test     测试
  chore    构建/工具

示例：
  feat(web): 新增引导式灵感创建流程
  fix(api): 修复流水线状态丢失问题
  refactor(engine): 拆分 writer.py 超长函数
  style(web): Dashboard 卡片暗色主题
  docs: 更新编码规范
```

---

## 六、代码审查清单

### Python
- [ ] 函数 < 50 行？
- [ ] 参数 < 6 个？
- [ ] 有类型注解？
- [ ] 有 docstring（公开函数）？
- [ ] 没有裸 except？
- [ ] 没有阻塞调用在 async 函数中？
- [ ] ruff check 通过？

### Vue/TypeScript
- [ ] 组件 < 350 行？
- [ ] script < 250 行？
- [ ] 函数 < 40 行？
- [ ] 没有 any？
- [ ] Props 有类型定义？
- [ ] 模板无复杂逻辑？
- [ ] 没有解构 reactive？
- [ ] npm run lint 通过？

---

## 七、工具配置

### 后端（Ruff）
```toml
# pyproject.toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "C4", "RET", "PTH"]
```

### 前端（ESLint + Prettier）
```json
// .eslintrc.cjs（建议配置）
{
  "extends": [
    "plugin:vue/vue3-recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier"
  ],
  "rules": {
    "vue/max-attributes-per-line": ["error", { "singleline": 3 }],
    "vue/singleline-element-content-newline": "off",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### Pre-commit Hook（建议）
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-eslint
    hooks:
      - id: eslint
        files: web/src/
```
