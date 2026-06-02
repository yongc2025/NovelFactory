<script setup lang="ts">
import { computed } from "vue";
import { Textarea } from "ant-design-vue";
import {
  STEP_HINTS,
  PROTAGONIST_TEMPLATES,
  HEROINE_TEMPLATES,
} from "./presets";

const props = defineProps<{
  gender: "male" | "female" | "both";
  selectedProtagonist: string | null;
  selectedHeroine: string | null;
  romanceMode: string | null;
  freeText: string;
}>();

const emit = defineEmits<{
  "select:protagonist": [id: string];
  "select:heroine": [id: string];
  "update:freeText": [value: string];
}>();

const hint = STEP_HINTS.character;

// 根据性别过滤主角模板
const protagonistOptions = computed(() =>
  PROTAGONIST_TEMPLATES.filter((t) => t.gender === props.gender),
);

// 是否显示女主选择（男频 + 选择了有女主的感情线）
const showHeroine = computed(
  () =>
    props.gender === "male" &&
    props.romanceMode &&
    props.romanceMode !== "none",
);
</script>

<template>
  <div class="step-character">
    <div class="step-character__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-character__subtitle">{{ hint.subtitle }}</p>
    </div>

    <!-- 主角性格模板 -->
    <div class="step-character__section">
      <div class="section-label">🧑 主角性格（点击选择，或跳过自由描述）</div>
      <div class="template-grid">
        <div
          v-for="t in protagonistOptions"
          :key="t.id"
          class="template-card"
          :class="{ 'template-card--selected': selectedProtagonist === t.id }"
          @click="emit('select:protagonist', t.id)"
        >
          <div class="template-card__name">{{ t.name }}</div>
          <div class="template-card__desc">{{ t.desc }}</div>
          <div class="template-card__example">{{ t.example }}</div>
        </div>
      </div>
    </div>

    <!-- 女主性格模板（条件显示） -->
    <div v-if="showHeroine" class="step-character__section">
      <div class="section-label">💃 女主性格</div>
      <div class="template-grid">
        <div
          v-for="t in HEROINE_TEMPLATES"
          :key="t.id"
          class="template-card"
          :class="{ 'template-card--selected': selectedHeroine === t.id }"
          @click="emit('select:heroine', t.id)"
        >
          <div class="template-card__name">{{ t.name }}</div>
          <div class="template-card__desc">{{ t.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 自由输入补充 -->
    <div class="step-character__free">
      <div class="section-label">✏️ 补充说明（可选）</div>
      <Textarea
        :value="freeText"
        @update:value="emit('update:freeText', $event)"
        :rows="3"
        placeholder="补充主角的其他特点，如：口头禅、特殊能力、背景故事...或者直接描述你心中的主角形象"
        class="free-textarea"
      />
    </div>
  </div>
</template>

<style scoped lang="less">
.step-character {
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

  &__section {
    margin-bottom: 24px;
  }

  &__free {
    margin-top: 8px;
  }
}

.section-label {
  font-size: 14px;
  color: #ccc;
  margin-bottom: 12px;
  font-weight: 500;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.template-card {
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.35);
    transform: translateY(-1px);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 4px;
  }

  &__desc {
    font-size: 12px;
    color: #999;
    line-height: 1.4;
    margin-bottom: 6px;
  }

  &__example {
    font-size: 11px;
    color: #666;
    font-style: italic;
  }
}

.free-textarea {
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
