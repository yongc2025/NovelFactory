// ========== 项目相关 ==========

/** 项目状态 */
export type ProjectStatus =
  | 'draft'
  | 'generating'
  | 'reviewing'
  | 'completed'
  | 'failed'

/** 流水线阶段 */
export type PipelineStage =
  | 'topic'
  | 'world'
  | 'characters'
  | 'outline'
  | 'chapters'
  | 'review'

/** 阶段确认动作 */
export type ConfirmAction = 'approve' | 'edit' | 'regenerate'

/** 项目 */
export interface Project {
  id: string
  title: string
  genre: string
  sub_genre?: string
  status: ProjectStatus
  inspiration: string
  platform: string
  word_count_target: number
  current_stage: PipelineStage
  created_at: string
  updated_at: string
}

/** 创建项目参数 */
export interface CreateProjectParams {
  inspiration: string
  platform: string
  word_count_target: number
  genre: string
  sub_genre?: string
  character_presets?: CharacterPreset[]
  world_constraints?: string
  generation_strategy?: GenerationStrategy
}

/** 选题方案 */
export interface TopicPlan {
  id: string
  project_id: string
  title: string
  logline: string
  theme: string
  target_audience: string
  conflict: string
  hook: string
  score: number
  selected: boolean
}

/** 世界观设定 */
export interface WorldSetting {
  id: string
  project_id: string
  era: string
  geography: string
  power_system: string
  social_structure: string
  key_locations: string[]
  rules: string[]
  constraints: string[]
  created_at: string
}

/** 角色预设（创建时） */
export interface CharacterPreset {
  name: string
  role: 'protagonist' | 'antagonist' | 'supporting'
  traits?: string[]
  background?: string
}

/** 角色 */
export interface Character {
  id: string
  project_id: string
  name: string
  role: 'protagonist' | 'antagonist' | 'supporting'
  traits: string[]
  background: string
  personality: string
  appearance: string
  relationships: CharacterRelationship[]
  arc: string
  created_at: string
}

/** 角色关系 */
export interface CharacterRelationship {
  target_id: string
  target_name: string
  relation: string
  description: string
}

/** 大纲 */
export interface Outline {
  id: string
  project_id: string
  total_chapters: number
  chapters: OutlineChapter[]
  created_at: string
}

/** 大纲章节 */
export interface OutlineChapter {
  chapter_number: number
  title: string
  summary: string
  key_events: string[]
  pov_character?: string
  word_count_target: number
}

/** 章节 */
export interface Chapter {
  id: string
  project_id: string
  chapter_number: number
  title: string
  content: string
  word_count: number
  status: 'draft' | 'reviewed' | 'final'
  created_at: string
  updated_at: string
}

/** 审校报告 */
export interface ReviewReport {
  id: string
  project_id: string
  overall_score: number
  consistency_score: number
  plot_score: number
  character_score: number
  writing_score: number
  issues: ReviewIssue[]
  summary: string
  suggestions: string[]
  created_at: string
}

/** 审校问题 */
export interface ReviewIssue {
  chapter_number: number
  severity: 'critical' | 'warning' | 'info'
  category: string
  description: string
  suggestion: string
}

/** 生成策略 */
export interface GenerationStrategy {
  model: string
  temperature: number
  style: string
  pacing: 'fast' | 'medium' | 'slow'
  tone: string
}

/** 流水线状态 */
export interface PipelineStatus {
  project_id: string
  current_stage: PipelineStage
  stages: StageStatus[]
  started_at: string
  updated_at: string
}

/** 阶段状态 */
export interface StageStatus {
  stage: PipelineStage
  status: 'pending' | 'running' | 'completed' | 'failed' | 'waiting_confirm'
  progress: number
  started_at?: string
  completed_at?: string
  error?: string
}

/** API 响应 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
