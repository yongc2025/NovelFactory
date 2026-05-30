<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Card,
  Button,
  Tag,
  Space,
  Typography,
  Tabs,
  TabPane,
  Spin,
  message,
} from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  PlayCircleOutlined,
  BulbOutlined,
  GlobalOutlined,
  TeamOutlined,
  FileTextOutlined,
  ReadOutlined,
  CheckCircleOutlined,
  EditOutlined,
  CloseOutlined,
} from '@ant-design/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import PipelineProgress from '@/components/project/PipelineProgress.vue'
import TopicCard from '@/components/project/TopicCard.vue'
import WorldPanel from '@/components/project/WorldPanel.vue'
import CharacterCard from '@/components/project/CharacterCard.vue'
import OutlineEditor from '@/components/project/OutlineEditor.vue'
import MetadataEditor from '@/components/project/MetadataEditor.vue'
import ChapterReader from '@/components/project/ChapterReader.vue'
import ReviewReport from '@/components/project/ReviewReport.vue'
import StageConfirm from '@/components/common/StageConfirm.vue'
import { useProjectStore } from '@/stores/project'
import type { ConfirmAction, BookMetadata } from '@/types'

const { Title, Text } = Typography

const route = useRoute()
const router = useRouter()
const store = useProjectStore()

const projectId = computed(() => route.params.id as string)
const activeTab = computed(() => (route.meta.tab as string) || 'overview')
const stageActionLoading = ref(false)
const stageActionText = ref('')
const globalLoading = computed(() => store.loading || stageActionLoading.value)
const currentChapterNum = computed(() => {
  const num = route.params.num
  return num ? parseInt(num as string) : 1
})

// 阶段名称映射
const stageNames: Record<string, string> = {
  topic: '选题方案',
  world: '世界观',
  character: '角色设定',
  characters: '角色设定',
  outline: '大纲',
  metadata: '书籍元数据',
  draft: '正文',
  scene: '场景细纲',
  chapters: '正文',
  review: '审校报告',
}

// 横向 Tab 配置
const tabItems = [
  { key: 'overview', label: '项目概览', icon: BulbOutlined },
  { key: 'topic', label: '选题方案', icon: BulbOutlined },
  { key: 'world', label: '世界观', icon: GlobalOutlined },
  { key: 'characters', label: '角色列表', icon: TeamOutlined },
  { key: 'outline', label: '大纲编辑', icon: FileTextOutlined },
  { key: 'metadata', label: '书籍元数据', icon: ReadOutlined },
  { key: 'chapters', label: '正文阅读', icon: ReadOutlined },
  { key: 'review', label: '审校报告', icon: CheckCircleOutlined },
]

// 阶段顺序（用于自动切换）
const tabOrder = ['topic', 'world', 'characters', 'outline', 'metadata', 'chapters', 'review']
const tabToStage: Record<string, string> = {
  topic: 'topic',
  world: 'world',
  characters: 'character',
  outline: 'outline',
  metadata: 'metadata',
  chapters: 'draft',
  review: 'review',
}
const activeBackendStage = computed(() => tabToStage[activeTab.value] ?? null)
const currentStageStatus = computed(() => {
  const stage = activeBackendStage.value
  if (!stage) return null
  return store.pipelineStatus?.stages?.find((item) => item.stage === stage) ?? null
})
const isCurrentStageWaitingConfirm = computed(() => {
  const stage = activeBackendStage.value
  if (!stage) return false
  const stageStatus = currentStageStatus.value?.status
  // 该阶段本身是 waiting_confirm，或流水线处于 confirming 状态
  return stageStatus === 'waiting_confirm' || (store.pipelineStatus?.status === 'confirming' && store.pipelineStatus?.current_stage === stage)
})
const shouldShowStageConfirm = computed(() => activeTab.value !== 'overview' && isCurrentStageWaitingConfirm.value)
const canApproveCurrentStage = computed(() => shouldShowStageConfirm.value)
const approveButtonTitle = computed(() => canApproveCurrentStage.value ? '采用当前阶段内容' : '当前阶段不在待确认状态')
const stageConfirmName = computed(() => stageNames[activeBackendStage.value ?? ''] || stageNames[activeTab.value] || '')
const stageConfirmDescription = computed(() => {
  if (activeTab.value === 'topic') {
    return '请选择一个方案采用，或提交反馈后重新生成选题方案。'
  }
  return '请审阅当前阶段内容，确认采用、提交反馈或重新生成。'
})

