<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  Card,
  Button,
  Input,
  Tag,
  Tabs,
  Cascader,
  Space,
  Tooltip,
  Modal,
  Spin,
  message,
} from 'ant-design-vue'
import {
  EditOutlined,
  ReloadOutlined,
  PlusOutlined,
  CloseOutlined,
  CheckOutlined,
  StarOutlined,
} from '@ant-design/icons-vue'
import type { BookMetadata } from '@/types'

const props = defineProps<{
  projectId: string
  metadata: BookMetadata | null
}>()

const emit = defineEmits<{
  (e: 'update', metadata: Partial<BookMetadata>): void
  (e: 'regenerate'): void
  (e: 'confirm'): void
}>()

// 状态
const editingTitle = ref(false)
const editTitleValue = ref('')
const showTitleCandidates = ref(false)
const activeSynopsisTab = ref('short')
const newTagInput = ref('')
const showTagInput = ref(false)
const localMetadata = ref<BookMetadata | null>(null)
const regenerating = ref(false)

// 分类级联选项（示例数据，实际应从后端获取）
const categoryOptions = [
  {
    value: 'fiction',
    label: '小说',
    children: [
      {
        value: 'fantasy',
        label: '玄幻',
        children: [
          { value: 'xuanhuan', label: '玄幻奇幻' },
          { value: 'xiuzhen', label: '修真仙侠' },
          { value: 'dushi', label: '都市异能' },
        ],
      },
      {
        value: 'romance',
        label: '言情',
        children: [
          { value: 'gudai', label: '古代言情' },
          { value: 'xiandai', label: '现代言情' },
          { value: 'chuanyue', label: '穿越重生' },
        ],
      },
      {
        value: 'scifi',
        label: '科幻',
        children: [
          { value: 'space', label: '星际文明' },
          { value: 'cyber', label: '赛博朋克' },
          { value: 'apocalypse', label: '末世生存' },
        ],
      },
      {
        value: 'mystery',
        label: '悬疑',
        children: [
          { value: 'detective', label: '侦探推理' },
          { value: 'horror', label: '灵异恐怖' },
          { value: 'suspense', label: '悬疑惊悚' },
        ],
      },
    ],
  },
  {
    value: 'nonfiction',
    label: '非虚构',
    children: [
      { value: 'history', label: '历史' },
      { value: 'biography', label: '传记' },
      { value: 'science', label: '科普' },
    ],
  },
]

// 监听 metadata 变化
watch(
  () => props.metadata,
  (val) => {
    if (val) {
      localMetadata.value = { ...val }
    }
  },
  { immediate: true }
)

// 简介内容计算属性
const currentSynopsis = computed({
  get() {
    if (!localMetadata.value) return ''
    switch (activeSynopsisTab.value) {
      case 'short':
        return localMetadata.value.synopsis_short
      case 'medium':
        return localMetadata.value.synopsis_medium
      case 'long':
        return localMetadata.value.synopsis_long
      default:
        return ''
    }
  },
  set(val: string) {
    if (!localMetadata.value) return
    switch (activeSynopsisTab.value) {
      case 'short':
        localMetadata.value.synopsis_short = val
        break
      case 'medium':
        localMetadata.value.synopsis_medium = val
        break
      case 'long':
        localMetadata.value.synopsis_long = val
        break
    }
  },
})

// 书名候选
const titleCandidates = computed(() => {
  return localMetadata.value?.title_candidates || []
})

// 标签
const tags = computed(() => {
  return localMetadata.value?.tags || []
})

// 分类路径
const categoryPath = computed({
  get() {
    if (!localMetadata.value?.category_path) return []
    return localMetadata.value.category_path.split('/')
  },
  set(val: string[]) {
    if (localMetadata.value) {
      localMetadata.value.category_path = val.join('/')
      localMetadata.value.category = val[val.length - 1] || ''
    }
  },
})

// 编辑书名
function startEditTitle() {
  editTitleValue.value = localMetadata.value?.title || ''
  editingTitle.value = true
}

