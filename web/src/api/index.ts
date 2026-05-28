import axios from 'axios'
import { message } from 'ant-design-vue'
import type {
  ApiResponse,
  Project,
  CreateProjectParams,
  PipelineStatus,
  TopicPlan,
  WorldSetting,
  Character,
  Outline,
  Chapter,
  ReviewReport,
  ConfirmAction,
  BookMetadata,
} from '@/types'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 可在此添加 token 等认证信息
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const msg = error.response?.data?.message || error.message || '请求失败'
    message.error(msg)
    return Promise.reject(error)
  }
)

// ========== 项目 API ==========

/** 创建项目 */
export function createProject(params: CreateProjectParams) {
  return http.post<ApiResponse<Project>>('/projects', params)
}

/** 项目列表 */
export function listProjects() {
  return http.get<ApiResponse<Project[]>>('/projects')
}

/** 项目详情 */
export function getProject(id: string) {
  return http.get<ApiResponse<Project>>(`/projects/${id}`)
}

// ========== 流水线 API ==========

/** 启动流水线 */
export function startPipeline(id: string) {
  return http.post<ApiResponse<PipelineStatus>>(`/projects/${id}/pipeline/start`)
}

/** 获取流水线状态 */
export function getPipelineStatus(id: string) {
  return http.get<ApiResponse<PipelineStatus>>(`/projects/${id}/pipeline/status`)
}

/** 确认阶段 */
export function confirmStage(id: string, action: ConfirmAction) {
  return http.post<ApiResponse<void>>(`/projects/${id}/pipeline/confirm`, { action })
}

// ========== 内容 API ==========

/** 获取选题方案 */
export function getTopic(id: string) {
  return http.get<ApiResponse<TopicPlan[]>>(`/projects/${id}/topic`)
}

/** 获取世界观 */
export function getWorld(id: string) {
  return http.get<ApiResponse<WorldSetting>>(`/projects/${id}/world`)
}

/** 获取角色列表 */
export function getCharacters(id: string) {
  return http.get<ApiResponse<Character[]>>(`/projects/${id}/characters`)
}

/** 获取大纲 */
export function getOutline(id: string) {
  return http.get<ApiResponse<Outline>>(`/projects/${id}/outline`)
}

/** 获取章节 */
export function getChapter(id: string, num: number) {
  return http.get<ApiResponse<Chapter>>(`/projects/${id}/chapters/${num}`)
}

/** 获取审校报告 */
export function getReview(id: string) {
  return http.get<ApiResponse<ReviewReport>>(`/projects/${id}/review`)
}

// ========== 元数据 API ==========

/** 获取书籍元数据 */
export function getMetadata(projectId: string) {
  return http.get<ApiResponse<BookMetadata>>(`/projects/${projectId}/metadata`)
}

/** 更新书籍元数据 */
export function updateMetadata(projectId: string, metadata: Partial<BookMetadata>) {
  return http.put<ApiResponse<void>>(`/projects/${projectId}/metadata`, metadata)
}

/** 重新生成书籍元数据 */
export function regenerateMetadata(projectId: string) {
  return http.post<ApiResponse<BookMetadata>>(`/projects/${projectId}/metadata/regenerate`)
}

// ========== 二次编辑 API ==========

/** 更新选题 */
export function updateTopic(projectId: string, data: any) {
  return http.put<ApiResponse<any>>(`/projects/${projectId}/topic`, data)
}

/** 更新世界观 */
export function updateWorld(projectId: string, data: any) {
  return http.put<ApiResponse<any>>(`/projects/${projectId}/world`, data)
}

/** 更新角色 */
export function updateCharacters(projectId: string, data: any) {
  return http.put<ApiResponse<any>>(`/projects/${projectId}/characters`, data)
}

/** 更新大纲 */
export function updateOutline(projectId: string, data: any) {
  return http.put<ApiResponse<any>>(`/projects/${projectId}/outline`, data)
}

/** 更新章节正文 */
export function updateChapterDraft(projectId: string, chapterNum: number, draft: string) {
  return http.put<ApiResponse<any>>(`/projects/${projectId}/chapters/${chapterNum}`, { content: draft })
}

/** 确认阶段 */
export function confirmStageAction(projectId: string, stage: string) {
  return http.post<ApiResponse<void>>(`/projects/${projectId}/pipeline/stages/${stage}/confirm`)
}

/** 获取阶段状态 */
export function getStages(projectId: string) {
  return http.get<ApiResponse<any>>(`/projects/${projectId}/pipeline/stages`)
}

export default http