function onTabChange(key: string | number) {
  const tabKey = String(key)
  if (tabKey === 'overview') {
    router.push(`/projects/${projectId.value}`)
  } else {
    router.push(`/projects/${projectId.value}/${tabKey}`)
  }
}

// 加载数据
onMounted(async () => {
  await store.fetchProject(projectId.value)
  await store.fetchPipelineStatus(projectId.value)
})

// 根据 tab 加载对应数据
watch([activeTab, currentChapterNum], async ([tab, chapterNum]) => {
  const id = projectId.value
  switch (tab) {
    case 'topic': await store.fetchTopic(id); break
    case 'world': await store.fetchWorld(id); break
    case 'characters': await store.fetchCharacters(id); break
    case 'outline': await store.fetchOutline(id); break
    case 'metadata': await store.fetchMetadata(id); break
    case 'chapters': await store.fetchChapter(id, chapterNum); break
    case 'review': await store.fetchReview(id); break
  }
}, { immediate: true })

// 章节导航
function prevChapter() {
  if (currentChapterNum.value > 1) {
    router.push(`/projects/${projectId.value}/chapters/${currentChapterNum.value - 1}`)
  }
}

function nextChapter() {
  const total = store.outline?.total_chapters || 999
  if (currentChapterNum.value < total) {
    router.push(`/projects/${projectId.value}/chapters/${currentChapterNum.value + 1}`)
  }
}

// 启动流水线
async function handleStartPipeline() {
  if (stageActionLoading.value) return
  stageActionLoading.value = true
  stageActionText.value = '正在启动生成流水线...'
  try {
    await store.startPipeline(projectId.value)
    message.success('流水线已启动！')
  } catch (error: any) {
    message.error(error.message || '启动失败')
  } finally {
    stageActionLoading.value = false
    stageActionText.value = ''
  }
}

// 等待阶段完成（轮询）
async function waitForStageComplete(id: string, stage: string) {
  const maxAttempts = 150 // 最多 5 分钟
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(r => setTimeout(r, 2000))
    await store.fetchPipelineStatus(id)
    const st = store.pipelineStatus?.stages?.find(s => s.stage === stage)
    if (st && (st.status === 'completed' || st.status === 'waiting_confirm' || st.status === 'failed')) {
      return st
    }
  }
  return null
}

async function loadStageData(stage: string) {
  switch (stage) {
    case 'topic': await store.fetchTopic(projectId.value); break
    case 'world': await store.fetchWorld(projectId.value); break
    case 'character': await store.fetchCharacters(projectId.value); break
    case 'outline': await store.fetchOutline(projectId.value); break
    case 'metadata': await store.fetchMetadata(projectId.value); break
    case 'draft': await store.fetchChapter(projectId.value, 1); break
    case 'review': await store.fetchReview(projectId.value); break
  }
}

function getNextTabKey(tab: string): string | null {
  const currentIdx = tabOrder.indexOf(tab)
  if (currentIdx < 0 || currentIdx >= tabOrder.length - 1) return null
  return tabOrder[currentIdx + 1]
}

async function runStageInternal(stage: string, feedback?: string) {
  await store.runStage(projectId.value, stage, feedback)
  const status = await waitForStageComplete(projectId.value, stage)
  if (!status) {
    throw new Error('阶段生成超时')
  }
  if (status.status === 'failed') {
    throw new Error(status.error || '阶段生成失败')
  }
  await loadStageData(stage)
}

// 运行阶段
async function handleRunStage(stage: string) {
  if (stageActionLoading.value) return
  stageActionLoading.value = true
  stageActionText.value = `正在生成${stageNames[stage] || '当前阶段'}...`
  try {
    await runStageInternal(stage)
    message.success('生成完成')
  } catch (error: any) {
    message.error(error.message || '生成失败')
  } finally {
    stageActionLoading.value = false
    stageActionText.value = ''
  }
}

