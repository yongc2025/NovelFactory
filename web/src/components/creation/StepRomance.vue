<script setup lang="ts">
import { computed } from 'vue'
import { STEP_HINTS, ROMANCE_MODES } from './presets'

const props = defineProps<{
  selected: string | null
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const hint = STEP_HINTS.romance

const safetyLabel = (n: number) => {
  if (n >= 5) return '最安全'
  if (n >= 4) return '安全'
  if (n >= 3) return '有争议'
  return '风险'
}
</script>

<template>
  <div class="step-romance">
    <div class="step-romance__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-romance__subtitle">{{ hint.subtitle }}</p>
    </div>

    <div class="step-romance__grid">
      <div
        v-for="mode in ROMANCE_MODES"
        :key="mode.id"
        class="romance-card"
        :class="{ 'romance-card--selected': selected === mode.id }"
        @click="emit('select', mode.id)"
      >
        <div class="romance-card__name">{{ mode.name }}</div>
        <div class="romance-card__desc">{{ mode.desc }}</div>
        <div class="romance-card__meta">
          <span class="safety-badge" :class="'safety-' + mode.safety">
            {{ safetyLabel(mode.safety) }}
          </span>
          <span class="genres">{{ mode.suitableGenres.join('、') }}</span>
        </div>
        <div class="romance-card__check" v-if="selected === mode.id">✓</div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-romance {
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
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    max-width: 700px;
    margin: 0 auto;
  }
}

.romance-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 12px;
  padding: 16px 18px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.35);
    transform: translateY(-2px);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
  }

  &__name {
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 6px;
  }

  &__desc {
    font-size: 13px;
    color: #999;
    margin-bottom: 10px;
    line-height: 1.4;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  &__check {
    position: absolute;
    top: 10px;
    right: 10px;
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

.safety-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;

  &.safety-5 {
    background: rgba(0, 214, 143, 0.15);
    color: #00d68f;
    border: 1px solid rgba(0, 214, 143, 0.3);
  }

  &.safety-4 {
    background: rgba(108, 92, 231, 0.12);
    color: #a29bfe;
    border: 1px solid rgba(108, 92, 231, 0.25);
  }

  &.safety-3 {
    background: rgba(255, 184, 0, 0.12);
    color: #ffb800;
    border: 1px solid rgba(255, 184, 0, 0.25);
  }
}

.genres {
  font-size: 11px;
  color: #666;
}
</style>
