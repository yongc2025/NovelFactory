<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Table, Tag, Space, Typography } from 'ant-design-vue'
import { PlusOutlined, EyeOutlined, PlayCircleOutlined } from '@ant-design/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useProjectStore } from '@/stores/project'
import type { Project } from '@/types'

const { Title, Text } = Typography
const router = useRouter()
const store = useProjectStore()

onMounted(() => {
  store.fetchProjects()
})

const statusColors: Record<string, string> = {
  draft: 'default',
  generating: 'processing',
  reviewing: 'warning',
  completed: 'success',
  failed: 'error',
}

const statusLabels: Record<string, string> = {
  draft: '草稿',
  generating: '生成中',
  reviewing: '审校中',
  completed: '已完成',
  failed: '失败',
}

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80, ellipsis: true },
  { title: '标题', dataIndex: 'title', ellipsis: true },
  { title: '题材', dataIndex: 'genre', width: 120 },
  {
    title: '状态',
    dataIndex: 'status',
    width: 100,
    customRender: ({ text }: { text: string }) =>
      h(Tag, { color: statusColors[text] }, () => statusLabels[text] || text),
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    width: 180,
    customRender: ({ text }: { text: string }) => new Date(text).toLocaleString('zh-CN'),
  },
  {
    title: '操作',
    key: 'action',
    width: 160,
    customRender: ({ record }: { record: Project }) =>
      h(Space, null, () => [
        h(
          Button,
          { type: 'link', size: 'small', onClick: () => router.push(`/projects/${record.id}`) },
          () => [h(EyeOutlined), ' 查看']
        ),
        record.status === 'draft'
          ? h(
              Button,
              { type: 'link', size: 'small', onClick: () => router.push(`/projects/${record.id}`) },
              () => [h(PlayCircleOutlined), ' 启动']
            )
          : null,
      ]),
  },
]

function goToCreate() {
  router.push('/projects/create')
}
</script>

<template>
  <AppLayout>
    <div class="dashboard">
      <div class="dashboard-header">
        <div>
          <Title :level="3" style="margin: 0">👋 欢迎来到 NovelFactory</Title>
          <Text type="secondary">AI 驱动的小说创作工坊</Text>
        </div>
        <Button type="primary" size="large" @click="goToCreate">
          <PlusOutlined /> 新建项目
        </Button>
      </div>

      <div class="dashboard-body">
        <Table
          :columns="columns"
          :data-source="store.sortedProjects"
          :loading="store.loading"
          :pagination="{ pageSize: 10 }"
          :row-key="(record: Project) => record.id"
          @row="(record: Project) => ({ onClick: () => router.push(`/projects/${record.id}`) })"
          class="project-table"
        />
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-body {
  background: var(--color-bg-elevated);
  border-radius: 8px;
  padding: 16px;
}

.project-table {
  cursor: pointer;
}
</style>
