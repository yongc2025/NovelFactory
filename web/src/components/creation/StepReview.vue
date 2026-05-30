<script setup lang="ts">
import { computed } from 'vue'
import { Button } from 'ant-design-vue'
import { RocketOutlined } from '@ant-design/icons-vue'
import { PLATFORM_CARDS } from './presets'

const props = defineProps<{
  genreText: string
  conflictText: string
  platformCardId: string | null
  characterText: string
  styleText: string
  generatedPremise: string
  loading: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

const platformCard = computed(() => PLATFORM_CARDS.find(c => c.id === props.platformCardId))

// 汇总所有步骤的输入
const summaryItems = computed(() => {
  const items: { label: string; value: string; emoji: string }[] = []

  if (props.genreText) {
    items.push({ label: '题材方向', value: props.genreText.slice(0, 50) + (props.genreText.length > 50 ? '...' : ''), emoji: '🎭' })
  }
  if (props.conflictText) {
    items.push({ label: '核心冲突', value: props.conflictText.slice(0, 50) + (props.conflictText.length > 50 ? '...' : ''), emoji: '💥' })
  }
  if (platformCard.value) {
    items.push({ label: '发布场景', value: `${platformCard.value.name} · ${(platformCard.value.targetWords / 10000).toFixed(0)}万字`, emoji: platformCard.value.emoji })
  }
  if (props.characterText) {
    items.push({ label: '角色设定', value: props.characterText.slice(0, 50) + (props.characterText.length > 50 ? '...' : ''), emoji: '👤' })
  }
  if (props.styleText) {
    items.push({ label: '风格偏好', value: props.styleText.slice(0, 50) + (props.styleText.length > 50 ? '...' : ''), emoji: '🎨' })
  }

  return items
})

const canSubmit = computed(() => props.conflictText.trim().length > 0)
</script>

<template>
  <div class="step-review">
    <div class="step-review__header">
      <h3>确认 & 开始创作</h3>
      <p class="step-review__subtitle">检查你的灵感描述，确认后开始生成</p>
    </div>

    <!-- AI 生成的灵感描述 -->
    <div class="review-section">
      <div class="review-section__title">📝 灵感描述</div>
      <div class="premise-box">
        {{ generatedPremise || conflictText || '(等待生成...)' }}
      </div>
    </div>

    <!-- 各步骤摘要 -->
    <div class="review-section">
      <div class="review-section__title">📋 你的输入摘要</div>
      <div class="summary-grid">
        <div v-for="item in summaryItems" :key="item.label" class="summary-item">
          <div class="summary-item__icon">{{ item.emoji }}</div>
          <div class="summary-item__content">
            <div class="summary-item__label">{{ item.label }}</div>
            <div class="summary-item__value">{{ item.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 平台参数预览 -->
    <div v-if="platformCard" class="review-section">
      <div class="review-section__title">⚙️ 生成参数</div>
      <div class="params-preview">
        <span class="param-tag">平台：{{ platformCard.platform }}</span>
        <span class="param-tag">篇幅：{{ (platformCard.targetWords / 10000).toFixed(0) }}万字</span>
        <span class="param-tag">章节：{{ platformCard.targetChapters }}章</span>
        <span class="param-tag">每章：{{ platformCard.chapterWordRange[0] }}-{{ platformCard.chapterWordRange[1] }}字</span>
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="step-review__action">
      <Button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!canSubmit"
        class="submit-btn"
        @click="emit('submit')"
      >
        <RocketOutlined /> 开始创作
      </Button>
      <div v-if="!canSubmit" class="submit-hint">请至少填写核心冲突</div>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-review {
  &__header {
    text-align: center;
    margin-bottom: 28px;

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

  &__action {
    margin-top: 32px;
    text-align: center;
  }
}

.review-section {
  margin-bottom: 24px;

  &__title {
    font-size: 16px;
    font-weight: 600;
    color: #ccc;
    margin-bottom: 12px;
  }
}

.premise-box {
  padding: 16px 20px;
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid rgba(108, 92, 231, 0.2);
  border-radius: 10px;
  color: #e0e0e0;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background: #1a1a2e;
  border: 1px solid rgba(108, 92, 231, 0.15);
  border-radius: 10px;

  &__icon {
    font-size: 24px;
    flex-shrink: 0;
  }

  &__label {
    font-size: 12px;
    color: #888;
    margin-bottom: 4px;
  }

  &__value {
    font-size: 13px;
    color: #e0e0e0;
    line-height: 1.4;
  }
}

.params-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.param-tag {
  font-size: 12px;
  padding: 4px 12px;
  background: rgba(108, 92, 231, 0.12);
  border: 1px solid rgba(108, 92, 231, 0.25);
  border-radius: 16px;
  color: #a29bfe;
}

.submit-btn {
  height: 48px;
  padding: 0 48px;
  font-size: 16px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
  border: none;
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4);

  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #5a4bd6 0%, #8c82fc 100%);
    box-shadow: 0 6px 24px rgba(108, 92, 231, 0.5);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.submit-hint {
  font-size: 12px;
  color: #ff6b6b;
  margin-top: 8px;
}
</style>
