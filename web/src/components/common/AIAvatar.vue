<script setup lang="ts">
import { computed } from 'vue'

/** AI 角色类型 */
type AIRole = 
  | 'planner'
  | 'worldbuilder'
  | 'character'
  | 'outliner'
  | 'metadata'
  | 'scene'
  | 'writer'
  | 'editor'
  | 'adapter'
  | 'dramatist'

/** 头像状态 */
type AvatarStatus = 'idle' | 'working' | 'done' | 'error'

const props = withDefaults(defineProps<{
  role: AIRole
  status?: AvatarStatus
  size?: 'small' | 'default' | 'large'
}>(), {
  status: 'idle',
  size: 'default',
})

// 角色配置映射
const roleConfig: Record<AIRole, { emoji: string; color: string; name: string }> = {
  planner: { emoji: '🎯', color: '#6C5CE7', name: '策划经理' },
  worldbuilder: { emoji: '🌍', color: '#0984E3', name: '世界观架构师' },
  character: { emoji: '👤', color: '#E17055', name: '角色设计师' },
  outliner: { emoji: '📋', color: '#00B894', name: '大纲编剧' },
  metadata: { emoji: '📝', color: '#FDCB6E', name: '元数据师' },
  scene: { emoji: '🎬', color: '#E84393', name: '场景编剧' },
  writer: { emoji: '✍️', color: '#00CEC9', name: '正文作者' },
  editor: { emoji: '🔍', color: '#A29BFE', name: '编辑审校' },
  adapter: { emoji: '📝', color: '#FD79A8', name: '内容适配师' },
  dramatist: { emoji: '🎬', color: '#FF7675', name: '剧本改编编剧' },
}

const config = computed(() => roleConfig[props.role])

const sizeMap = {
  small: 36,
  default: 48,
  large: 64,
}

const sizePx = computed(() => sizeMap[props.size])

const containerStyle = computed(() => ({
  width: `${sizePx.value}px`,
  height: `${sizePx.value}px`,
  '--role-color': config.value.color,
}))
</script>

<template>
  <div
    class="ai-avatar"
    :class="[
      `ai-avatar--${status}`,
      `ai-avatar--${size}`,
    ]"
    :style="containerStyle"
    :title="config.name"
  >
    <!-- 头像主体 -->
    <div class="ai-avatar__inner">
      <span class="ai-avatar__emoji">{{ config.emoji }}</span>
    </div>

    <!-- 状态指示器 -->
    <div v-if="status === 'working'" class="ai-avatar__ring ai-avatar__ring--working"></div>
    <div v-if="status === 'done'" class="ai-avatar__badge ai-avatar__badge--done">✓</div>
    <div v-if="status === 'error'" class="ai-avatar__badge ai-avatar__badge--error">✕</div>
  </div>
</template>

<style scoped lang="less">
@import '@/styles/design-tokens.less';

.ai-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &__inner {
    width: 100%;
    height: 100%;
    border-radius: @radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--role-color);
    background: linear-gradient(135deg, var(--role-color) 0%, color-mix(in srgb, var(--role-color) 70%, #fff) 100%);
    transition: all @transition-normal;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }

  &__emoji {
    font-size: 1em;
    line-height: 1;
  }

  // 尺寸变体
  &--small {
    .ai-avatar__emoji {
      font-size: 16px;
    }
  }

  &--default {
    .ai-avatar__emoji {
      font-size: 22px;
    }
  }

  &--large {
    .ai-avatar__emoji {
      font-size: 30px;
    }
  }

  // 空闲状态
  &--idle {
    .ai-avatar__inner {
      opacity: 0.7;
    }
  }

  // 工作状态：脉冲发光 + 旋转
  &--working {
    .ai-avatar__inner {
      opacity: 1;
      animation: avatarPulse 1.5s ease-in-out infinite;
    }

    .ai-avatar__ring--working {
      position: absolute;
      inset: -4px;
      border-radius: @radius-full;
      border: 2px solid var(--role-color);
      opacity: 0.6;
      animation: avatarRingPulse 1.5s ease-in-out infinite;
    }
  }

  // 完成状态
  &--done {
    .ai-avatar__inner {
      opacity: 1;
      box-shadow: 0 0 12px rgba(0, 184, 148, 0.4);
    }
  }

  // 错误状态
  &--error {
    .ai-avatar__inner {
      opacity: 1;
      box-shadow: 0 0 12px rgba(255, 118, 117, 0.4);
      animation: avatarShake 0.5s ease-in-out;
    }
  }

  // 状态徽章
  &__badge {
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 16px;
    height: 16px;
    border-radius: @radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: @font-weight-bold;
    color: #fff;
    border: 2px solid @color-bg-elevated;

    &--done {
      background: @color-success;
    }

    &--error {
      background: @color-error;
    }
  }
}

// 脉冲动画
@keyframes avatarPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 20px var(--role-color), 0 0 40px rgba(0, 0, 0, 0.2);
  }
}

// 光环脉冲
@keyframes avatarRingPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.15);
    opacity: 0;
  }
}

// 抖动动画
@keyframes avatarShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-3px); }
  40% { transform: translateX(3px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
}
</style>
