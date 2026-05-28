<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, List, Tag, Input, Button, Collapse, Empty, Space, InputNumber } from 'ant-design-vue'
import {
  EditOutlined,
  SaveOutlined,
  BookOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import type { Outline, OutlineChapter } from '@/types'

const props = defineProps<{
  outline: Outline | null
  loading?: boolean
}>()

const emit = defineEmits<{
  save: [chapters: OutlineChapter[]]
}>()

const editingIndex = ref<number | null>(null)
const editForm = ref<OutlineChapter | null>(null)

function startEdit(index: number, chapter: OutlineChapter) {
  editingIndex.value = index
  editForm.value = { ...chapter }
}

function cancelEdit() {
  editingIndex.value = null
  editForm.value = null
}

function saveEdit() {
  if (editForm.value && editingIndex.value !== null) {
    emit('save', [editForm.value])
    editingIndex.value = null
    editForm.value = null
  }
}

const collapseItems = computed(() => {
  if (!props.outline) return []
  return props.outline.chapters.map((ch, i) => ({
    key: String(i),
    label: `第${ch.chapter_number}章 ${ch.title}`,
    children: ch,
  }))
})
</script>

<template>
  <div class="outline-editor">
    <Empty v-if="!outline && !loading" description="大纲尚未生成" />
    <template v-else-if="outline">
      <div class="outline-header">
        <span class="outline-info">
          <BookOutlined />
          共 {{ outline.total_chapters }} 章
        </span>
      </div>

      <Collapse accordion>
        <Collapse.Panel
          v-for="(ch, index) in outline.chapters"
          :key="index"
          :header="`第${ch.chapter_number}章 ${ch.title}`"
        >
          <template v-if="editingIndex === index && editForm">
            <div class="edit-form">
              <div class="form-item">
                <label>标题</label>
                <Input v-model:value="editForm.title" />
              </div>
              <div class="form-item">
                <label>摘要</label>
                <Input.TextArea v-model:value="editForm.summary" :rows="3" />
              </div>
              <div class="form-item">
                <label>关键事件</label>
                <Input.TextArea
                  :value="editForm.key_events.join('\n')"
                  @update:value="(v: string) => editForm!.key_events = v.split('\n').filter(Boolean)"
                  :rows="3"
                  placeholder="每行一个事件"
                />
              </div>
              <div class="form-item">
                <label>POV 角色</label>
                <Input v-model:value="editForm.pov_character" />
              </div>
              <div class="form-item">
                <label>目标字数</label>
                <InputNumber v-model:value="editForm.word_count_target" :min="500" :step="500" />
              </div>
              <Space style="margin-top: 12px">
                <Button type="primary" @click="saveEdit">
                  <SaveOutlined /> 保存
                </Button>
                <Button @click="cancelEdit">取消</Button>
              </Space>
            </div>
          </template>
          <template v-else>
            <div class="chapter-info">
              <p class="chapter-summary">{{ ch.summary }}</p>
              <div class="chapter-meta">
                <Tag v-if="ch.pov_character" color="blue">
                  <UserOutlined /> {{ ch.pov_character }}
                </Tag>
                <Tag color="orange">目标 {{ ch.word_count_target }} 字</Tag>
              </div>
              <div class="chapter-events" v-if="ch.key_events.length">
                <div class="events-label">关键事件：</div>
                <ul>
                  <li v-for="(event, i) in ch.key_events" :key="i">{{ event }}</li>
                </ul>
              </div>
              <Button
                type="link"
                size="small"
                @click="startEdit(index, ch)"
                style="padding: 0; margin-top: 8px"
              >
                <EditOutlined /> 编辑
              </Button>
            </div>
          </template>
        </Collapse.Panel>
      </Collapse>
    </template>
  </div>
</template>

<style scoped>
.outline-editor {
  padding: 8px 0;
}

.outline-header {
  margin-bottom: 16px;
}

.outline-info {
  font-size: 16px;
  font-weight: 500;
}

.chapter-summary {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.chapter-meta {
  margin-bottom: 8px;
}

.events-label {
  color: var(--color-text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

.chapter-events ul {
  padding-left: 20px;
  margin: 0;
}

.chapter-events li {
  margin-bottom: 4px;
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
</style>
