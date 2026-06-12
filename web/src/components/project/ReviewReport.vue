<script setup lang="ts">
import {computed, h} from 'vue'
import { Card, Progress, Table, Tag, List, Empty, Spin, Descriptions } from 'ant-design-vue'
import type { ReviewReport as ReviewReportType, ReviewIssue } from '@/types'

const props = defineProps<{
  report: ReviewReportType | null
  loading?: boolean
}>()

const severityColors: Record<string, string> = {
  critical: 'red',
  warning: 'orange',
  info: 'blue',
}

const severityLabels: Record<string, string> = {
  critical: '严重',
  warning: '警告',
  info: '提示',
}

const scoreColor = (score: number) => {
  if (score >= 80) return '#52c41a'
  if (score >= 60) return '#faad14'
  return '#f5222d'
}

const issueColumns = [
  { title: '章节/位置', dataIndex: 'chapter_number', width: 100, customRender: ({ text, record }: any) => {
      if (text > 0) return `第 ${text} 章`
      // 如果没有章节号，显示建议栏中的位置信息（我们在后端把 location 映射到了 suggestion）
      return record.suggestion || '-'
    }
  },
  {
    title: '严重度',
    dataIndex: 'severity',
    width: 100,
    customRender: ({ text }: { text: string }) =>
      h(Tag, { color: severityColors[text] || 'blue' }, () => severityLabels[text] || '提示'),
  },
  { title: '分类', dataIndex: 'category', width: 120 },
  { title: '问题描述', dataIndex: 'description', ellipsis: true },
]

// 建议列表渲染函数 - 修正参数签名为 (item, index)
function renderSuggestionItem(item: string, index: number) {
  return h(List.Item, null, () => `${index + 1}. ${item}`)
}
</script>

<template>
  <div class="review-report">
    <Empty v-if="!report && !loading" description="审校报告尚未生成" />
    <Spin :spinning="loading" v-else-if="loading">
      <div style="height: 200px" />
    </Spin>
    <template v-else-if="report">
      <Card title="📊 综合评分" class="report-card">
        <div class="score-overview">
          <div class="score-main">
            <Progress
              type="dashboard"
              :percent="report.overall_score || 0"
              :stroke-color="scoreColor(report.overall_score || 0)"
              :size="140"
            />
            <div class="score-label">综合评分</div>
          </div>
          <div class="score-details">
            <div class="score-item">
              <span class="item-label">一致性</span>
              <Progress :percent="report.consistency_score || 0" :stroke-color="scoreColor(report.consistency_score || 0)" size="small" />
            </div>
            <div class="score-item">
              <span class="item-label">剧情</span>
              <Progress :percent="report.plot_score || 0" :stroke-color="scoreColor(report.plot_score || 0)" size="small" />
            </div>
            <div class="score-item">
              <span class="item-label">角色</span>
              <Progress :percent="report.character_score || 0" :stroke-color="scoreColor(report.character_score || 0)" size="small" />
            </div>
            <div class="score-item">
              <span class="item-label">文笔</span>
              <Progress :percent="report.writing_score || 0" :stroke-color="scoreColor(report.writing_score || 0)" size="small" />
            </div>
          </div>
        </div>
      </Card>

      <div class="two-columns" style="margin-top: 16px">
        <Card title="🌟 作品亮点" class="report-card flex-1" v-if="report.highlights && report.highlights.length">
          <List
            :data-source="report.highlights"
            size="small"
            :render-item="renderSuggestionItem"
          />
        </Card>
        <Card title="💡 改进建议" class="report-card flex-1" v-if="report.suggestions && report.suggestions.length">
          <List
            :data-source="report.suggestions"
            size="small"
            :render-item="renderSuggestionItem"
          />
        </Card>
      </div>

      <Card title="⚠️ 发现问题" class="report-card" style="margin-top: 16px" v-if="report.issues && report.issues.length">
        <Table
          :columns="issueColumns"
          :data-source="report.issues"
          :pagination="{ pageSize: 10 }"
          size="small"
          :row-key="(_: any, i: any) => i"
        />
      </Card>
    </template>
  </div>
</template>

<style scoped>
.review-report {
  padding: 8px 0;
}

.report-card {
  margin-bottom: 0;
}

.two-columns {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
}

.score-overview {
  display: flex;
  align-items: center;
  gap: 48px;
  flex-wrap: wrap;
}

.score-main {
  text-align: center;
}

.score-label {
  margin-top: 8px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.score-details {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-label {
  width: 60px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.report-summary {
  line-height: 1.8;
  color: var(--color-text);
}
</style>
