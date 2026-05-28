<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Card,
  Tag,
  Typography,
  Empty,
  Spin,
  Space,
  Button,
  Input,
  message,
} from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  FileTextOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
} from '@ant-design/icons-vue'
import type { Chapter } from '@/types'

const { Paragraph } = Typography

const props = defineProps<{
  chapter: Chapter | null
  loading?: boolean
  totalChapters?: number
  projectId: string
}>()

const emit = defineEmits<{
  prev: []
  next: []
  update: [data: Chapter]
}>()

const editing = ref(false)
const editContent = ref('')

const canPrev = computed(() => props.chapter && props.chapter.chapter_number > 1)
const canNext = computed(
  () =>
    props.chapter &&
    props.totalChapters !== undefined &&
    props.chapter.chapter_number < props.totalChapters
)

const statusLabel = computed(() => {
  if (!props.chapter) return { text: '', color: 'default' }
  const map: Record<string, { text: string; color: string }> = {
    draft: { text: '草稿', color: 'default' },
    reviewed: { text: '已审校', color: 'blue' },
    final: { text: '终稿', color: 'green' },
  }
  return map[props.chapter.status] || { text: '未知', color: 'default' }
})

const formattedContent = computed(() => {
  if (!props.chapter) return ''
  return props.chapter.content.split('\n').filter(Boolean)
})

const wordCount = computed(() => {
  if (editing.value) {
    return editContent.value.replace(/\s/g, '').length
  }
  return props.chapter?.word_count ?? 0
})

function startEdit() {
  editContent.value = props.chapter?.content ?? ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editContent.value = ''
}

async function saveEdit() {
  if (!props.chapter) return
  try {
    const { updateChapterDraft } = await import('@/api')
    await updateChapterDraft(props.projectId, props.chapter.chapter_number, editContent.value)
    emit('update', {
      ...props.chapter,
      content: editContent.value,
      word_count: editContent.value.replace(/\s/g, '').length,
    })
    editing.value = false
    editContent.value = ''
    message.success('正文已保存')
  } catch {
    message.error('保存失败')
  }
}
</script>

<template>
  <div class="chapter-reader">
    <Spin :spinning="loading">
      <Empty v-if="!chapter && !loading" description="章节内容不存在" />
      <template v-else-if="chapter">
        <Card class="chapter-card">
          <template #title>
            <div class="chapter-header">
              <div class="chapter-title-block">
                <FileTextOutlined />
                <span>第{{ chapter.chapter_number }}章 {{ chapter.title }}</span>
                <Tag :color="statusLabel.color">{{ statusLabel.text }}</Tag>
              </div>
              <div class="chapter-stats">
                <Tag color="purple">{{ wordCount }} 字</Tag>
                <template v-if="!editing">
                  <Button size="small" @click="startEdit">
                    <EditOutlined /> 编辑
                  </Button>
                </template>
                <template v-else>
                  <Space>
                    <Button size="small" type="primary" @click="saveEdit">
                      <SaveOutlined /> 保存
                    </Button>
                    <Button size="small" @click="cancelEdit">
                      <CloseOutlined /> 取消
                    </Button>
                  </Space>
                </template>
              </div>
            </div>
          </template>

          <!-- 查看模式 -->
          <div v-if="!editing" class="chapter-content">
            <p v-for="(para, i) in formattedContent" :key="i" class="content-para">
              {{ para }}
            </p>
          </div>

          <!-- 编辑模式 -->
          <div v-else class="chapter-edit">
            <Input.TextArea
              v-model:value="editContent"
              :rows="20"
              placeholder="输入正文内容..."
              class="content-textarea"
            />
          </div>

          <template #actions>
            <div class="chapter-nav">
              <Space>
                <Button :disabled="!canPrev" @click="emit('prev')">
                  <ArrowLeftOutlined /> 上一章
                </Button>
                <Button :disabled="!canNext" @click="emit('next')">
                  下一章 <ArrowRightOutlined />
                </Button>
              </Space>
            </div>
          </template>
        </Card>
      </template>
    </Spin>
  </div>
</template>

<style scoped>
.chapter-reader {
  padding: 8px 0;
}

.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.chapter-title-block {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.chapter-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-content {
  line-height: 2;
  font-size: 16px;
}

.content-para {
  text-indent: 2em;
  margin-bottom: 0;
}

.chapter-edit {
  margin-top: 8px;
}

.content-textarea {
  font-size: 15px;
  line-height: 1.8;
  font-family: 'Noto Serif SC', 'Source Han Serif SC', serif;
}

.chapter-nav {
  display: flex;
  justify-content: center;
}
</style>