function saveTitle() {
  if (localMetadata.value && editTitleValue.value.trim()) {
    localMetadata.value.title = editTitleValue.value.trim()
    emit('update', { title: localMetadata.value.title })
  }
  editingTitle.value = false
}

function cancelEditTitle() {
  editingTitle.value = false
}

// 选择候选书名
function selectTitleCandidate(title: string) {
  if (localMetadata.value) {
    localMetadata.value.title = title
    emit('update', { title })
  }
  showTitleCandidates.value = false
}

// 标签操作
function addTag() {
  const tag = newTagInput.value.trim()
  if (tag && localMetadata.value && !localMetadata.value.tags.includes(tag)) {
    localMetadata.value.tags.push(tag)
    emit('update', { tags: [...localMetadata.value.tags] })
  }
  newTagInput.value = ''
  showTagInput.value = false
}

function removeTag(tag: string) {
  if (localMetadata.value) {
    localMetadata.value.tags = localMetadata.value.tags.filter((t) => t !== tag)
    emit('update', { tags: [...localMetadata.value.tags] })
  }
}

// 分类变更
function onCategoryChange(value: any) {
  const stringValues = Array.isArray(value) ? value.map(String) : []
  categoryPath.value = stringValues
  emit('update', {
    category: stringValues[stringValues.length - 1] || '',
    category_path: stringValues.join('/'),
  })
}

// 保存简介
function saveSynopsis() {
  if (localMetadata.value) {
    emit('update', {
      synopsis_short: localMetadata.value.synopsis_short,
      synopsis_medium: localMetadata.value.synopsis_medium,
      synopsis_long: localMetadata.value.synopsis_long,
    })
    message.success('简介已保存')
  }
}

// 重新生成
async function handleRegenerate() {
  Modal.confirm({
    title: '确认重新生成',
    content: '重新生成将覆盖当前所有元数据，是否继续？',
    onOk: async () => {
      regenerating.value = true
      try {
        emit('regenerate')
      } finally {
        regenerating.value = false
      }
    },
  })
}

// 确认元数据
function handleConfirm() {
  emit('confirm')
  message.success('元数据已确认')
}
</script>

