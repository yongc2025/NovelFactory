import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api'
import type {
  Project,
  PipelineStatus,
  TopicPlan,
  WorldSetting,
  Character,
  Outline,
  Chapter,
  ReviewReport,
  CreateProjectParams,
  ConfirmAction,
  BookMetadata,
} from '@/types'

export const useProjectStore = defineStore('project', () => {
  // ========== 状态 ==========
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const pipelineStatus = ref<PipelineStatus | null>(null)
  const topicPlans = ref<TopicPlan[]>([])
  const worldSetting = ref<WorldSetting | null>(null)
  const characters = ref<Character[]>([])
  const outline = ref<Outline | null>(null)
  const currentChapter = ref<Chapter | null>(null)
  const reviewReport = ref<ReviewReport | null>(null)
  const metadata = ref<BookMetadata | null>(null)

  const loading = ref(false)
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========
  const sortedProjects = computed(() =>
    [...projects.value].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  )

  const currentStage = computed(() => pipelineStatus.value?.current_stage ?? null)

  const stageProgress = computed(() => {
    if (!pipelineStatus.value) return 0
    const stages = pipelineStatus.value.stages
    const completed = stages.filter((s) => s.status === 'completed').length
    return Math.round((completed / stages.length) * 100)
  })

  // ========== 操作 ==========

  async function fetchProjects() {
    loading.value = true
    try {
      const res = await api.listProjects()
      projects.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string) {
    loading.value = true
    try {
      const res = await api.getProject(id)
      currentProject.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createProject(params: CreateProjectParams) {
    loading.value = true
    try {
      const res = await api.createProject(params)
      projects.value.unshift(res.data.data)
      return res.data.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchPipelineStatus(id: string) {
    try {
      const res = await api.getPipelineStatus(id)
      pipelineStatus.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function startPipeline(id: string) {
    loading.value = true
    try {
      const res = await api.startPipeline(id)
      pipelineStatus.value = res.data.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function confirmStage(id: string, action: ConfirmAction) {
    loading.value = true
    try {
      await api.confirmStage(id, action)
      await fetchPipelineStatus(id)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTopic(id: string) {
    loading.value = true
    try {
      const res = await api.getTopic(id)
      topicPlans.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchWorld(id: string) {
    loading.value = true
    try {
      const res = await api.getWorld(id)
      worldSetting.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchCharacters(id: string) {
    loading.value = true
    try {
      const res = await api.getCharacters(id)
      characters.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchOutline(id: string) {
    loading.value = true
    try {
      const res = await api.getOutline(id)
      outline.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchChapter(id: string, num: number) {
    loading.value = true
    try {
      const res = await api.getChapter(id, num)
      currentChapter.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchReview(id: string) {
    loading.value = true
    try {
      const res = await api.getReview(id)
      reviewReport.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchMetadata(projectId: string) {
    loading.value = true
    try {
      const res = await api.getMetadata(projectId)
      metadata.value = res.data.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function updateMetadata(projectId: string, data: Partial<BookMetadata>) {
    loading.value = true
    try {
      await api.updateMetadata(projectId, data)
      if (metadata.value) {
        metadata.value = { ...metadata.value, ...data }
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function regenerateMetadata(projectId: string) {
    loading.value = true
    try {
      const res = await api.regenerateMetadata(projectId)
      metadata.value = res.data.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTopicData(projectId: string, data: any) {
    loading.value = true
    try {
      await api.updateTopic(projectId, data)
      topicPlans.value = data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateWorldData(projectId: string, data: any) {
    loading.value = true
    try {
      await api.updateWorld(projectId, data)
      worldSetting.value = data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateCharactersData(projectId: string, data: any) {
    loading.value = true
    try {
      await api.updateCharacters(projectId, data)
      characters.value = data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateOutlineData(projectId: string, data: any) {
    loading.value = true
    try {
      await api.updateOutline(projectId, data)
      outline.value = data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateChapterDraft(projectId: string, chapterNum: number, draft: string) {
    loading.value = true
    try {
      await api.updateChapterDraft(projectId, chapterNum, draft)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function confirmStageAction(projectId: string, stage: string) {
    loading.value = true
    try {
      await api.confirmStageAction(projectId, stage)
      await fetchPipelineStatus(projectId)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentProject.value = null
    pipelineStatus.value = null
    topicPlans.value = []
    worldSetting.value = null
    characters.value = []
    outline.value = null
    currentChapter.value = null
    reviewReport.value = null
    metadata.value = null
  }

  return {
    // 状态
    projects,
    currentProject,
    pipelineStatus,
    topicPlans,
    worldSetting,
    characters,
    outline,
    currentChapter,
    reviewReport,
    metadata,
    loading,
    error,
    // 计算属性
    sortedProjects,
    currentStage,
    stageProgress,
    // 操作
    fetchProjects,
    fetchProject,
    createProject,
    fetchPipelineStatus,
    startPipeline,
    confirmStage,
    fetchTopic,
    fetchWorld,
    fetchCharacters,
    fetchOutline,
    fetchChapter,
    fetchReview,
    fetchMetadata,
    updateMetadata,
    regenerateMetadata,
    updateTopicData,
    updateWorldData,
    updateCharactersData,
    updateOutlineData,
    updateChapterDraft,
    confirmStageAction,
    clearCurrent,
  }
})
