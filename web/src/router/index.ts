import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘' },
  },
  {
    path: '/projects/create',
    name: 'ProjectCreate',
    component: () => import('@/views/ProjectCreate.vue'),
    meta: { title: '新建项目' },
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '项目详情' },
  },
  {
    path: '/projects/:id/topic',
    name: 'ProjectTopic',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '选题详情', tab: 'topic' },
  },
  {
    path: '/projects/:id/world',
    name: 'ProjectWorld',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '世界观', tab: 'world' },
  },
  {
    path: '/projects/:id/characters',
    name: 'ProjectCharacters',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '角色列表', tab: 'characters' },
  },
  {
    path: '/projects/:id/outline',
    name: 'ProjectOutline',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '大纲编辑', tab: 'outline' },
  },
  {
    path: '/projects/:id/scene',
    name: 'ProjectScene',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '场景细纲', tab: 'scene' },
  },
  {
    path: '/projects/:id/metadata',
    name: 'ProjectMetadata',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '书籍元数据', tab: 'metadata' },
  },
  {
    path: '/projects/:id/chapters',
    name: 'ProjectChapters',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '正文', tab: 'chapters' },
  },
  {
    path: '/projects/:id/chapters/:num',
    name: 'ChapterReader',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '章节阅读', tab: 'chapters' },
  },
  {
    path: '/projects/:id/review',
    name: 'ProjectReview',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '审校报告', tab: 'review' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - NovelFactory`
  }
  next()
})

export default router