// 阶段确认
async function handleStageConfirm(action: ConfirmAction, feedback?: string) {
  const stage = activeBackendStage.value
  if (!stage || stageActionLoading.value) return
  if (action === 'approve' && !canApproveCurrentStage.value) {
    message.warning('当前阶段不在待确认状态，暂不能采用')
    return
  }

  stageActionLoading.value = true
  stageActionText.value = action === 'regenerate' ? `正在重新生成${stageNames[stage]}...`
    : action === 'edit' ? `正在根据反馈重新生成${stageNames[stage]}...`
    : '正在提交阶段操作...'
  try {
    if (action === 'approve') {
      await store.confirmStage(projectId.value, action, stage, feedback)
      message.success('已采用')
      const nextTab = getNextTabKey(activeTab.value)
      if (nextTab) {
        const nextStage = tabToStage[nextTab]
        router.push(`/projects/${projectId.value}/${nextTab}`)
        stageActionText.value = `正在生成${stageNames[nextStage]}...`
        await runStageInternal(nextStage)
      }
    } else if (action === 'edit') {
      // 编辑反馈：先 confirm(edit) 设 idle，再 runStage 带 feedback
      await store.confirmStage(projectId.value, action, stage, feedback)
      await runStageInternal(stage, feedback)
      message.success('根据反馈重新生成完成')
    } else if (action === 'regenerate') {
      await store.confirmStage(projectId.value, action, stage)
      await runStageInternal(stage)
      message.success('重新生成完成')
    }
  } catch (error: any) {
    message.error(error.message || '操作失败')
  } finally {
    stageActionLoading.value = false
    stageActionText.value = ''
  }
}

// 选题采用处理
async function handleTopicSelect(topicId: string) {
  if (stageActionLoading.value) return
  stageActionLoading.value = true
  stageActionText.value = '正在保存选题选择...'
  try {
    const nextPlans = store.topicPlans.map(t => ({ ...t, selected: t.id === topicId }))
    store.topicPlans = nextPlans
    const { updateTopic } = await import('@/api')
    await Promise.all(nextPlans.map((topic) => updateTopic(projectId.value, topic)))
  } catch (error: any) {
    message.error(error.message || '保存选题失败')
    stageActionLoading.value = false
    stageActionText.value = ''
    return
  }
  stageActionLoading.value = false
  stageActionText.value = ''
  await handleStageConfirm('approve')
}

// 选题更新
function onTopicUpdate(data: any) {
  store.topicPlans = store.topicPlans.map((t) =>
    t.id === data.id ? { ...t, ...data } : t
  )
}

// 世界观更新
function onWorldUpdate(data: any) {
  store.worldSetting = { ...store.worldSetting, ...data }
}

// 角色更新
function onCharacterUpdate(data: any) {
  store.characters = store.characters.map((c) =>
    c.id === data.id ? { ...c, ...data } : c
  )
}

// 角色删除
async function onCharacterDelete(id: string) {
  try {
    const { updateCharacters } = await import('@/api')
    const remaining = store.characters.filter((c) => c.id !== id)
    await updateCharacters(projectId.value, remaining)
    store.characters = remaining
    message.success('角色已删除')
  } catch {
    message.error('删除失败')
  }
}

// 大纲更新
function onOutlineUpdate(data: any) {
  store.outline = { ...store.outline, ...data }
}

// 章节更新
function onChapterUpdate(data: any) {
  store.currentChapter = { ...store.currentChapter, ...data }
}

// 元数据更新
async function onMetadataUpdate(data: Partial<BookMetadata>) {
  try {
    await store.updateMetadata(projectId.value, data)
    message.success('元数据已更新')
  } catch {
    message.error('更新失败')
  }
}

// 元数据重新生成
async function onMetadataRegenerate() {
  try {
    await store.regenerateMetadata(projectId.value)
    message.success('元数据已重新生成')
  } catch {
    message.error('重新生成失败')
  }
}

// 元数据确认
function onMetadataConfirm() {
  handleStageConfirm('approve')
}

