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
  PipelineTask,
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
  const activeTask = ref<PipelineTask | null>(null)

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
      projects.value = res.data.data ?? res.data
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
      currentProject.value = res.data.data ?? res.data
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
      const project = res.data.data ?? res.data
      projects.value.unshift(project)
      return project
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
      pipelineStatus.value = (res.data.data ?? res.data)
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function deleteProject(id: string) {
    try {
      await api.deleteProject(id)
      projects.value = projects.value.filter((p) => p.id !== id)
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function startPipeline(id: string) {
    loading.value = true
    try {
      const res = await api.startPipeline(id)
      pipelineStatus.value = (res.data.data ?? res.data)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function unwrapTask(data: PipelineTask | { data?: PipelineTask }): PipelineTask {
    return 'data' in data && data.data ? data.data : data as PipelineTask
  }

  async function runStage(id: string, stage: string, feedback?: string) {
    loading.value = true
    try {
      const res = await api.runStage(id, stage, feedback)
      const task = unwrapTask(res.data)
      activeTask.value = task
      await fetchPipelineStatus(id)
      return task
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function confirmStage(id: string, action: ConfirmAction, stage?: string, feedback?: string) {
    loading.value = true
    try {
      const res = await api.confirmStage(id, action, stage, feedback)
      await fetchPipelineStatus(id)
      return res
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
      const data: any = res.data.data ?? res.data
      const plans = Array.isArray(data?.topic) ? data.topic : Array.isArray(data) ? data : []
      // 兼容旧数据：补全缺失字段
      topicPlans.value = plans.map((t: any) => ({
        id: t.id || '',
        project_id: t.project_id || id,
        title: t.title || '',
        logline: t.logline || t.premise || '',
        theme: t.theme || '',
        genre: t.genre || '',
        target_audience: t.target_audience || t.target_readers || '',
        conflict: t.conflict || '',
        hook: t.hook || '',
        platforms: Array.isArray(t.platforms) ? t.platforms : typeof t.platforms === 'string' ? [t.platforms] : [],
        word_count: t.word_count || '',
        score: typeof t.score === 'number' ? t.score : 0,
        reasoning: t.reasoning || '',
        selected: !!t.selected,
      }))
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
      const data = (res.data.data ?? res.data) as WorldSetting | { world?: WorldSetting } | null
      // API 返回 { project_id, world: {...} }，提取 world 字段
      const world = data && Object.prototype.hasOwnProperty.call(data, 'world')
        ? (data as { world?: WorldSetting }).world
        : data as WorldSetting | null
      worldSetting.value = (world && Object.keys(world).length > 0) ? world : null
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
      const data: any = res.data.data ?? res.data
      characters.value = Array.isArray(data?.characters) ? data.characters : Array.isArray(data) ? data : []
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
      const data = (res.data.data ?? res.data) as Outline | { outline?: Outline } | null
      // API 返回 { project_id, outline: {...} }，提取 outline 字段
      const outlineData = data && Object.prototype.hasOwnProperty.call(data, 'outline')
        ? (data as { outline?: Outline }).outline
        : data as Outline | null
      outline.value = (outlineData && Object.keys(outlineData).length > 0) ? outlineData : null
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function generateOutlineBatch(projectId: string, batchSize: number) {
    loading.value = true
    try {
      const res = await api.generateOutlineBatch(projectId, batchSize)
      const task = unwrapTask(res.data)
      activeTask.value = task
      return task
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchChapter(id: string, num: number) {
    loading.value = true
    try {
      const res = await api.getChapter(id, num)
      const data = res.data.data ?? res.data
      currentChapter.value = (data && Object.keys(data).length > 0 && ((data as any).scenes || (data as any).draft)) ? data : null
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
      const data = (res.data.data ?? res.data) as ReviewReport | { review?: ReviewReport } | null
      // API 返回 { project_id, review: {...} }，提取 review 字段
      const reviewData = data && Object.prototype.hasOwnProperty.call(data, 'review')
        ? (data as { review?: ReviewReport }).review
        : data as ReviewReport | null
      reviewReport.value = (reviewData && Object.keys(reviewData).length > 0) ? reviewData : null
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
      const data = res.data.data ?? res.data
      // API 返回 BookMetadata 直接作为响应
      metadata.value = (data && Object.keys(data).length > 0) ? data : null
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
      metadata.value = (res.data.data ?? res.data)
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

  async function fetchActiveTask(projectId: string) {
    try {
      const res = await api.getActiveTask(projectId)
      const task = unwrapTask(res.data)
      activeTask.value = task.task_id ? task : null
      return activeTask.value
    } catch (e: any) {
      error.value = e.message
      return null
    }
  }

  function setActiveTask(task: PipelineTask | null) {
    activeTask.value = task
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
    activeTask.value = null
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
    activeTask,
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
    runStage,
    confirmStage,
    fetchTopic,
    fetchWorld,
    fetchCharacters,
    fetchOutline,
    generateOutlineBatch,
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
    fetchActiveTask,
    setActiveTask,
    deleteProject,
    clearCurrent,
  }
})
