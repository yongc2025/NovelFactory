/** 任务轮询器：统一管理异步任务提交、轮询和取消 */

import { computed, onBeforeUnmount, ref } from 'vue'
import { cancelTask, getTask } from '@/api'
import type { PipelineTask } from '@/types'

type ApiResult = { data: PipelineTask | { data?: PipelineTask } } | PipelineTask
type ApiCall = () => Promise<ApiResult>

const RUNNING_STATUS = new Set(['pending', 'running'])
const FINAL_STATUS = new Set(['success', 'failed', 'cancelled'])

function unwrapTask(payload: PipelineTask | { data?: PipelineTask }): PipelineTask {
  return 'data' in payload && payload.data ? payload.data : payload as PipelineTask
}

function unwrapResult(result: ApiResult): PipelineTask {
  return 'data' in result ? unwrapTask(result.data) : result
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function useTaskPoller() {
  const activeTask = ref<PipelineTask | null>(null)
  const elapsed = ref(0)
  const isPolling = ref(false)
  const lastResult = ref<PipelineTask | null>(null)

  let elapsedTimer: ReturnType<typeof setInterval> | null = null
  let pollToken = 0

  const progress = computed(() => activeTask.value?.progress?.percent ?? 0)
  const statusText = computed(() => {
    const task = activeTask.value
    if (!task) return '空闲'
    if (task.status === 'pending') return '等待执行'
    if (task.status === 'running') return task.progress?.label || '正在生成'
    if (task.status === 'success') return '已完成'
    if (task.status === 'failed') return task.error || '任务失败'
    if (task.status === 'cancelled') return '已取消'
    return '空闲'
  })
  const isActive = computed(() => RUNNING_STATUS.has(activeTask.value?.status || ''))

  function startElapsed() {
    stopElapsed()
    elapsed.value = 0
    elapsedTimer = setInterval(() => { elapsed.value += 1 }, 1000)
  }

  function stopElapsed() {
    if (elapsedTimer) {
      clearInterval(elapsedTimer)
      elapsedTimer = null
    }
  }

  function formatElapsed(seconds = elapsed.value): string {
    if (seconds < 60) return `${seconds} 秒`
    return `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`
  }

  async function submitTask(apiCall: ApiCall): Promise<PipelineTask> {
    if (isActive.value && activeTask.value) return activeTask.value
    const token = ++pollToken
    const response = await apiCall()
    const submittedTask = unwrapResult(response)
    activeTask.value = submittedTask
    lastResult.value = submittedTask
    startElapsed()
    return pollTask(submittedTask.task_id, token)
  }

  async function pollTask(taskId: string | null, token = pollToken): Promise<PipelineTask> {
    if (!taskId) throw new Error('任务 ID 为空')
    isPolling.value = true
    await sleep(10000)
    try {
      while (token === pollToken) {
        const response = await getTask(taskId)
        const task = unwrapTask(response.data)
        activeTask.value = task
        lastResult.value = task
        if (FINAL_STATUS.has(task.status)) return task
        await sleep(elapsed.value > 60 ? 5000 : 3000)
      }
      throw new Error('任务轮询已被替换')
    } finally {
      isPolling.value = false
      if (!isActive.value) stopElapsed()
    }
  }

  async function cancelActiveTask(): Promise<void> {
    const taskId = activeTask.value?.task_id
    if (!taskId) return
    await cancelTask(taskId)
    const response = await getTask(taskId)
    activeTask.value = unwrapTask(response.data)
  }

  function resetTask() {
    pollToken += 1
    activeTask.value = null
    lastResult.value = null
    isPolling.value = false
    stopElapsed()
  }

  onBeforeUnmount(resetTask)

  return {
    activeTask,
    elapsed,
    isActive,
    isPolling,
    lastResult,
    progress,
    statusText,
    submitTask,
    pollTask,
    cancelTask: cancelActiveTask,
    formatElapsed,
    resetTask,
  }
}
