<script setup lang="ts">
import { computed } from 'vue'
import { Tag } from 'ant-design-vue'
import { PLATFORM_CARDS, STEP_HINTS } from './presets'

const hint = STEP_HINTS.platform

const props = defineProps<{
  selectedId: string | null
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const selectedCard = computed(() => PLATFORM_CARDS.find(c => c.id === props.selectedId))
</script>

<template>
  <div class="step-platform">
    <div class="step-platform__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-platform__subtitle">{{ hint.subtitle }}</p>
    </div>

    <div class="step-platform__grid">
      <div
        v-for="card in PLATFORM_CARDS"
        :key="card.id"
        class="platform-card"
        :class="{ 'platform-card--selected': selectedId === card.id }"
        @click="emit('select', card.id)"
      >
        <div class="platform-card__icon">{{ card.emoji }}</div>
        <div class="platform-card__name">{{ card.name }}</div>
        <div class="platform-card__desc">{{ card.desc }}</div>
        <div class="platform-card__meta">
          <Tag class="meta-tag">{{ card.platform }}</Tag>
          <Tag class="meta-tag">{{ (card.targetWords / 10000).toFixed(0) }}万字</Tag>
          <Tag class="meta-tag">{{ card.targetChapters }}章</Tag>
        </div>
        <div class="platform-card__check" v-if="selectedId === card.id">✓</div>
      </div>
    </div>

    <div v-if="selectedCard" class="step-platform__preview">
      <div class="preview-row">
        <span class="preview-label">平台：</span>
        <span class="preview-value">{{ selectedCard.platform }}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">篇幅：</span>
        <span class="preview-value">{{ (selectedCard.targetWords / 10000).toFixed(0) }}万字 / {{ selectedCard.targetChapters }}章</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">每章：</span>
        <span class="preview-value">{{ selectedCard.chapterWordRange[0] }}-{{ selectedCard.chapterWordRange[1] }}字</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-platform {
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

  &__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;

    @media (max-width: 900px) {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  &__preview {
    margin-top: 24px;
    padding: 14px 18px;
    background: rgba(108, 92, 231, 0.08);
    border: 1px solid rgba(108, 92, 231, 0.2);
    border-radius: 8px;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }
}

.platform-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.15);
  border-radius: 12px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;
  user-select: none;

  &:hover {
    border-color: rgba(108, 92, 231, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(108, 92, 231, 0.15);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 20px rgba(108, 92, 231, 0.2);
  }

  &__icon {
    font-size: 36px;
    margin-bottom: 8px;
  }

  &__name {
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 6px;
  }

  &__desc {
    font-size: 12px;
    color: #888;
    margin-bottom: 10px;
  }

  &__meta {
    display: flex;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
  }

  &__check {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    background: #6c5ce7;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 14px;
    font-weight: bold;
  }
}

.meta-tag {
  font-size: 11px;
  background: rgba(108, 92, 231, 0.15);
  border: 1px solid rgba(108, 92, 231, 0.3);
  color: #a29bfe;
  border-radius: 4px;
  padding: 0 6px;
  line-height: 20px;
}

.preview-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-label {
  font-size: 13px;
  color: #888;
}

.preview-value {
  font-size: 14px;
  color: #e0e0e0;
}
</style>
