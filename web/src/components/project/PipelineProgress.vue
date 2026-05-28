<script setup lang="ts">
import { computed } from 'vue'
import { Steps, Tag } from 'ant-design-vue'
import {
  BulbOutlined,
  GlobalOutlined,
  TeamOutlined,
  FileTextOutlined,
  ReadOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons-vue'
import type { PipelineStatus, PipelineStage } from '@/types'

const props = defineProps<{
  status: PipelineStatus | null
}>()

const stageLabels: Record<PipelineStage, string> = {
  topic: '选题',
  world: '世界观',
  characters: '角色',
  outline: '大纲',
  chapters: '正文',
  review: '审校',
}

const stageIcons: Record<PipelineStage, () => any> = {
  topic: () => h(BulbOutlined),
  world: () => h(GlobalOutlined),
  characters: () => h(TeamOutlined),
  outline: () => h(FileTextOutlined),
  chapters: () => h(ReadOutlined),
  review: () => h(CheckCircleOutlined),
}

const stageOrder: PipelineStage[] = ['topic', 'world', 'characters', 'outline', 'chapters', 'review']

const stepsItems = computed(() => {
  if (!props.status) return []

  return stageOrder.map((stage) => {
    const stageStatus = props.status!.stages.find((s) => s.stage === stage)
    let status: 'wait' | 'process' | 'finish' | 'error' = 'wait'

    if (stageStatus) {
      switch (stageStatus.status) {
        case 'completed':
          status = 'finish'
          break
        case 'running':
        case 'waiting_confirm':
          status = 'process'
          break
        case 'failed':
          status = 'error'
          break
        default:
          status = 'wait'
      }
    }

    return {
      title: stageLabels[stage],
      status,
      icon: stageIcons[stage],
    }
  })
})

const currentStep = computed(() => {
  if (!props.status) return 0
  return stageOrder.indexOf(props.status.current_stage)
})
</script>

<template>
  <div class="pipeline-progress">
    <Steps
      :current="currentStep"
      :items="stepsItems"
      size="small"
    />
    <div v-if="status" class="progress-meta">
      <Tag :color="status.current_stage === 'review' ? 'green' : 'blue'">
        当前阶段：{{ stageLabels[status.current_stage] }}
      </Tag>
    </div>
  </div>
</template>

<style scoped>
.pipeline-progress {
  padding: 16px 0;
}

.progress-meta {
  margin-top: 12px;
  text-align: right;
}
</style>
