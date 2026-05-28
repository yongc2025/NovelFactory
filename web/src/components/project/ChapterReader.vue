<script setup lang="ts">
import { computed } from 'vue'
import { Card, Tag, Typography, Empty, Spin, Space, Button } from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue'
import type { Chapter } from '@/types'

const { Paragraph } = Typography

const props = defineProps<{
  chapter: Chapter | null
  loading?: boolean
  totalChapters?: number
}>()

const emit = defineEmits<{
  prev: []
  next: []
}>()

const canPrev = computed(() => props.chapter && props.chapter.chapter_number > 1)
const canNext = computed(
  () =>
    props.chapter &&
    props.totalChapters !== undefined &&
    props.chapter.chapter_number < props.totalChapters
)

const statusLabel = computed(() => {
  if (!props.chapter) return ''
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
                <Tag color="purple">{{ chapter.word_count }} 字</Tag>
              </div>
            </div>
          </template>

          <div class="chapter-content">
            <p v-for="(para, i) in formattedContent" :key="i" class="content-para">
              {{ para }}
            </p>
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

.chapter-content {
  line-height: 2;
  font-size: 16px;
}

.content-para {
  text-indent: 2em;
  margin-bottom: 0;
}

.chapter-nav {
  display: flex;
  justify-content: center;
}
</style>