// 操作日志（模拟数据，后续可接入真实日志）
const operationLogs = ref([
  { time: '10:30', action: '项目创建完成', status: 'done' as const },
])

// 组件 ref（用于触发编辑模式）
const worldPanelRef = ref<InstanceType<typeof WorldPanel> | null>(null)
const outlineEditorRef = ref<InstanceType<typeof OutlineEditor> | null>(null)
</script>

<template>
  <AppLayout>
    <div class="project-detail" v-if="store.currentProject">
      <!-- 顶部 -->
      <div class="detail-header">
        <Space align="center">
          <Button @click="router.push('/')">
            <ArrowLeftOutlined /> 返回
          </Button>
          <Title :level="3" style="margin: 0">
            {{ store.currentProject.title }}
          </Title>
          <Tag :color="store.currentProject.status === 'completed' ? 'green' : 'blue'">
            {{ store.currentProject.status }}
          </Tag>
        </Space>

        <Button
          v-if="store.currentProject.status === 'draft'"
          type="primary"
          @click="handleStartPipeline"
          :loading="globalLoading"
        >
          <PlayCircleOutlined /> 启动生成流水线
        </Button>
      </div>

      <!-- 流水线进度 -->
      <Card class="pipeline-card" size="small">
        <PipelineProgress :status="store.pipelineStatus" />
      </Card>

      <!-- 横向 Tab 导航 -->
      <Tabs :active-key="activeTab" @change="onTabChange" class="detail-tabs">
        <TabPane v-for="tab in tabItems" :key="tab.key" :tab="tab.label" />
      </Tabs>

      <!-- 主体区域：内容 + 右侧面板 -->
      <div class="detail-body">
        <!-- 内容区 -->
        <div class="detail-content">
          <Spin :spinning="globalLoading" :tip="stageActionText || '加载中...'" class="content-spin">

          <!-- 概览 -->
          <template v-if="activeTab === 'overview'">
            <Card title="项目信息" class="content-card">
              <p><strong>灵感：</strong>{{ store.currentProject.inspiration }}</p>
              <p><strong>题材：</strong>{{ store.currentProject.genre }}</p>
              <p><strong>平台：</strong>{{ store.currentProject.platforms?.join('、') || store.currentProject.platform || '未设置' }}</p>
              <p><strong>目标字数：</strong>{{ ((store.currentProject.target_words || store.currentProject.word_count_target || 0) / 10000).toFixed(0) }}万字</p>
              <p><strong>创建时间：</strong>{{ new Date(store.currentProject.created_at).toLocaleString('zh-CN') }}</p>
              <div style="text-align: center; margin-top: 24px;">
                <Button type="primary" size="large" @click="onTabChange('topic')">
                  下一步：选题方案 →
                </Button>
              </div>
            </Card>
          </template>

          <!-- 选题方案 -->
          <template v-if="activeTab === 'topic'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><BulbOutlined /> 选题方案</span>
              <Space>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('topic')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.topicPlans.length" class="empty-framework">
              <div class="empty-card-placeholder" v-for="i in 3" :key="i">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <TopicCard
              v-for="topic in store.topicPlans"
              :key="topic.id"
              :topic="topic"
              :project-id="projectId"
              @select="handleTopicSelect(topic.id)"
              @update="onTopicUpdate"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.topicPlans.length"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 世界观 -->
          <template v-if="activeTab === 'world'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><GlobalOutlined /> 世界观设定</span>
              <Space>
                <Button v-if="store.worldSetting" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button v-if="store.worldSetting && worldPanelRef?.editing" class="stage-action-button btn-cancel" @click="worldPanelRef?.cancelEdit()">
                  <CloseOutlined /> 取消
                </Button>
                <Button v-if="store.worldSetting && !worldPanelRef?.editing" class="stage-action-button btn-edit" @click="worldPanelRef?.startEdit()">
                  <EditOutlined /> 编辑
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('world')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.worldSetting" class="empty-framework">
              <div class="empty-card-placeholder">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
              <div class="empty-card-placeholder">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <WorldPanel
              v-if="store.worldSetting"
              ref="worldPanelRef"
              :world="store.worldSetting"
              :loading="globalLoading"
              :project-id="projectId"
              :show-confirm="false"
              :hide-actions="true"
              @update="onWorldUpdate"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.worldSetting"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 角色列表 -->
          <template v-if="activeTab === 'characters'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><TeamOutlined /> 角色列表</span>
              <Space>
                <Button v-if="store.characters.length" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('character')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.characters.length" class="empty-framework">
              <div class="empty-card-placeholder" v-for="i in 3" :key="i">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                  <div class="empty-avatar"></div>
                  <div class="empty-card-line title" style="flex: 1;"></div>
                </div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <CharacterCard
              v-for="char in store.characters"
              :key="char.id"
              :character="char"
              :project-id="projectId"
              @update="onCharacterUpdate"
              @delete="onCharacterDelete"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.characters.length"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 大纲编辑 -->
          <template v-if="activeTab === 'outline'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><FileTextOutlined /> 大纲编辑</span>
              <Space>
                <Button v-if="store.outline" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button v-if="store.outline && outlineEditorRef?.editing" class="stage-action-button btn-cancel" @click="outlineEditorRef?.cancelEdit()">
                  <CloseOutlined /> 取消
                </Button>
                <Button v-if="store.outline && !outlineEditorRef?.editing" class="stage-action-button btn-edit" @click="outlineEditorRef?.startEdit()">
                  <EditOutlined /> 编辑
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('outline')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.outline" class="empty-framework">
              <div class="empty-card-placeholder" v-for="i in 5" :key="i">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <OutlineEditor
              v-if="store.outline"
              ref="outlineEditorRef"
              :outline="store.outline"
              :loading="globalLoading"
              :project-id="projectId"
              :show-confirm="false"
              :hide-actions="true"
              @update="onOutlineUpdate"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.outline"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 书籍元数据 -->
          <template v-if="activeTab === 'metadata'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><ReadOutlined /> 书籍元数据</span>
              <Space>
                <Button v-if="store.metadata" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('metadata')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.metadata" class="empty-framework">
              <div class="empty-card-placeholder">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <MetadataEditor
              v-if="store.metadata"
              :project-id="projectId"
              :metadata="store.metadata"
              @update="onMetadataUpdate"
              @regenerate="onMetadataRegenerate"
              @confirm="onMetadataConfirm"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.metadata"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 正文阅读 -->
          <template v-if="activeTab === 'chapters'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><ReadOutlined /> 正文阅读</span>
              <Space>
                <Button v-if="store.currentChapter" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('draft')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.currentChapter" class="empty-framework">
              <div class="empty-card-placeholder" v-for="i in 5" :key="i">
                <div class="empty-card-line"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line short"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <ChapterReader
              v-if="store.currentChapter"
              :chapter="store.currentChapter"
              :loading="globalLoading"
              :total-chapters="store.outline?.total_chapters"
              :project-id="projectId"
              @prev="prevChapter"
              @next="nextChapter"
              @update="onChapterUpdate"
            />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.currentChapter"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          <!-- 审校报告 -->
          <template v-if="activeTab === 'review'">
            <!-- 顶部操作栏 -->
            <div class="stage-top-bar">
              <span class="stage-top-title"><CheckCircleOutlined /> 审校报告</span>
              <Space>
                <Button v-if="store.reviewReport" class="stage-action-button btn-adopt" :loading="stageActionLoading" :disabled="!canApproveCurrentStage || stageActionLoading" :title="approveButtonTitle" @click="handleStageConfirm('approve')">
                  <CheckCircleOutlined /> 采用
                </Button>
                <Button class="stage-action-button btn-generate" type="primary" :loading="stageActionLoading" @click="handleRunStage('review')">
                  <BulbOutlined /> AI生成
                </Button>
              </Space>
            </div>
            <!-- 空状态 -->
            <div v-if="!store.reviewReport" class="empty-framework">
              <div class="empty-card-placeholder">
                <div class="empty-card-line title"></div>
                <div class="empty-card-line"></div>
                <div class="empty-card-line"></div>
              </div>
            </div>
            <!-- 有数据 -->
            <ReviewReport v-if="store.reviewReport" :report="store.reviewReport" :loading="globalLoading" />
            <StageConfirm
              v-if="shouldShowStageConfirm && store.reviewReport"
              class="stage-action-card"
              :stage-name="stageConfirmName"
              :loading="stageActionLoading"
              @confirm="handleStageConfirm"
            />
          </template>

          </Spin>
        </div>

        <!-- 右侧面板 -->
        <div class="right-panel">
          <!-- 当前阶段 -->
          <Card title="当前阶段" size="small" class="panel-card">
            <div class="current-stage-info">
              <Text strong>
                {{ stageNames[store.pipelineStatus?.current_stage || ''] || '待启动' }}
              </Text>
              <Tag
                :color="store.pipelineStatus?.status === 'confirming' ? 'orange' : store.pipelineStatus?.status === 'running' ? 'blue' : 'default'"
                style="margin-left: 8px"
              >
                {{ store.pipelineStatus?.status || 'idle' }}
              </Tag>
            </div>
          </Card>

          <!-- 操作日志 -->
          <Card title="操作日志" size="small" class="panel-card" style="margin-top: 12px">
            <div class="logs-list">
              <div
                v-for="(log, index) in operationLogs"
                :key="index"
                class="log-item"
              >
                <span class="log-time">{{ log.time }}</span>
                <span class="log-action">{{ log.action }}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.project-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.pipeline-card {
  margin-bottom: 16px;
}

