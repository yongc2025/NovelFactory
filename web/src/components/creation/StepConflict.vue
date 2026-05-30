<script setup lang="ts">
import { computed, ref } from 'vue'
import { Input, Button, message } from 'ant-design-vue'
import { BulbOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { STEP_HINTS } from './presets'
import http from '@/api'

const props = defineProps<{
  freeText: string
  gender?: 'male' | 'female' | 'both' | null
  genreName?: string
}>()

const emit = defineEmits<{
  'update:freeText': [value: string]
}>()

const hint = STEP_HINTS.conflict

// 结构化字段
const fields = ref({
  identity: '',    // 主角身份
  job: '',         // 职业
  personality: '', // 性格特点
  event: '',       // 发生了什么
  goal: '',        // 主角想做什么
  obstacle: '',    // 什么在阻碍他
})

// 从 freeText 初始化字段（如果已有内容）
function parseFromText(text: string) {
  if (!text) return
  const lines = text.split('\n')
  for (const line of lines) {
    if (line.includes('主角身份：')) fields.value.identity = line.split('：')[1]?.trim() || ''
    if (line.includes('职业：')) fields.value.job = line.split('：')[1]?.trim() || ''
    if (line.includes('性格特点：')) fields.value.personality = line.split('：')[1]?.trim() || ''
    if (line.includes('发生了什么：')) fields.value.event = line.split('：')[1]?.trim() || ''
    if (line.includes('主角想做什么：')) fields.value.goal = line.split('：')[1]?.trim() || ''
    if (line.includes('什么在阻碍他：')) fields.value.obstacle = line.split('：')[1]?.trim() || ''
  }
}

// 初始化
parseFromText(props.freeText)

// 同步字段到 freeText
function syncToText() {
  const lines = [
    `主角身份：${fields.value.identity}`,
    `职业：${fields.value.job}`,
    `性格特点：${fields.value.personality}`,
    `发生了什么：${fields.value.event}`,
    `主角想做什么：${fields.value.goal}`,
    `什么在阻碍他：${fields.value.obstacle}`,
  ]
  emit('update:freeText', lines.join('\n'))
}

// AI 生成
const aiLoading = ref(false)
async function generateByAI() {
  aiLoading.value = true
  try {
    const res = await http.post('/generate/inspiration', {
      gender: props.gender || 'male',
      genre_name: props.genreName || '',
      story_background: props.freeText || '请根据题材生成一个故事梗概',
      style_text: '',
    })
    const data = res.data.data ?? res.data
    const version = data.versions?.[0]
    if (version?.synopsis) {
      // 将 AI 生成的 synopsis 解析到字段中
      const text = version.synopsis
      emit('update:freeText', text)
      // 尝试从 AI 输出中提取字段
      const lines = text.split('\n')
      for (const line of lines) {
        if (line.includes('身份') || line.includes('是')) fields.value.identity = line.slice(0, 30)
      }
      message.success('AI 已生成，请检查并调整')
    }
  } catch (e: any) {
    message.error(e.response?.data?.detail || '生成失败，请重试')
  } finally {
    aiLoading.value = false
  }
}

const isComplete = computed(() => {
  return fields.value.identity.trim().length > 0 || props.freeText.trim().length > 0
})
defineExpose({ isComplete })
</script>

<template>
  <div class="step-conflict">
    <div class="step-conflict__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-conflict__subtitle">{{ hint.subtitle }}</p>
    </div>

    <!-- 结构化输入字段 -->
    <div class="step-conflict__fields">
      <div class="field-row" v-for="field in hint.angles" :key="field.label">
        <div class="field-label">{{ field.icon }} {{ field.label }}</div>
        <Input
          v-if="field.label === '主角是谁？'"
          v-model:value="fields.identity"
          @update:value="syncToText"
          :placeholder="field.hint"
          class="field-input"
        />
        <Input
          v-else-if="field.label === '发生了什么？'"
          v-model:value="fields.event"
          @update:value="syncToText"
          :placeholder="field.hint"
          class="field-input"
        />
        <Input
          v-else-if="field.label === '主角想做什么？'"
          v-model:value="fields.goal"
          @update:value="syncToText"
          :placeholder="field.hint"
          class="field-input"
        />
        <Input
          v-else-if="field.label === '什么在阻碍他？'"
          v-model:value="fields.obstacle"
          @update:value="syncToText"
          :placeholder="field.hint"
          class="field-input"
        />
      </div>

      <!-- 补充字段 -->
      <div class="field-row">
        <div class="field-label">💼 职业</div>
        <Input v-model:value="fields.job" @update:value="syncToText" placeholder="如：程序员、医生、学生..." class="field-input" />
      </div>
      <div class="field-row">
        <div class="field-label">🎭 性格特点</div>
        <Input v-model:value="fields.personality" @update:value="syncToText" placeholder="如：毒舌、逗逼、高冷..." class="field-input" />
      </div>
    </div>

    <!-- 完整文本预览（可编辑）+ AI 按钮 -->
    <div class="step-conflict__preview">
      <div class="preview-top">
        <span class="preview-label">📝 完整灵感描述（可直接编辑）：</span>
        <Button
          :loading="aiLoading"
          @click="generateByAI"
          class="ai-btn"
          size="small"
        >
          <BulbOutlined v-if="!aiLoading" /> {{ aiLoading ? 'AI 生成中...' : '🤖 AI 帮我生成' }}
        </Button>
      </div>
      <Input.TextArea
        :value="freeText"
        @update:value="emit('update:freeText', $event)"
        :rows="8"
        placeholder="填写上方字段后自动生成，也可以直接在这里编辑...\n\n例如：主角林舰是理工科博士，因实验成果被学长剽窃，连续熬夜猝死在实验室。醒来竟穿越到末法时代魔法世界的落魄贵族身上。他发现这个世界的物理法则依然稳固——前世的知识在这里是降维打击。他用物理学原理改良魔法阵，用化学知识提炼魔药残渣，10年间建立起魔法工业帝国..."
        class="preview-textarea"
      />
    </div>
  </div>
</template>

<style scoped lang="less">
.step-conflict {
  &__header {
    text-align: center;
    margin-bottom: 24px;

    h3 {
      font-size: 22px;
      color: #e0e0e0;
      margin: 0 0 8px;
    }
  }

  &__subtitle {
    font-size: 14px;
    color: #888;
    margin: 0;
  }

  &__fields {
    margin: 0 auto 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  &__preview {
    margin: 0 auto;
  }
}

.field-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-label {
  font-size: 13px;
  color: #ccc;
  min-width: 120px;
  flex-shrink: 0;
}

.field-input {
  flex: 1;
  background: #1a1a2e;
  border-color: rgba(108, 92, 231, 0.3);
}

.preview-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.preview-label {
  font-size: 13px;
  color: #ccc;
}

.ai-btn {
  background: linear-gradient(135deg, rgba(108, 92, 231, 0.15), rgba(162, 155, 254, 0.1));
  border: 1px solid rgba(108, 92, 231, 0.3);
  color: #a29bfe;
  border-radius: 16px;

  &:hover {
    border-color: #6c5ce7;
    color: #e0e0e0;
  }
}

.preview-textarea {
  background: #1a1a2e;
  border-color: rgba(108, 92, 231, 0.3);
}

:deep(.ant-input) {
  background: #1a1a2e;
  color: #e0e0e0;
  border-color: rgba(108, 92, 231, 0.3);
}

:deep(.ant-input::placeholder) {
  color: #555;
}
</style>
