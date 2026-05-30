<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Tag, Input, Select, Empty, Tooltip, Modal, message } from 'ant-design-vue'
import {
  PlusOutlined,
  SearchOutlined,
  PlayCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  BookOutlined,
} from '@ant-design/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import AIAvatar from '@/components/common/AIAvatar.vue'
import { useProjectStore } from '@/stores/project'
import type { Project, PipelineStage } from '@/types'

const router = useRouter()
const store = useProjectStore()

onMounted(() => {
  store.fetchProjects()
})

// 搜索与筛选
const searchText = ref('')
const statusFilter = ref<string | undefined>(undefined)

const filteredProjects = computed(() => {
  let list = store.sortedProjects
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    list = list.filter(
      (p) =>
        p.title.toLowerCase().includes(keyword) ||
        p.genre.toLowerCase().includes(keyword)
    )
  }
  if (statusFilter.value) {
    list = list.filter((p) => p.status === statusFilter.value)
  }
  return list
})

// 统计数据
const totalProjects = computed(() => store.projects.length)
const generatingCount = computed(
  () => store.projects.filter((p) => p.status === 'generating').length
)
const completedCount = computed(
  () => store.projects.filter((p) => p.status === 'completed').length
)
const totalWords = computed(() => {
  return store.projects.reduce((sum, p: any) => {
    const words = p.word_count_target || 0
    if (p.status === 'completed') return sum + words
    if (p.current_stage === 'chapters' || p.current_stage === 'review')
      return sum + Math.round(words * 0.8)
    return sum
  }, 0)
})

// 状态配置
const statusConfig: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: '草稿' },
  generating: { color: 'processing', label: '生成中' },
  reviewing: { color: 'warning', label: '审校中' },
  completed: { color: 'success', label: '已完成' },
  failed: { color: 'error', label: '失败' },
}

// 流水线阶段配置
const stageOrder: PipelineStage[] = ['topic', 'world', 'characters', 'outline', 'chapters', 'review']
const stageEmoji: Record<string, string> = {
  topic: '🎯',
  world: '🌍',
  characters: '👤',
  outline: '📋',
  chapters: '✍️',
  review: '🔍',
}

// 获取当前阶段索引
function getStageIndex(project: Project): number {
  return stageOrder.indexOf((project as any).current_stage || 'topic')
}

// 获取阶段状态
function getStageStatus(project: Project, stage: PipelineStage): 'pending' | 'active' | 'done' {
  const currentIdx = getStageIndex(project)
  const stageIdx = stageOrder.indexOf(stage)
  if (stageIdx < currentIdx) return 'done'
  if (stageIdx === currentIdx) return 'active'
  return 'pending'
}

