<script setup lang="ts">
import { computed } from 'vue'
import { GENRE_CARDS } from './presets'

const props = defineProps<{
  gender: 'male' | 'female' | 'both' | null
  genreId: string | null
}>()

const emit = defineEmits<{
  'update:gender': [value: 'male' | 'female' | 'both']
  'update:genreId': [value: string]
}>()

const genderOptions = [
  { id: 'male' as const, emoji: '⚔️', name: '男频', desc: '升级打怪、热血战斗、权谋争霸' },
  { id: 'female' as const, emoji: '💕', name: '女频', desc: '甜宠虐恋、宫斗宅斗、重生逆袭' },
  { id: 'both' as const, emoji: '📚', name: '通用', desc: '悬疑推理、科幻末世、都市现实' },
]

const filteredGenres = computed(() => {
  if (!props.gender) return GENRE_CARDS
  return GENRE_CARDS.filter(c => c.gender === props.gender || c.gender === 'both')
})

const canProceed = computed(() => !!props.gender && !!props.genreId)
defineExpose({ canProceed })
</script>

<template>
  <div class="quick-step1">
    <div class="quick-step1__header">
      <h3>快速定位</h3>
      <p class="quick-step1__subtitle">选好性别和题材，AI 帮你搞定后面的事</p>
    </div>

    <!-- 性别选择 -->
    <div class="quick-step1__section">
      <div class="section-label">📌 目标读者</div>
      <div class="gender-grid">
        <div
          v-for="opt in genderOptions"
          :key="opt.id"
          class="gender-card"
          :class="{ 'gender-card--selected': gender === opt.id }"
          @click="emit('update:gender', opt.id)"
        >
          <span class="gender-card__emoji">{{ opt.emoji }}</span>
          <span class="gender-card__name">{{ opt.name }}</span>
          <span class="gender-card__desc">{{ opt.desc }}</span>
          <span v-if="gender === opt.id" class="gender-card__check">✓</span>
        </div>
      </div>
    </div>

    <!-- 题材选择 -->
    <div class="quick-step1__section">
      <div class="section-label">🎭 题材方向</div>
      <div class="genre-grid">
        <div
          v-for="card in filteredGenres"
          :key="card.id"
          class="genre-card"
          :class="{ 'genre-card--selected': genreId === card.id }"
          @click="emit('update:genreId', card.id)"
        >
          <span class="genre-card__emoji">{{ card.emoji }}</span>
          <span class="genre-card__name">{{ card.name }}</span>
          <span class="genre-card__desc">{{ card.desc }}</span>
          <span v-if="genreId === card.id" class="genre-card__check">✓</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.quick-step1 {
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

  &__section {
    margin-bottom: 28px;
  }
}

.section-label {
  font-size: 14px;
  color: #ccc;
  margin-bottom: 12px;
  font-weight: 500;
}

.gender-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 500px;
  margin: 0 auto;
}

.gender-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.15);
  border-radius: 14px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;

  &:hover {
    border-color: rgba(108, 92, 231, 0.4);
    transform: translateY(-2px);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 20px rgba(108, 92, 231, 0.2);
  }

  &__emoji {
    font-size: 36px;
    display: block;
    margin-bottom: 8px;
  }

  &__name {
    font-size: 18px;
    font-weight: 700;
    color: #e0e0e0;
    display: block;
    margin-bottom: 4px;
  }

  &__desc {
    font-size: 12px;
    color: #888;
    display: block;
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

.genre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.genre-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 12px;
  padding: 16px 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;

  &:hover {
    border-color: rgba(108, 92, 231, 0.35);
    transform: translateY(-2px);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 16px rgba(108, 92, 231, 0.15);
  }

  &__emoji {
    font-size: 32px;
    display: block;
    margin-bottom: 8px;
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
    color: #e0e0e0;
    display: block;
    margin-bottom: 4px;
  }

  &__desc {
    font-size: 11px;
    color: #888;
    display: block;
    line-height: 1.3;
  }

  &__check {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 22px;
    height: 22px;
    background: #6c5ce7;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 13px;
    font-weight: bold;
  }
}
</style>
