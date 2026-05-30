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
  platforms?: string[]
  word_count_target: number
  target_words?: number
  current_stage: PipelineStage
  created_at: string
  updated_at: string
  book_title?: string
  book_synopsis?: string
  book_tags?: string[]
  book_category?: string
  [key: string]: any
}

/** 创建项目参数 — 对应后端 ProjectCreate */
export interface CreateProjectParams {
  // Level 1: 必填
  premise: string
  platforms: string[]
  length_type: 'short' | 'medium' | 'long' | 'comic'
  // Level 2: 选填
  genre_major?: string
  genre_minor?: string
  target_audience?: string
  tone?: string
  // Level 3: 选填
  protagonist_name?: string
  protagonist_desc?: string
  antagonist_name?: string
  antagonist_desc?: string
  has_romance?: string
  romance_desc?: string
  supporting_count?: number
  // Level 4: 选填
  world_setting?: string
  world_custom?: string
  reference_works?: string
  forbidden_elements?: string[]
  // Level 5: 选填
  target_words?: number
  target_chapters?: number
  chapter_word_range?: number[]
  climax_density?: string
  climax_interval?: number
  foreshadow_count?: number
  model_provider?: string
  style_sample?: string
  // 书籍元数据（可选）
  book_title?: string
  book_synopsis?: string
  book_tags?: string[]
  book_category?: string
  // 生成策略
  generation_strategy?: GenerationStrategy
}

/** 选题方案 */
export interface TopicPlan {
  id: string
  project_id: string
  title: string           // 书名
  logline: string         // 一句话梗概
  theme: string           // 主题/立意
  genre: string           // 题材类型
  target_audience: string // 目标读者
  conflict: string        // 核心冲突
  hook: string            // 卖点/钩子
  platforms: string[]     // 推荐平台
  word_count: string      // 建议篇幅
  score: number           // AI评分 (1-100)
  reasoning: string       // 评分理由
  selected: boolean       // 是否被选中
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

/** 书籍元数据 */
export interface BookMetadata {
  title: string
  title_candidates: string[]
  synopsis_short: string
  synopsis_medium: string
  synopsis_long: string
  tags: string[]
  category: string
  category_path: string
}
