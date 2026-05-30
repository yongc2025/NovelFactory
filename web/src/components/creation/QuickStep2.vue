<script setup lang="ts">
import { computed } from 'vue'
import { PLATFORM_CARDS, PROTAGONIST_TEMPLATES, HEROINE_TEMPLATES, ROMANCE_MODES } from './presets'

const props = defineProps<{
  gender: 'male' | 'female' | 'both'
  // 区块 A
  platformId: string | null
  // 区块 B
  protagonistName: string
  protagonistId: string | null
  heroineId: string | null
  romanceMode: string | null
  storyBackground: string
  // 区块 C
  styleText: string
  referenceWorks: string
  forbiddenElements: string
}>()

const emit = defineEmits<{
  'update:platformId': [value: string]
  'update:protagonistName': [value: string]
  'update:protagonistId': [value: string]
  'update:heroineId': [value: string]
  'update:romanceMode': [value: string]
  'update:storyBackground': [value: string]
  'update:styleText': [value: string]
  'update:referenceWorks': [value: string]
  'update:forbiddenElements': [value: string]
}>()

// 主角性格模板（按性别过滤）
const protagonistOptions = computed(() =>
  PROTAGONIST_TEMPLATES.filter(t => t.gender === props.gender)
)

// 是否显示女主相关（男频 + 有感情线）
const showHeroine = computed(() =>
  props.gender === 'male' &&
  props.romanceMode &&
  props.romanceMode !== 'none'
)

// 感情线模式（男频时显示）
const showRomance = computed(() => props.gender === 'male')

const canProceed = computed(() => !!props.platformId)
defineExpose({ canProceed })
</script>

