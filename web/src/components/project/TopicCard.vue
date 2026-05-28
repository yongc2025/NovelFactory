<script setup lang="ts">
import { ref } from 'vue'
import { Card, Tag, Button, Rate, Space, Input, InputNumber, message } from 'ant-design-vue'
import {
  CheckCircleOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
} from '@ant-design/icons-vue'
import type { TopicPlan } from '@/types'

const props = defineProps<{
  topic: TopicPlan
  selected?: boolean
  projectId: string
}>()

const emit = defineEmits<{
  select: [id: string]
  update: [data: TopicPlan]
}>()

const editing = ref(false)
const editData = ref<TopicPlan | null>(null)

function startEdit() {
  editData.value = JSON.parse(JSON.stringify(props.topic))
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editData.value = null
}

async function saveEdit() {
  if (!editData.value) return
  try {
    const { updateTopic } = await import('@/api')
    await updateTopic(props.projectId, editData.value)
    emit('update', editData.value)
    editing.value = false
    editData.value = null
    message.success('选题已保存')
  } catch {
    message.error('保存失败')
  }
}
</script>

<template>
  <Card
    class="topic-card"
    :class="{ 'topic-card--selected': selected || topic.selected }"
    hoverable
  >
    <template #title>
      <div class="topic-title">
        <template v-if="!editing">
          <span>{{ topic.title }}</span>
          <Tag v-if="selected || topic.selected" color="green">
            <CheckCircleOutlined /> 已选
          </Tag>
        </template>
        <template v-else>
          <Input v-model:value="editData!.title" style="flex: 1" />
        </template>
      </div>
    </template>

    <!-- 查看模式 -->
    <template v-if="!editing">
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
    </template>

    <!-- 编辑模式 -->
    <template v-else-if="editData">
      <div class="edit-form">
        <div class="form-item">
          <label>一句话梗概</label>
          <Input.TextArea v-model:value="editData.logline" :rows="2" />
        </div>
        <div class="topic-meta-edit">
          <div class="form-item">
            <label>主题</label>
            <Input v-model:value="editData.theme" />
          </div>
          <div class="form-item">
            <label>目标受众</label>
            <Input v-model:value="editData.target_audience" />
          </div>
          <div class="form-item">
            <label>核心冲突</label>
            <Input v-model:value="editData.conflict" />
          </div>
          <div class="form-item">
            <label>钩子</label>
            <Input v-model:value="editData.hook" />
          </div>
        </div>
        <div class="form-item">
          <label>评分 (0-100)</label>
          <InputNumber v-model:value="editData.score" :min="0" :max="100" style="width: 120px" />
        </div>
      </div>
    </template>

    <template #actions>
      <Space>
        <template v-if="!editing">
          <Button type="primary" @click.stop="emit('select', topic.id)">
            采用此方案
          </Button>
          <Button @click.stop="startEdit">
            <EditOutlined /> 编辑
          </Button>
        </template>
        <template v-else>
          <Button type="primary" @click.stop="saveEdit">
            <SaveOutlined /> 保存
          </Button>
          <Button @click.stop="cancelEdit">
            <CloseOutlined /> 取消
          </Button>
        </template>
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
  gap: 8px;
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

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-item label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.topic-meta-edit {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
</style>