.detail-tabs {
  margin-bottom: 16px;
}

.detail-body {
  display: flex;
  gap: 16px;
}

.detail-content {
  flex: 1;
  min-width: 0;
}

.content-spin {
  display: block;
}

.content-spin :deep(.ant-spin-container) {
  min-height: 200px;
}

.stage-action-card {
  position: sticky;
  top: 80px;
  z-index: 5;
  margin-bottom: 4px;
}

.right-panel {
  width: 280px;
  flex-shrink: 0;
}

.panel-card {
  position: sticky;
  top: 16px;
}

.current-stage-info {
  display: flex;
  align-items: center;
}

.logs-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.log-time {
  color: #999;
  flex-shrink: 0;
}

.log-action {
  color: #333;
}

/* 顶部操作栏 */
.stage-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.24);
}

.stage-top-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 按钮样式统一 */
.stage-action-button {
  min-width: 82px;
  height: 32px;
  border-radius: 6px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.12);
}

.stage-action-button:disabled {
  color: rgba(255, 255, 255, 0.72) !important;
  border-color: rgba(255, 255, 255, 0.28) !important;
  background: rgba(255, 255, 255, 0.14) !important;
  box-shadow: none;
}

.btn-adopt {
  color: #135200 !important;
  border-color: #b7eb8f !important;
  background: #f6ffed !important;
}
.btn-adopt:hover {
  color: #237804 !important;
  border-color: #95de64 !important;
  background: #d9f7be !important;
}

.btn-edit {
  color: #0958d9 !important;
  border-color: #91caff !important;
  background: #e6f4ff !important;
}
.btn-edit:hover {
  color: #003eb3 !important;
  border-color: #69b1ff !important;
  background: #bae0ff !important;
}

.btn-cancel {
  color: #595959 !important;
  border-color: #d9d9d9 !important;
  background: #ffffff !important;
}
.btn-cancel:hover {
  color: #262626 !important;
  border-color: #bfbfbf !important;
  background: #f5f5f5 !important;
}

.btn-generate {
  color: #3f2a00 !important;
  border-color: #ffd666 !important;
  background: #ffd666 !important;
}
.btn-generate:hover {
  color: #2b1d00 !important;
  border-color: #ffc53d !important;
  background: #ffc53d !important;
}

/* 空状态框架 */
.empty-framework {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-card-placeholder {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.empty-card-line {
  height: 14px;
  background: #e8e8e8;
  border-radius: 4px;
  margin-bottom: 10px;
}

.empty-card-line.title {
  width: 40%;
  height: 18px;
  margin-bottom: 14px;
}

.empty-card-line.short {
  width: 60%;
}

.empty-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e8e8e8;
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .right-panel {
    display: none;
  }
}
</style>