<template>
  <Spin :spinning="!localMetadata">
    <div class="metadata-editor" v-if="localMetadata">
      <!-- 书名区域 -->
      <Card class="metadata-section" size="small">
        <template #title>
          <Space>
            <span>📚 书名</span>
            <Tooltip title="查看AI推荐书名">
              <Button
                type="link"
                size="small"
                @click="showTitleCandidates = !showTitleCandidates"
              >
                <StarOutlined /> 候选书名
              </Button>
            </Tooltip>
          </Space>
        </template>

        <div class="title-area">
          <div v-if="!editingTitle" class="title-display">
            <span class="title-text">{{ localMetadata.title }}</span>
            <Button type="link" size="small" @click="startEditTitle">
              <EditOutlined /> 修改
            </Button>
          </div>
          <div v-else class="title-edit">
            <Input
              v-model:value="editTitleValue"
              placeholder="输入书名"
              :maxlength="30"
              show-count
              @press-enter="saveTitle"
            />
            <Space>
              <Button type="primary" size="small" @click="saveTitle">
                <CheckOutlined /> 保存
              </Button>
              <Button size="small" @click="cancelEditTitle">取消</Button>
            </Space>
          </div>
        </div>

        <!-- 候选书名列表 -->
        <div v-if="showTitleCandidates" class="title-candidates">
          <div class="candidates-header">AI 推荐书名：</div>
          <Space wrap>
            <Tag
              v-for="candidate in titleCandidates"
              :key="candidate"
              :color="candidate === localMetadata.title ? 'blue' : 'default'"
              class="candidate-tag"
              @click="selectTitleCandidate(candidate)"
            >
              {{ candidate }}
            </Tag>
          </Space>
        </div>
      </Card>

      <!-- 简介区域 -->
      <Card class="metadata-section" size="small">
        <template #title>
          <Space>
            <span>📝 简介</span>
            <Button type="link" size="small" @click="saveSynopsis">
              <CheckOutlined /> 保存简介
            </Button>
          </Space>
        </template>

        <Tabs v-model:activeKey="activeSynopsisTab" type="card">
          <Tabs.TabPane key="short" tab="50字版本">
            <Input.TextArea
              v-model:value="localMetadata.synopsis_short"
              :rows="3"
              placeholder="50字左右的简介"
              :maxlength="100"
              show-count
            />
          </Tabs.TabPane>
          <Tabs.TabPane key="medium" tab="150字版本">
            <Input.TextArea
              v-model:value="localMetadata.synopsis_medium"
              :rows="5"
              placeholder="150字左右的简介"
              :maxlength="300"
              show-count
            />
          </Tabs.TabPane>
          <Tabs.TabPane key="long" tab="300字版本">
            <Input.TextArea
              v-model:value="localMetadata.synopsis_long"
              :rows="8"
              placeholder="300字左右的简介"
              :maxlength="600"
              show-count
            />
          </Tabs.TabPane>
        </Tabs>
      </Card>

      <!-- 标签区域 -->
      <Card class="metadata-section" size="small">
        <template #title>
          <Space>
            <span>🏷️ 标签</span>
            <span class="tag-hint">（点击标签可删除）</span>
          </Space>
        </template>

        <div class="tags-area">
          <Space wrap>
            <Tag
              v-for="tag in tags"
              :key="tag"
              closable
              color="blue"
              @close="removeTag(tag)"
            >
              {{ tag }}
            </Tag>
            <div v-if="showTagInput" class="tag-input-wrapper">
              <Input
                v-model:value="newTagInput"
                size="small"
                placeholder="输入标签"
                style="width: 100px"
                @press-enter="addTag"
                @blur="addTag"
              />
            </div>
            <Button
              v-else
              type="dashed"
              size="small"
              @click="showTagInput = true"
            >
              <PlusOutlined /> 添加标签
            </Button>
          </Space>
        </div>
      </Card>

      <!-- 分类区域 -->
      <Card class="metadata-section" size="small">
        <template #title>
          <span>📂 分类</span>
        </template>

        <div class="category-area">
          <div class="category-current">
            当前分类：
            <Tag color="purple" v-if="localMetadata.category">
              {{ localMetadata.category_path || localMetadata.category }}
            </Tag>
            <span v-else class="no-category">未设置</span>
          </div>
          <Cascader
            :value="categoryPath"
            :options="categoryOptions"
            placeholder="选择分类"
            style="width: 300px"
            @change="onCategoryChange"
          />
        </div>
      </Card>

      <!-- 操作按钮 -->
      <div class="metadata-actions">
        <Space>
          <Button @click="handleRegenerate" :loading="regenerating">
            <ReloadOutlined /> 重新生成
          </Button>
          <Button type="primary" @click="handleConfirm">
            <CheckOutlined /> 确认元数据
          </Button>
        </Space>
      </div>
    </div>
  </Spin>
</template>

<style scoped>
.metadata-editor {
  max-width: 800px;
}

.metadata-section {
  margin-bottom: 16px;
}

.title-area {
  margin-bottom: 12px;
}

.title-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.title-edit {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-candidates {
  margin-top: 12px;
  padding: 12px;
  background: var(--color-bg-secondary, #f6f8fa);
  border-radius: 6px;
}

.candidates-header {
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.candidate-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.candidate-tag:hover {
  transform: scale(1.05);
}

.tags-area {
  min-height: 40px;
}

.tag-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: normal;
}

.tag-input-wrapper {
  display: inline-block;
}

.category-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-current {
  display: flex;
  align-items: center;
  gap: 8px;
}

.no-category {
  color: var(--color-text-secondary);
}

.metadata-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

/* 暗色模式支持 */
[data-theme='dark'] .title-candidates {
  background: rgba(255, 255, 255, 0.06);
}

[data-theme='dark'] .candidate-tag {
  border-color: rgba(255, 255, 255, 0.2);
}
</style>
