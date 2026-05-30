<script setup lang="ts">
import { computed } from 'vue'
import { Button } from 'ant-design-vue'
import { RocketOutlined } from '@ant-design/icons-vue'
import { PLATFORM_CARDS, GENRE_CARDS, PROTAGONIST_TEMPLATES, HEROINE_TEMPLATES, ROMANCE_MODES } from './presets'
import type { InspirationVersion } from './QuickStep3.vue'

const props = defineProps<{
  gender: 'male' | 'female' | 'both' | null
  genreId: string | null
  platformId: string | null
  protagonistName: string
  protagonistId: string | null
  heroineId: string | null
  romanceMode: string | null
  storyBackground: string
  styleText: string
  referenceWorks: string
  forbiddenElements: string
  selectedInspiration: InspirationVersion | null
  loading: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

const genreCard = computed(() => GENRE_CARDS.find(c => c.id === props.genreId))
const platformCard = computed(() => PLATFORM_CARDS.find(c => c.id === props.platformId))
const protagonist = computed(() => PROTAGONIST_TEMPLATES.find(t => t.id === props.protagonistId))
const heroine = computed(() => HEROINE_TEMPLATES.find(t => t.id === props.heroineId))
const romance = computed(() => ROMANCE_MODES.find(m => m.id === props.romanceMode))

const summaryItems = computed(() => {
  const items: { label: string; value: string; emoji: string }[] = []

  if (props.gender) {
    items.push({ label: '目标读者', value: props.gender === 'male' ? '男频' : '女频', emoji: props.gender === 'male' ? '⚔️' : '💕' })
  }
  if (genreCard.value) {
    items.push({ label: '题材方向', value: genreCard.value.name, emoji: genreCard.value.emoji })
  }
  if (platformCard.value) {
    items.push({ label: '发布平台', value: `${platformCard.value.name} · ${(platformCard.value.targetWords / 10000).toFixed(0)}万字`, emoji: platformCard.value.emoji })
  }
  if (protagonist.value) {
    items.push({ label: '主角性格', value: protagonist.value.name, emoji: '👤' })
  }
  if (props.protagonistName) {
    items.push({ label: '主角姓名', value: props.protagonistName, emoji: '✏️' })
  }
  if (romance.value && romance.value.id !== 'none') {
    items.push({ label: '感情线', value: romance.value.name, emoji: '💕' })
  }
  if (heroine.value) {
    items.push({ label: '女主性格', value: heroine.value.name, emoji: '👩' })
  }
  if (props.styleText) {
    items.push({ label: '写作风格', value: props.styleText.slice(0, 30) + (props.styleText.length > 30 ? '...' : ''), emoji: '🎨' })
  }
  if (props.referenceWorks) {
    items.push({ label: '参考作品', value: props.referenceWorks, emoji: '📚' })
  }

  return items
})
</script>

<template>
  <div class="quick-step4">
    <div class="quick-step4__header">
      <h3>确认 & 开始创作</h3>
      <p class="quick-step4__subtitle">检查你的选择，确认后开始生成</p>
    </div>

    <!-- 选中的灵感 -->
    <div v-if="selectedInspiration" class="quick-step4__section">
      <div class="section-title">✨ 选中的灵感</div>
      <div class="inspiration-box">
        <div class="inspiration-titles">
          <span class="titles-label">📖 备选书名：</span>
          <div class="titles-list">
            <span v-for="(t, i) in selectedInspiration.titles" :key="i" class="title-tag">{{ t }}</span>
          </div>
        </div>
        <div class="inspiration-synopsis">
          <span class="synopsis-label">📝 故事梗概：</span>
          <p class="synopsis-text">{{ selectedInspiration.synopsis }}</p>
        </div>
      </div>
    </div>

    <!-- 基础信息摘要 -->
    <div class="quick-step4__section">
      <div class="section-title">📋 基础信息</div>
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
    <div v-if="platformCard" class="quick-step4__section">
      <div class="section-title">⚙️ 生成参数</div>
      <div class="params-preview">
        <span class="param-tag">平台：{{ platformCard.platform }}</span>
        <span class="param-tag">篇幅：{{ (platformCard.targetWords / 10000).toFixed(0) }}万字</span>
        <span class="param-tag">章节：{{ platformCard.targetChapters }}章</span>
        <span class="param-tag">每章：{{ platformCard.chapterWordRange[0] }}-{{ platformCard.chapterWordRange[1] }}字</span>
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="quick-step4__action">
      <Button
        type="primary"
        size="large"
        :loading="loading"
        class="submit-btn"
        @click="emit('submit')"
      >
        <RocketOutlined /> 开始创作
      </Button>
    </div>
  </div>
</template>

<style scoped lang="less">
.quick-step4 {
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
    margin-bottom: 24px;
  }

  &__action {
    margin-top: 32px;
    text-align: center;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #ccc;
  margin-bottom: 12px;
}

.inspiration-box {
  padding: 20px;
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid rgba(108, 92, 231, 0.2);
  border-radius: 12px;
}

.inspiration-titles {
  margin-bottom: 14px;

  .titles-label {
    font-size: 13px;
    color: #999;
    display: block;
    margin-bottom: 6px;
  }
}

.titles-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.title-tag {
  font-size: 14px;
  padding: 4px 14px;
  background: rgba(108, 92, 231, 0.15);
  border: 1px solid rgba(108, 92, 231, 0.3);
  border-radius: 16px;
  color: #e0e0e0;
  font-weight: 500;
}

.inspiration-synopsis {
  .synopsis-label {
    font-size: 13px;
    color: #999;
    display: block;
    margin-bottom: 6px;
  }

  .synopsis-text {
    font-size: 14px;
    color: #e0e0e0;
    line-height: 1.8;
    margin: 0;
    white-space: pre-wrap;
  }
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #1a1a2e;
  border: 1px solid rgba(108, 92, 231, 0.15);
  border-radius: 10px;

  &__icon {
    font-size: 20px;
    flex-shrink: 0;
  }

  &__label {
    font-size: 12px;
    color: #888;
    margin-bottom: 2px;
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
}
</style>
