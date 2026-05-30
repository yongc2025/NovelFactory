<script setup lang="ts">
import { computed } from 'vue'
import AIAvatar from '@/components/common/AIAvatar.vue'
import type { PipelineStatus } from '@/types'

const props = defineProps<{
  status: PipelineStatus | null
}>()

// 阶段配置：角色 + 阶段名
interface StageConfig {
  key: string
  label: string
  role: 'planner' | 'worldbuilder' | 'character' | 'outliner' | 'metadata' | 'scene' | 'writer' | 'editor' | 'adapter' | 'dramatist'
}

// 流水线只有 6 个阶段（metadata 是内容阶段，不属于流水线）
const stageConfigs: StageConfig[] = [
  { key: 'topic', label: '选题', role: 'planner' },
  { key: 'world', label: '世界观', role: 'worldbuilder' },
  { key: 'characters', label: '角色', role: 'character' },
  { key: 'outline', label: '大纲', role: 'outliner' },
  { key: 'chapters', label: '正文', role: 'writer' },
  { key: 'review', label: '审校', role: 'editor' },
]

// 获取节点状态
function getNodeStatus(stage: string): 'pending' | 'active' | 'done' | 'error' {
  if (!props.status) return 'pending'
  
  const stageStatus = props.status.stages?.find((s) => s.stage === stage)
  if (!stageStatus) return 'pending'
  
  switch (stageStatus.status) {
    case 'completed':
      return 'done'
    case 'running':
    case 'waiting_confirm':
      return 'active'
    case 'failed':
      return 'error'
    default:
      return 'pending'
  }
}

// 获取连线状态
function getConnectorStatus(index: number): 'completed' | 'active' | 'pending' {
  if (!props.status) return 'pending'
  
  const currentStageIndex = stageConfigs.findIndex(
    (s) => s.key === props.status!.current_stage
  )
  
  if (index < currentStageIndex) return 'completed'
  if (index === currentStageIndex) return 'active'
  return 'pending'
}

// 当前阶段进度百分比
const currentProgress = computed(() => {
  if (!props.status) return 0
  const stage = props.status.stages?.find(
    (s) => s.stage === props.status!.current_stage
  )
  return stage?.progress ?? 0
})

// 当前阶段配置
const currentStageConfig = computed(() => {
  if (!props.status) return null
  return stageConfigs.find((s) => s.key === props.status!.current_stage) ?? null
})
</script>

<template>
  <div class="pipeline-progress">
    <div class="pipeline-track">
      <div
        v-for="(stage, index) in stageConfigs"
        :key="stage.key"
        class="pipeline-node"
        :class="`pipeline-node--${getNodeStatus(stage.key)}`"
      >
        <!-- 连线（节点前） -->
        <div
          v-if="index > 0"
          class="pipeline-connector"
          :class="`pipeline-connector--${getConnectorStatus(index - 1)}`"
        ></div>

        <!-- 头像节点 -->
        <div class="pipeline-avatar-wrapper">
          <AIAvatar
            :role="stage.role"
            :status="getNodeStatus(stage.key) === 'active' ? 'working' : getNodeStatus(stage.key) === 'done' ? 'done' : getNodeStatus(stage.key) === 'error' ? 'error' : 'idle'"
            size="default"
          />
        </div>

        <!-- 阶段名称 -->
        <span class="pipeline-label">{{ stage.label }}</span>
      </div>
    </div>

    <!-- 当前阶段进度 -->
    <div v-if="status && currentStageConfig" class="pipeline-current">
      <span class="pipeline-current-label">
        当前阶段：<strong>{{ currentStageConfig.label }}</strong>
      </span>
      <div class="pipeline-progress-bar">
        <div
          class="pipeline-progress-fill"
          :style="{ width: `${currentProgress}%` }"
        ></div>
      </div>
      <span class="pipeline-current-percent">{{ currentProgress }}%</span>
    </div>
  </div>
</template>

<style scoped lang="less">
@import '@/styles/design-tokens.less';

.pipeline-progress {
  padding: @space-md 0;
}

.pipeline-track {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
}

.pipeline-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;

  &:first-child {
    .pipeline-connector {
      display: none;
    }
  }
}

.pipeline-connector {
  position: absolute;
  top: 24px;
  left: -50%;
  width: 100%;
  height: 2px;
  z-index: 0;

  &--completed {
    background: linear-gradient(90deg, @color-secondary, @color-primary);
  }

  &--active {
    background: linear-gradient(90deg, @color-primary, @color-primary-light);
    animation: connectorPulse 1.5s ease-in-out infinite;
  }

  &--pending {
    background: @color-border;
    background-image: repeating-linear-gradient(
      90deg,
      transparent,
      transparent 4px,
      @color-bg-elevated 4px,
      @color-bg-elevated 8px
    );
  }
}

.pipeline-avatar-wrapper {
  position: relative;
  z-index: 1;
}

.pipeline-label {
  margin-top: @space-sm;
  font-size: @font-size-xs;
  color: @color-text-secondary;
  white-space: nowrap;

  .pipeline-node--active & {
    color: @color-primary-light;
    font-weight: @font-weight-semibold;
  }

  .pipeline-node--done & {
    color: @color-secondary;
  }

  .pipeline-node--error & {
    color: @color-error;
  }
}

.pipeline-current {
  display: flex;
  align-items: center;
  gap: @space-md;
  margin-top: @space-lg;
  padding: @space-sm @space-md;
  background: @color-bg;
  border-radius: @radius-md;
}

.pipeline-current-label {
  font-size: @font-size-sm;
  color: @color-text-secondary;
  white-space: nowrap;

  strong {
    color: @color-primary-light;
  }
}

.pipeline-progress-bar {
  flex: 1;
  height: 6px;
  background: @color-border;
  border-radius: @radius-full;
  overflow: hidden;
}

.pipeline-progress-fill {
  height: 100%;
  background: @gradient-primary;
  border-radius: @radius-full;
  transition: width @transition-normal;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: shimmer 1.5s ease-in-out infinite;
  }
}

.pipeline-current-percent {
  font-size: @font-size-sm;
  font-weight: @font-weight-semibold;
  color: @color-primary-light;
  min-width: 36px;
  text-align: right;
}

@keyframes connectorPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

// 响应式：小屏幕时缩小
@media (max-width: @screen-md) {
  .pipeline-avatar-wrapper {
    transform: scale(0.8);
  }

  .pipeline-label {
    font-size: 10px;
  }
}
</style>
