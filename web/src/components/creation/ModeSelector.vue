<script setup lang="ts">
const emit = defineEmits<{
  select: [mode: 'quick' | 'full']
}>()

const modes = [
  {
    id: 'quick' as const,
    emoji: '🚀',
    name: '快速模式',
    time: '约 3 分钟',
    desc: 'AI 帮你搞定大部分内容，只需做几个关键选择',
    features: ['4 步完成', 'AI 生成灵感', '最少输入'],
  },
  {
    id: 'full' as const,
    emoji: '📝',
    name: '完整模式',
    time: '约 8 分钟',
    desc: '8 步精细控制每个细节，适合有明确想法的创作者',
    features: ['8 步引导', '精细控制', '深度定制'],
  },
]
</script>

<template>
  <div class="mode-selector">
    <div class="mode-selector__header">
      <h2>✨ 创建新项目</h2>
      <p class="mode-selector__subtitle">选择你的创建方式</p>
    </div>

    <div class="mode-selector__grid">
      <div
        v-for="mode in modes"
        :key="mode.id"
        class="mode-card"
        @click="emit('select', mode.id)"
      >
        <div class="mode-card__emoji">{{ mode.emoji }}</div>
        <div class="mode-card__name">{{ mode.name }}</div>
        <div class="mode-card__time">{{ mode.time }}</div>
        <div class="mode-card__desc">{{ mode.desc }}</div>
        <div class="mode-card__features">
          <span v-for="f in mode.features" :key="f" class="feature-tag">{{ f }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.mode-selector {
  &__header {
    text-align: center;
    margin-bottom: 48px;

    h2 {
      font-size: 28px;
      color: #e0e0e0;
      margin: 0 0 12px;
    }
  }

  &__subtitle {
    font-size: 16px;
    color: #888;
    margin: 0;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 700px;
    margin: 0 auto;

    @media (max-width: 600px) {
      grid-template-columns: 1fr;
    }
  }
}

.mode-card {
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.15);
  border-radius: 20px;
  padding: 36px 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;

  &:hover {
    border-color: rgba(108, 92, 231, 0.5);
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(108, 92, 231, 0.2);
  }

  &__emoji {
    font-size: 56px;
    margin-bottom: 16px;
  }

  &__name {
    font-size: 22px;
    font-weight: 700;
    color: #e0e0e0;
    margin-bottom: 6px;
  }

  &__time {
    font-size: 13px;
    color: #a29bfe;
    margin-bottom: 12px;
  }

  &__desc {
    font-size: 14px;
    color: #999;
    line-height: 1.6;
    margin-bottom: 16px;
  }

  &__features {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
  }
}

.feature-tag {
  font-size: 12px;
  padding: 4px 12px;
  background: rgba(108, 92, 231, 0.12);
  border: 1px solid rgba(108, 92, 231, 0.25);
  border-radius: 16px;
  color: #a29bfe;
}
</style>
