<script setup lang="ts">
import { computed } from 'vue'
import { Input } from 'ant-design-vue'
import { STEP_HINTS } from './presets'

const props = defineProps<{
  freeText: string
}>()

const emit = defineEmits<{
  'update:freeText': [value: string]
}>()

const hint = STEP_HINTS.style

const isComplete = computed(() => props.freeText.trim().length > 0)
defineExpose({ isComplete })
</script>

<template>
  <div class="step-style">
    <div class="step-style__header">
      <h3>{{ hint.title }}</h3>
      <p class="step-style__subtitle">{{ hint.subtitle }}</p>
    </div>

    <div class="step-style__input">
      <Input.TextArea
        :value="freeText"
        @update:value="emit('update:freeText', $event)"
        :rows="5"
        :placeholder="hint.placeholder"
        class="style-textarea"
      />
      <div class="char-count">{{ freeText.length }} 字</div>
    </div>
  </div>
</template>

<style scoped lang="less">
.step-style {
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

  &__input {
    max-width: 700px;
    margin: 0 auto;
    position: relative;
  }
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #666;
  margin-top: 6px;
}

.style-textarea {
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
