<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button, Input } from 'ant-design-vue'
import { ReloadOutlined, EditOutlined } from '@ant-design/icons-vue'

export interface InspirationVersion {
  id: string
  synopsis: string
  titles: string[]
  selected: boolean
}

const props = defineProps<{
  versions: InspirationVersion[]
  loading: boolean
  generated: boolean
}>()

const emit = defineEmits<{
  generate: []
  regenerate: []
  'select-version': [id: string]
  'update-synopsis': [id: string, text: string]
  'update-title': [id: string, index: number, text: string]
  'regenerate-with-direction': [direction: string]
}>()

const directionInput = ref('')

function handleSelect(id: string) {
  emit('select-version', id)
}

function handleRegenerate() {
  emit('regenerate')
}

function handleRegenerateWithDirection() {
  if (directionInput.value.trim()) {
    emit('regenerate-with-direction', directionInput.value.trim())
    directionInput.value = ''
  }
}

const selectedVersion = computed(() => props.versions.find(v => v.selected))
defineExpose({ selectedVersion })
</script>

<template>
  <div class="quick-step3">
    <div class="quick-step3__header">
      <h3>AI 生成灵感</h3>
      <p class="quick-step3__subtitle">基于你的选择，AI 为你构思故事</p>
    </div>

    <!-- 未生成时：显示生成按钮 -->
    <div v-if="!generated && !loading" class="quick-step3__start">
      <div class="start-illustration">✨</div>
      <p class="start-text">一切准备就绪，点击按钮让 AI 为你构思 2-3 个故事灵感</p>
      <Button type="primary" size="large" class="generate-btn" @click="emit('generate')">
        ✨ 生成灵感
      </Button>
    </div>

    <!-- 生成中 -->
    <div v-if="loading" class="quick-step3__loading">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <p class="loading-text">AI 正在构思中，请稍候...</p>
      <p class="loading-hint">通常需要 10-30 秒</p>
    </div>

    <!-- 生成完成：显示灵感 -->
    <div v-if="generated && !loading" class="quick-step3__results">
      <div class="results-header">
        <span class="results-label">✨ AI 生成的故事灵感</span>
      </div>

      <div class="versions-list">
        <div
          v-for="version in versions"
          :key="version.id"
          class="version-card version-card--selected"
        >
          <div class="version-card__content">
            <!-- 书名备选 -->
            <div class="version-card__titles">
              <span class="titles-label">📖 备选书名：</span>
              <div class="titles-list">
                <span
                  v-for="(title, idx) in version.titles"
                  :key="idx"
                  class="title-tag"
                >{{ title }}</span>
              </div>
            </div>

            <!-- 故事梗概 -->
            <div class="version-card__synopsis">
              <span class="synopsis-label">📝 故事梗概：</span>
              <a-textarea
                :value="version.synopsis"
                @update:value="emit('update-synopsis', version.id, $event)"
                :rows="7"
                class="synopsis-textarea"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 强调方向重新生成 -->
      <div class="regenerate-section">
        <div class="regenerate-row">
          <Button @click="handleRegenerate">
            <ReloadOutlined /> 重新生成
          </Button>
          <div class="direction-input">
            <a-input
              v-model:value="directionInput"
              placeholder="想强调什么方向？（如：更虐一点、更轻松日常...）"
              @pressEnter="handleRegenerateWithDirection"
            />
            <Button
              size="small"
              :disabled="!directionInput.trim()"
              @click="handleRegenerateWithDirection"
            >
              <ReloadOutlined /> 按方向生成
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.quick-step3 {
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
}

// 开始区域
.quick-step3__start {
  text-align: center;
  padding: 48px 0;
}

.start-illustration {
  font-size: 72px;
  margin-bottom: 20px;
}

.start-text {
  font-size: 15px;
  color: #999;
  margin-bottom: 24px;
  line-height: 1.6;
}

.generate-btn {
  height: 48px;
  padding: 0 48px;
  font-size: 16px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
  border: none;
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4);

  &:hover {
    background: linear-gradient(135deg, #5a4bd6 0%, #8c82fc 100%);
    box-shadow: 0 6px 24px rgba(108, 92, 231, 0.5);
  }
}

// 加载中
.quick-step3__loading {
  text-align: center;
  padding: 64px 0;
}

.loading-spinner {
  margin-bottom: 24px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(108, 92, 231, 0.2);
  border-top-color: #6c5ce7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.loading-hint {
  font-size: 13px;
  color: #666;
}

// 结果区域
.quick-step3__results {
  .results-header {
    margin-bottom: 16px;
  }

  .results-label {
    font-size: 15px;
    color: #ccc;
    font-weight: 500;
  }
}

.versions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.version-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.12);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(108, 92, 231, 0.3);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.08);
    box-shadow: 0 0 20px rgba(108, 92, 231, 0.15);
  }

  &__select {
    flex-shrink: 0;
    padding-top: 4px;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__titles {
    margin-bottom: 12px;
  }

  &__synopsis {
    .synopsis-label,
    .titles-label {
      font-size: 13px;
      color: #999;
      display: block;
      margin-bottom: 6px;
    }
  }
}

.radio-dot {
  width: 20px;
  height: 20px;
  border: 2px solid #555;
  border-radius: 50%;
  transition: all 0.2s;

  &--active {
    border-color: #6c5ce7;
    background: #6c5ce7;
    box-shadow: inset 0 0 0 4px #1a1a2e;
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

.synopsis-textarea {
  background: #16162a;
  border-color: rgba(108, 92, 231, 0.2);
  color: #e0e0e0;
  resize: vertical;
}

:deep(.ant-input) {
  background: #16162a;
  color: #e0e0e0;
  border-color: rgba(108, 92, 231, 0.2);
}

:deep(.ant-input:focus) {
  border-color: #6c5ce7;
  box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.15);
}

// 重新生成区域
.regenerate-section {
  padding-top: 16px;
  border-top: 1px solid #2d2d44;
}

.regenerate-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.direction-input {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;

  .ant-input {
    flex: 1;
    min-width: 0;
  }
}
</style>
