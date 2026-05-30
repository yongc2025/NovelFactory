<script setup lang="ts">
import { computed, ref } from 'vue'
import { Input } from 'ant-design-vue'
import { GENRE_CARDS, STEP_HINTS } from './presets'

const props = defineProps<{
  freeText: string
  gender?: 'male' | 'female' | 'both' | null
}>()

const emit = defineEmits<{
  'update:freeText': [value: string]
}>()

const hint = STEP_HINTS.genre

// 按性别过滤题材卡片：both 始终显示
const filteredCards = computed(() => {
  if (!props.gender) return GENRE_CARDS
  return GENRE_CARDS.filter(c => c.gender === 'both' || c.gender === props.gender)
})

// 选中的卡片 ID
const selectedCardId = ref<string | null>(null)

// 点击卡片 → 直接选中，填入题材名称
function selectCard(card: typeof GENRE_CARDS[0]) {
  selectedCardId.value = card.id
  emit('update:freeText', card.name)
}

// 自定义输入（限制 15 字）
function onCustomInput(val: string) {
  selectedCardId.value = null
  emit('update:freeText', val.slice(0, 15))
}

const isComplete = computed(() => props.freeText.trim().length > 0)
defineExpose({ isComplete })
</script>

<template>
  <div class="step-genre">
    <div class="step-genre__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-genre__subtitle">{{ hint.subtitle }}</p>
    </div>

    <!-- 题材卡片：主选择区 -->
    <div class="step-genre__cards">
      <div class="cards-grid">
        <div
          v-for="card in filteredCards"
          :key="card.id"
          class="genre-card"
          :class="{ 'genre-card--selected': selectedCardId === card.id }"
          @click="selectCard(card)"
        >
          <span class="genre-card__emoji">{{ card.emoji }}</span>
          <span class="genre-card__name">{{ card.name }}</span>
          <span class="genre-card__desc">{{ card.desc }}</span>
          <div class="genre-card__check" v-if="selectedCardId === card.id">✓</div>
        </div>
      </div>
    </div>

    <!-- 自定义输入：折叠式，不抢视觉焦点 -->
    <div class="step-genre__custom">
      <div class="custom-label">没有合适的？手动输入题材（15字以内）：</div>
      <Input
        :value="freeText"
        @update:value="onCustomInput"
        placeholder="如：赛博朋克、克苏鲁、美食..."
        :maxlength="15"
        class="custom-input"
      />
      <span class="char-count">{{ freeText.length }}/15</span>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-genre {
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

  &__cards {
    margin-bottom: 24px;
  }

  &__custom {
    max-width: 400px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 6px;
    align-items: center;
  }
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-width: 700px;
  margin: 0 auto;
}

.genre-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 10px;
  background: #1a1a2e;
  border: 2px solid #2d2d44;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.4);
    background: #1f1f35;
    transform: translateY(-2px);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 16px rgba(108, 92, 231, 0.2);
  }

  &__emoji {
    font-size: 32px;
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
    color: #e0e0e0;
  }

  &__desc {
    font-size: 11px;
    color: #888;
    text-align: center;
    line-height: 1.3;
  }

  &__check {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 22px;
    height: 22px;
    background: #6c5ce7;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 12px;
    font-weight: bold;
  }
}

.custom-label {
  font-size: 12px;
  color: #666;
  text-align: center;
}

.custom-input {
  background: #1a1a2e;
  border-color: rgba(108, 92, 231, 0.3);
  max-width: 300px;
}

.char-count {
  font-size: 11px;
  color: #555;
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
