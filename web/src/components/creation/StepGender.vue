<script setup lang="ts">
import { computed } from 'vue'
import { STEP_HINTS } from './presets'

const props = defineProps<{
  selected: 'male' | 'female' | 'both' | null
}>()

const emit = defineEmits<{
  select: [value: 'male' | 'female' | 'both']
}>()

const hint = STEP_HINTS.gender

const options = [
  { id: 'male' as const, emoji: '⚔️', name: '男频', desc: '升级打怪、热血战斗、权谋争霸', keywords: '升级、打脸、金手指、种田、热血' },
  { id: 'female' as const, emoji: '💕', name: '女频', desc: '甜宠虐恋、宫斗宅斗、重生逆袭', keywords: '甜宠、虐恋、宫斗、重生、逆袭' },
  { id: 'both' as const, emoji: '📚', name: '通用', desc: '悬疑推理、科幻末世、都市现实', keywords: '悬疑、科幻、都市、历史、灵异' },
]
</script>

<template>
  <div class="step-gender">
    <div class="step-gender__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-gender__subtitle">{{ hint.subtitle }}</p>
    </div>

    <div class="step-gender__grid">
      <div
        v-for="opt in options"
        :key="opt.id"
        class="gender-card"
        :class="{ 'gender-card--selected': selected === opt.id }"
        @click="emit('select', opt.id)"
      >
        <div class="gender-card__emoji">{{ opt.emoji }}</div>
        <div class="gender-card__name">{{ opt.name }}</div>
        <div class="gender-card__desc">{{ opt.desc }}</div>
        <div class="gender-card__keywords">{{ opt.keywords }}</div>
        <div class="gender-card__check" v-if="selected === opt.id">✓</div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-gender {
  &__header {
    text-align: center;
    margin-bottom: 32px;

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
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 600px;
    margin: 0 auto;
  }
}

.gender-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.15);
  border-radius: 16px;
  padding: 28px 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;

  &:hover {
    border-color: rgba(108, 92, 231, 0.4);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.15);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 24px rgba(108, 92, 231, 0.2);
  }

  &__emoji {
    font-size: 48px;
    margin-bottom: 12px;
  }

  &__name {
    font-size: 20px;
    font-weight: 700;
    color: #e0e0e0;
    margin-bottom: 8px;
  }

  &__desc {
    font-size: 14px;
    color: #aaa;
    margin-bottom: 12px;
    line-height: 1.5;
  }

  &__keywords {
    font-size: 12px;
    color: #666;
    padding: 6px 12px;
    background: rgba(108, 92, 231, 0.08);
    border-radius: 12px;
    display: inline-block;
  }

  &__check {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 28px;
    height: 28px;
    background: #6c5ce7;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
  }
}
</style>
