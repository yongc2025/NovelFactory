<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Card,
  Menu,
  Button,
  Tag,
  Spin,
  Space,
  Typography,
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
} from '@ant-design/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import PipelineProgress from '@/components/project/PipelineProgress.vue'
import TopicCard from '@/components/project/TopicCard.vue'
import WorldPanel from '@/components/project/WorldPanel.vue'
import CharacterCard from '@/components/project/CharacterCard.vue'
import OutlineEditor from '@/components/project/OutlineEditor.vue'
import ChapterReader from '@/components/project/ChapterReader.vue'
import ReviewReport from '@/components/project/ReviewReport.vue'
import StageConfirm from '@/components/common/StageConfirm.vue'
import { useProjectStore } from '@/stores/project'
import type { ConfirmAction } from '@/types'

const { Title, Text } = Typography

const route = useRoute()
const router = useRouter()
const store = useProjectStore()

const projectId = computed(() => route.params.id as string)
const activeTab = computed(() => (route.meta.tab as string) || 'overview')
const currentChapterNum = computed(() => {
  const num = route.params.num
  return num ? parseInt(num as string) : 1
})

// 阶段名称映射
const stageNames: Record<string, string> = {
  topic: '选题方案',
  world: '世界观',
  characters: '角色设定',
  outline: '大纲',
  chapters: '正文',
  review: '审校报告',
}

// 侧边导航
const sideMenuItems = [
  { key: 'overview', icon: () => h(BulbOutlined), label: '项目概览' },
  { key: 'topic', icon: () => h(BulbOutlined), label: '选题方案' },
  { key: 'world', icon: () => h(GlobalOutlined), label: '世界观' },
  { key: 'characters', icon: () => h(TeamOutlined), label: '角色列表' },
  { key: 'outline', icon: () => h(FileTextOutlined), label: '大纲编辑' },
  { key: 'chapters', icon: () => h(ReadOutlined), label: '正文阅读' },
  { key: 'review', icon: () => h(CheckCircleOutlined), label: '审校报告' },
]

const selectedKeys = computed(() => [activeTab.value])

function onMenuClick({ key }: { key: string }) {
  if (key === 'overview') {
    router.push(`/projects/${projectId.value}`)
  } else {
    router.push(`/projects/${projectId.value}/${key}`)
  }
}

// 加载数据
onMounted(async () => {
  await store.fetchProject(projectId.value)
  await store.fetchPipelineStatus(projectId.value)
})

// 根据 tab 加载对应数据
watch(activeTab, async (tab) => {
  const id = projectId.value
  switch (tab) {
    case 'topic':
      await store.fetchTopic(id)
      break
    case 'world':
      await store.fetchWorld(id)
      break
    case 'characters':
      await store.fetchCharacters(id)
      break
    case 'outline':
      await store.fetchOutline(id)
      break
    case 'chapters':
      await store.fetchChapter(id, currentChapterNum.value)
      break
    case 'review':
      await store.fetchReview(id)
      break
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
  try {
    await store.startPipeline(projectId.value)
    message.success('流水线已启动！')
  } catch {
    message.error('启动失败')
  }
}

// 阶段确认
async function handleStageConfirm(action: ConfirmAction, feedback?: string) {
  try {
    await store.confirmStage(projectId.value, action)
    message.success(
      action === 'approve' ? '已采用' : action === 'edit' ? '已提交反馈' : '正在重新生成'
    )
  } catch {
    message.error('操作失败')
  }
}
</script>

<template>
  <AppLayout>
    <Spin :spinning="store.loading && !store.currentProject">
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
            :loading="store.loading"
          >
            <PlayCircleOutlined /> 启动生成流水线
          </Button>
        </div>

        <!-- 流水线进度 -->
        <Card class="pipeline-card" size="small">
          <PipelineProgress :status="store.pipelineStatus" />
        </Card>

        <!-- 主体区域 -->
        <div class="detail-body">
          <!-- 侧边导航 -->
          <Card class="side-nav" size="small">
            <Menu
              :selected-keys="selectedKeys"
              :items="sideMenuItems"
              @click="onMenuClick"
              mode="inline"
            />
          </Card>

          <!-- 内容区 -->
          <div class="detail-content">
            <!-- 概览 -->
            <template v-if="activeTab === 'overview'">
              <Card title="项目信息">
                <p><strong>灵感：</strong>{{ store.currentProject.inspiration }}</p>
                <p><strong>题材：</strong>{{ store.currentProject.genre }}</p>
                <p><strong>平台：</strong>{{ store.currentProject.platform }}</p>
                <p><strong>目标字数：</strong>{{ (store.currentProject.word_count_target / 10000).toFixed(0) }}万字</p>
                <p><strong>创建时间：</strong>{{ new Date(store.currentProject.created_at).toLocaleString('zh-CN') }}</p>
              </Card>

              <StageConfirm
                v-if="store.pipelineStatus?.stages.some(s => s.status === 'waiting_confirm')"
                :stage-name="stageNames[store.pipelineStatus?.current_stage || ''] || ''"
                :loading="store.loading"
                @confirm="handleStageConfirm"
                style="margin-top: 16px"
              />
            </template>

            <!-- 选题 -->
            <template v-if="activeTab === 'topic'">
              <Title :level="4">💡 选题方案</Title>
              <TopicCard
                v-for="topic in store.topicPlans"
                :key="topic.id"
                :topic="topic"
                @select="handleStageConfirm('approve')"
              />
              <StageConfirm
                v-if="store.topicPlans.length > 0"
                stage-name="选题方案"
                :loading="store.loading"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 世界观 -->
            <template v-if="activeTab === 'world'">
              <Title :level="4">🌍 世界观设定</Title>
              <WorldPanel :world="store.worldSetting" :loading="store.loading" />
              <StageConfirm
                v-if="store.worldSetting"
                stage-name="世界观"
                :loading="store.loading"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 角色 -->
            <template v-if="activeTab === 'characters'">
              <Title :level="4">👥 角色列表</Title>
              <CharacterCard
                v-for="char in store.characters"
                :key="char.id"
                :character="char"
              />
              <StageConfirm
                v-if="store.characters.length > 0"
                stage-name="角色设定"
                :loading="store.loading"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 大纲 -->
            <template v-if="activeTab === 'outline'">
              <Title :level="4">📋 大纲编辑</Title>
              <OutlineEditor :outline="store.outline" :loading="store.loading" />
              <StageConfirm
                v-if="store.outline"
                stage-name="大纲"
                :loading="store.loading"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 正文 -->
            <template v-if="activeTab === 'chapters'">
              <Title :level="4">📖 正文阅读</Title>
              <ChapterReader
                :chapter="store.currentChapter"
                :loading="store.loading"
                :total-chapters="store.outline?.total_chapters"
                @prev="prevChapter"
                @next="nextChapter"
              />
            </template>

            <!-- 审校 -->
            <template v-if="activeTab === 'review'">
              <Title :level="4">📊 审校报告</Title>
              <ReviewReport :report="store.reviewReport" :loading="store.loading" />
            </template>
          </div>
        </div>
      </div>
    </Spin>
  </AppLayout>
</template>

<style scoped>
.project-detail {
  max-width: 1200px;
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

.detail-body {
  display: flex;
  gap: 16px;
}

.side-nav {
  width: 200px;
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .detail-body {
    flex-direction: column;
  }

  .side-nav {
    width: 100%;
  }
}
</style>