<template>
  <div class="quick-step2">
    <div class="quick-step2__header">
      <h3>补充信息</h3>
      <p class="quick-step2__subtitle">大部分可选，选填越多 AI 越精准</p>
    </div>

    <!-- 区块 A：平台+篇幅（必选） -->
    <div class="quick-step2__section">
      <div class="section-label required">📌 发布平台 & 篇幅</div>
      <div class="platform-grid">
        <div
          v-for="card in PLATFORM_CARDS"
          :key="card.id"
          class="platform-card"
          :class="{ 'platform-card--selected': platformId === card.id }"
          @click="emit('update:platformId', card.id)"
        >
          <div class="platform-card__icon">{{ card.emoji }}</div>
          <div class="platform-card__name">{{ card.name }}</div>
          <div class="platform-card__meta">
            <span class="meta-chip">{{ card.platform }}</span>
            <span class="meta-chip">{{ (card.targetWords / 10000).toFixed(0) }}万字</span>
          </div>
          <span v-if="platformId === card.id" class="platform-card__check">✓</span>
        </div>
      </div>
    </div>

    <!-- 区块 B：角色+感情线 -->
    <div class="quick-step2__section">
      <div class="section-label">👤 角色设定（可选）</div>

      <!-- 主角姓名 -->
      <div class="field-row">
        <div class="field-label">主角姓名</div>
        <a-input
          :value="protagonistName"
          @update:value="emit('update:protagonistName', $event)"
          placeholder="留空则 AI 自动生成"
          allow-clear
        />
      </div>

      <!-- 主角性格 -->
      <div class="field-row">
        <div class="field-label">主角性格</div>
        <div class="template-grid">
          <div
            v-for="t in protagonistOptions"
            :key="t.id"
            class="template-card"
            :class="{ 'template-card--selected': protagonistId === t.id }"
            @click="emit('update:protagonistId', t.id)"
          >
            <div class="template-card__name">{{ t.name }}</div>
            <div class="template-card__desc">{{ t.desc }}</div>
          </div>
        </div>
      </div>

      <!-- 感情线模式（男频时显示） -->
      <div v-if="showRomance" class="field-row">
        <div class="field-label">感情线模式</div>
        <div class="romance-grid">
          <div
            v-for="mode in ROMANCE_MODES"
            :key="mode.id"
            class="romance-card"
            :class="{ 'romance-card--selected': romanceMode === mode.id }"
            @click="emit('update:romanceMode', mode.id)"
          >
            <div class="romance-card__name">{{ mode.name }}</div>
            <div class="romance-card__desc">{{ mode.desc }}</div>
          </div>
        </div>
      </div>

      <!-- 女主性格（有条件显示） -->
      <div v-if="showHeroine" class="field-row">
        <div class="field-label">女主性格</div>
        <div class="template-grid">
          <div
            v-for="t in HEROINE_TEMPLATES"
            :key="t.id"
            class="template-card"
            :class="{ 'template-card--selected': heroineId === t.id }"
            @click="emit('update:heroineId', t.id)"
          >
            <div class="template-card__name">{{ t.name }}</div>
            <div class="template-card__desc">{{ t.desc }}</div>
          </div>
        </div>
      </div>

      <!-- 故事背景 -->
      <div class="field-row">
        <div class="field-label">📖 故事背景（可选，AI 会重点参考这段描述）</div>
        <a-textarea
          :value="storyBackground"
          @update:value="emit('update:storyBackground', $event)"
          :rows="4"
          placeholder="详细描述你的故事：主角是谁？发生了什么？他想做什么？什么在阻碍他？越详细 AI 生成的灵感越贴合你的想法..."
        />
      </div>
    </div>

    <!-- 区块 C：风格（可选） -->
    <div class="quick-step2__section">
      <div class="section-label">🎨 风格偏好（可选）</div>

      <div class="field-row">
        <div class="field-label">写作风格</div>
        <a-textarea
          :value="styleText"
          @update:value="emit('update:styleText', $event)"
          :rows="2"
          placeholder="例如：轻松幽默、热血爽文、细腻文艺..."
        />
      </div>

      <div class="field-row">
        <div class="field-label">参考作品</div>
        <a-input
          :value="referenceWorks"
          @update:value="emit('update:referenceWorks', $event)"
          placeholder="例如：庆余年、斗破苍穹、甄嬛传..."
        />
      </div>

      <div class="field-row">
        <div class="field-label">禁止元素</div>
        <a-input
          :value="forbiddenElements"
          @update:value="emit('update:forbiddenElements', $event)"
          placeholder="不想出现的内容，用逗号分隔"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.quick-step2 {
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
    padding-bottom: 24px;
    border-bottom: 1px solid #2d2d44;

    &:last-child {
      border-bottom: none;
    }
  }
}

.section-label {
  font-size: 15px;
  color: #ccc;
  margin-bottom: 14px;
  font-weight: 600;

  &.required::after {
    content: ' *';
    color: #ff6b6b;
  }
}

.field-row {
  margin-bottom: 16px;
}

.field-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.platform-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.platform-card {
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

  &__icon {
    font-size: 28px;
    margin-bottom: 6px;
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 6px;
  }

  &__meta {
    display: flex;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
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

.meta-chip {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(108, 92, 231, 0.15);
  border: 1px solid rgba(108, 92, 231, 0.3);
  border-radius: 10px;
  color: #a29bfe;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.template-card {
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.35);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
  }

  &__name {
    font-size: 13px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 3px;
  }

  &__desc {
    font-size: 11px;
    color: #999;
    line-height: 1.3;
  }
}

.romance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.romance-card {
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.35);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
  }

  &__name {
    font-size: 13px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 3px;
  }

  &__desc {
    font-size: 11px;
    color: #999;
    line-height: 1.3;
  }
}

:deep(.ant-input),
:deep(.ant-select-selector) {
  background: #1a1a2e !important;
  border-color: rgba(108, 92, 231, 0.3) !important;
  color: #e0e0e0 !important;
}

:deep(.ant-input::placeholder) {
  color: #555 !important;
}
</style>
