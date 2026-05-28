<script setup lang="ts">
import { Card, Tag, Button, Rate, Space } from 'ant-design-vue'
import { CheckCircleOutlined } from '@ant-design/icons-vue'
import type { TopicPlan } from '@/types'

defineProps<{
  topic: TopicPlan
  selected?: boolean
}>()

const emit = defineEmits<{
  select: [id: string]
}>()
</script>

<template>
  <Card
    class="topic-card"
    :class="{ 'topic-card--selected': selected || topic.selected }"
    hoverable
  >
    <template #title>
      <div class="topic-title">
        <span>{{ topic.title }}</span>
        <Tag v-if="selected || topic.selected" color="green">
          <CheckCircleOutlined /> 已选
        </Tag>
      </div>
    </template>

    <div class="topic-content">
      <p class="topic-logline">{{ topic.logline }}</p>

      <div class="topic-meta">
        <div class="meta-item">
          <span class="meta-label">主题：</span>
          <span>{{ topic.theme }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">受众：</span>
          <span>{{ topic.target_audience }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">冲突：</span>
          <span>{{ topic.conflict }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">钩子：</span>
          <span>{{ topic.hook }}</span>
        </div>
      </div>

      <div class="topic-score">
        <span class="score-label">AI 评分：</span>
        <Rate :value="Math.round(topic.score / 20)" disabled allow-half />
        <span class="score-value">{{ topic.score }}分</span>
      </div>
    </div>

    <template #actions>
      <Space>
        <Button type="primary" @click.stop="emit('select', topic.id)">
          采用此方案
        </Button>
      </Space>
    </template>
  </Card>
</template>

<style scoped>
.topic-card {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.topic-card--selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(29, 57, 196, 0.2);
}

.topic-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topic-logline {
  color: var(--color-text-secondary);
  font-style: italic;
  margin-bottom: 16px;
  line-height: 1.6;
}

.topic-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.topic-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  color: var(--color-text-secondary);
}

.score-value {
  font-weight: 600;
  color: var(--color-primary);
}
</style>
