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

  function clearCurrent() {
    currentProject.value = null
    pipelineStatus.value = null
    topicPlans.value = []
    worldSetting.value = null
    characters.value = []
    outline.value = null
    currentChapter.value = null
    reviewReport.value = null
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
    clearCurrent,
  }
})