// 格式化字数
function formatWordCount(count: number): string {
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万`
  return count.toString()
}

// 格式化时间
function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 统计卡片数据
const statCards = computed(() => [
  {
    title: '总项目数',
    value: totalProjects.value,
    icon: BookOutlined,
    gradient: 'linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%)',
    shadow: '0 8px 24px rgba(108, 92, 231, 0.3)',
  },
  {
    title: '进行中',
    value: generatingCount.value,
    icon: SyncOutlined,
    gradient: 'linear-gradient(135deg, #0984E3 0%, #74B9FF 100%)',
    shadow: '0 8px 24px rgba(9, 132, 227, 0.3)',
  },
  {
    title: '已完成',
    value: completedCount.value,
    icon: CheckCircleOutlined,
    gradient: 'linear-gradient(135deg, #00B894 0%, #55EFC4 100%)',
    shadow: '0 8px 24px rgba(0, 184, 148, 0.3)',
  },
  {
    title: '总字数',
    value: formatWordCount(totalWords.value),
    icon: FileTextOutlined,
    gradient: 'linear-gradient(135deg, #FD79A8 0%, #FDCFE8 100%)',
    shadow: '0 8px 24px rgba(253, 121, 168, 0.3)',
  },
])

// 操作
function goToCreate() {
  router.push('/projects/create')
}

function goToDetail(id: string) {
  router.push(`/projects/${id}`)
}

function handleDelete(e: Event, id: string) {
  e.stopPropagation()
  Modal.confirm({
    title: '确认删除',
    content: '删除后不可恢复，确认要删除这个项目吗？',
    okText: '确认删除',
    cancelText: '取消',
    okButtonProps: { danger: true },
    async onOk() {
      try {
        await store.deleteProject(id)
        message.success('项目已删除')
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <AppLayout>
    <div class="dashboard">
      <!-- 欢迎头部 -->
      <div class="welcome-section slide-up">
        <div class="welcome-text">
          <h1 class="welcome-title">👋 欢迎来到 NovelFactory</h1>
          <p class="welcome-subtitle">AI 驱动的小说创作工厂 — 让灵感成真</p>
        </div>
        <Button type="primary" size="large" class="create-btn" @click="goToCreate">
          <PlusOutlined /> 新建项目
        </Button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div
          v-for="(card, index) in statCards"
          :key="card.title"
          class="stat-card slide-up"
          :style="{ animationDelay: `${(index + 1) * 100}ms`, background: card.gradient, boxShadow: card.shadow }"
        >
          <div class="stat-card-content">
            <div class="stat-icon">
              <component :is="card.icon" />
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ card.value }}</span>
              <span class="stat-title">{{ card.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索与筛选栏 -->
      <div class="filter-bar slide-up" style="animation-delay: 500ms">
        <Input
          v-model:value="searchText"
          placeholder="搜索项目名称或题材..."
          class="search-input"
          allow-clear
        >
          <template #prefix>
            <SearchOutlined style="color: var(--color-text-tertiary)" />
          </template>
        </Input>
        <Select
          v-model:value="statusFilter"
          placeholder="筛选状态"
          allow-clear
          class="status-filter"
          :options="[
            { value: 'draft', label: '草稿' },
            { value: 'generating', label: '生成中' },
            { value: 'reviewing', label: '审校中' },
            { value: 'completed', label: '已完成' },
            { value: 'failed', label: '失败' },
          ]"
        />
      </div>

      <!-- 项目卡片网格 -->
      <div v-if="filteredProjects.length > 0" class="projects-grid">
        <div
          v-for="(project, index) in filteredProjects"
          :key="project.id"
          class="project-card slide-up"
          :style="{ animationDelay: `${(index + 6) * 50}ms` }"
          @click="goToDetail(project.id)"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <h3 class="card-title">{{ project.title }}</h3>
            <Tag
              :color="statusConfig[project.status]?.color || 'default'"
              class="status-tag"
            >
              {{ statusConfig[project.status]?.label || project.status }}
            </Tag>
          </div>

          <!-- 题材标签 -->
          <div class="card-genre">
            <Tag color="purple" class="genre-tag">{{ (project.genre || '').slice(0, 10) }}{{ (project.genre || '').length > 10 ? '...' : '' }}</Tag>
          </div>

          <!-- 流水线进度 -->
          <div class="card-pipeline">
            <div
              v-for="stage in stageOrder"
              :key="stage"
              class="pipeline-dot"
              :class="`pipeline-dot--${getStageStatus(project, stage)}`"
              :title="stage"
            >
              <span class="dot-emoji">{{ stageEmoji[stage] }}</span>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="card-stats">
            <div class="stat-item">
              <FileTextOutlined class="stat-item-icon" />
              <span>{{ formatWordCount((project as any).word_count_target || 0) }}字</span>
            </div>
            <div class="stat-item">
              <BookOutlined class="stat-item-icon" />
              <span>{{ (project as any).platform || '--' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-item-time">{{ formatTime((project as any).updated_at || project.created_at || '') }}</span>
            </div>
          </div>

          <!-- 快捷操作 -->
          <div class="card-actions">
            <Tooltip title="查看">
              <Button type="text" size="small" @click.stop="goToDetail(project.id)">
                <EyeOutlined />
              </Button>
            </Tooltip>
            <Tooltip v-if="project.status === 'draft'" title="启动流水线">
              <Button type="text" size="small" @click.stop="goToDetail(project.id)">
                <PlayCircleOutlined style="color: var(--color-secondary)" />
              </Button>
            </Tooltip>
            <Tooltip title="删除">
              <Button type="text" size="small" danger @click="(e: Event) => handleDelete(e, project.id)">
                <DeleteOutlined />
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state slide-up">
        <Empty :image="Empty.PRESENTED_IMAGE_SIMPLE">
          <template #description>
            <span class="empty-title">还没有项目</span>
            <span class="empty-subtitle">创建你的第一个项目，开始 AI 创作之旅</span>
          </template>
          <Button type="primary" size="large" @click="goToCreate">
            <PlusOutlined /> 创建第一个项目
          </Button>
        </Empty>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped lang="less">
@import '@/styles/design-tokens.less';

.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

// 欢迎区域
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: @space-xl;
  flex-wrap: wrap;
  gap: @space-md;
}

.welcome-title {
  font-size: @font-size-2xl;
  font-weight: @font-weight-bold;
  color: @color-text;
  margin: 0;
  line-height: @line-height-tight;
}

.welcome-subtitle {
  font-size: @font-size-base;
  color: @color-text-secondary;
  margin: @space-xs 0 0 0;
}

.create-btn {
  height: 44px;
  padding: 0 @space-xl;
  font-size: @font-size-base;
  border-radius: @radius-lg;
  box-shadow: @shadow-glow-primary;
}

// 统计卡片网格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: @space-md;
  margin-bottom: @space-xl;
}

.stat-card {
  border-radius: @radius-xl;
  padding: @space-lg;
  color: #fff;
  position: relative;
  overflow: hidden;
  transition: transform @transition-fast;

  &:hover {
    transform: translateY(-2px);
  }

  // 装饰性背景圆
  &::before {
    content: '';
    position: absolute;
    top: -20px;
    right: -20px;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -30px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
  }
}

.stat-card-content {
  display: flex;
  align-items: center;
  gap: @space-md;
  position: relative;
  z-index: 1;
}

.stat-icon {
  font-size: 32px;
  opacity: 0.9;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: @font-size-3xl;
  font-weight: @font-weight-bold;
  line-height: @line-height-tight;
}

.stat-title {
  font-size: @font-size-sm;
  opacity: 0.85;
  margin-top: 2px;
}

// 搜索与筛选
.filter-bar {
  display: flex;
  gap: @space-md;
  margin-bottom: @space-xl;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.status-filter {
  width: 160px;
}

// 项目卡片网格
.projects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: @space-lg;
}

.project-card {
  background: @color-bg-elevated;
  border: 1px solid @color-border;
  border-radius: @radius-xl;
  padding: @space-lg;
  cursor: pointer;
  transition: all @transition-normal;

  &:hover {
    border-color: @color-primary;
    box-shadow: @shadow-glow-primary;
    transform: translateY(-2px);
  }
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: @space-sm;
  margin-bottom: @space-sm;
}

.card-title {
  font-size: @font-size-lg;
  font-weight: @font-weight-semibold;
  color: @color-text;
  margin: 0;
  line-height: @line-height-tight;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.status-tag {
  flex-shrink: 0;
}

.card-genre {
  margin-bottom: @space-md;
}

.genre-tag {
  font-size: @font-size-xs;
}

// 流水线进度点
.card-pipeline {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: @space-md;
  padding: @space-sm 0;
}

.pipeline-dot {
  flex: 1;
  height: 32px;
  border-radius: @radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  background: @color-bg;
  border: 1px solid @color-border;
  transition: all @transition-normal;

  .dot-emoji {
    font-size: 14px;
  }

  &--done {
    background: rgba(0, 184, 148, 0.15);
    border-color: @color-secondary;

    .dot-emoji {
      filter: none;
    }
  }

  &--active {
    background: @color-primary-bg;
    border-color: @color-primary;
    animation: dotPulse 2s ease-in-out infinite;

    .dot-emoji {
      filter: none;
    }
  }

  &--pending {
    opacity: 0.5;

    .dot-emoji {
      filter: grayscale(1);
    }
  }
}

@keyframes dotPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(108, 92, 231, 0.3);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.1);
  }
}

// 统计信息
.card-stats {
  display: flex;
  align-items: center;
  gap: @space-md;
  margin-bottom: @space-md;
  padding-top: @space-sm;
  border-top: 1px solid @color-border;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: @font-size-sm;
  color: @color-text-secondary;
}

.stat-item-icon {
  font-size: @font-size-sm;
  color: @color-text-tertiary;
}

.stat-item-time {
  color: @color-text-tertiary;
  font-size: @font-size-xs;
}

// 快捷操作
.card-actions {
  display: flex;
  align-items: center;
  gap: @space-xs;
  padding-top: @space-sm;
  border-top: 1px solid @color-border;
  opacity: 0;
  transition: opacity @transition-fast;

  .project-card:hover & {
    opacity: 1;
  }
}

// 空状态
.empty-state {
  padding: @space-3xl 0;
  text-align: center;
}

.empty-title {
  display: block;
  font-size: @font-size-lg;
  font-weight: @font-weight-semibold;
  color: @color-text;
  margin-bottom: @space-sm;
}

.empty-subtitle {
  display: block;
  color: @color-text-secondary;
}

// 响应式
@media (max-width: @screen-xl) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: @screen-md) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .status-filter {
    width: 100%;
  }
}
</style>
