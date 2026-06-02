<script setup lang="ts">
import {
  Typography,
  Card,
  Tag,
  Space,
  Button,
  Table,
  Popconfirm,
  Empty,
  message,
} from "ant-design-vue";
import {
  FileTextOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  BulbOutlined,
} from "@ant-design/icons-vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { OutlineChapter } from "@/types";

const props = defineProps<{
  projectId: string;
  outline: any;
  outlineChapters: OutlineChapter[];
  outlinePagedChapters: OutlineChapter[];
  outlinePage: number;
  outlinePageSize: number;
  outlineGeneratedCount: number;
  outlineTotalChapters: number;
  globalLoading: boolean;
  taskLoading: boolean;
  stageActionLoading: boolean;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
}>();

const emit = defineEmits<{
  (e: "update:outlinePage", val: number): void;
  (e: "openDetail", chapter: any): void;
  (e: "deleteChapter", index: number): void;
  (e: "deleteAll"): void;
  (e: "generateBatch"): void;
  (e: "confirm", action: any): void;
}>();

const outlineColumns = [
  { title: "序号", key: "index", width: 60 },
  {
    title: "章节标题",
    dataIndex: "title",
    key: "title",
    width: 220,
    ellipsis: true,
  },
  {
    title: "核心事件",
    dataIndex: "core_event",
    key: "core_event",
    ellipsis: true,
  },
  {
    title: "出场角色",
    dataIndex: "characters_present",
    key: "characters_present",
    width: 180,
  },
  { title: "操作", key: "action", width: 140 },
];
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><FileTextOutlined /> 大纲编辑</span>
      <Space>
        <Popconfirm
          v-if="outline && outlineChapters.length > 0"
          title="确定清空全部大纲？此操作不可恢复。"
          @confirm="emit('deleteAll')"
          ok-text="确认清空"
          cancel-text="取消"
          :ok-button-props="{ danger: true }"
        >
          <Button danger :loading="stageActionLoading"
            ><DeleteOutlined /> 全部删除</Button
          >
        </Popconfirm>
        <Button
          v-if="outline && outlineChapters.length > 0 && shouldShowStageConfirm"
          class="stage-action-button btn-adopt"
          :loading="stageActionLoading"
          @click="emit('confirm', 'approve')"
        >
          <CheckCircleOutlined /> 采用
        </Button>
        <Button
          class="stage-action-button btn-generate"
          type="primary"
          :loading="globalLoading"
          :disabled="taskLoading"
          @click="emit('generateBatch')"
        >
          <BulbOutlined />
          {{
            outlineGeneratedCount > 0
              ? `继续生成 (${outlineGeneratedCount}/${outlineTotalChapters})`
              : "AI生成"
          }}
        </Button>
      </Space>
    </div>

    <div class="stage-content">
      <div
        v-if="!outline || outlineChapters.length === 0"
        class="empty-framework"
      >
        <Empty description="大纲为空，点击上方「AI生成」开始创作" />
      </div>

      <template v-if="outline && outlineChapters.length > 0">
        <!-- 伏笔池概览 -->
        <Card
          size="small"
          title="全局伏笔池"
          style="margin-bottom: 24px"
          v-if="outline.foreshadows && outline.foreshadows.length"
        >
          <div class="foreshadow-pool">
            <Tag
              v-for="fs in outline.foreshadows"
              :key="fs.id"
              :color="fs.status === 'callback' ? 'cyan' : 'orange'"
              style="margin-bottom: 8px"
            >
              [ID: {{ fs.id }}] {{ fs.content }}
              <span v-if="fs.revealed_at_chapter"
                >({{ fs.revealed_at_chapter }}章收)</span
              >
            </Tag>
          </div>
        </Card>

        <Table
          :columns="outlineColumns"
          :data-source="outlinePagedChapters"
          :pagination="false"
          size="small"
          row-key="chapter_num"
        >
          <template #bodyCell="{ record, index, column }">
            <template v-if="column.key === 'index'">
              {{ (outlinePage - 1) * outlinePageSize + index + 1 }}
            </template>
            <template v-else-if="column.key === 'title'">
              {{ record.title }}
            </template>
            <template v-else-if="column.key === 'core_event'">
              {{
                record.core_event
                  ? record.core_event.slice(0, 60) +
                    (record.core_event.length > 60 ? "..." : "")
                  : "-"
              }}
            </template>
            <template v-else-if="column.key === 'characters_present'">
              <template
                v-if="
                  Array.isArray(record.characters_present) &&
                  record.characters_present.length
                "
              >
                <Tag
                  v-for="c in record.characters_present.slice(0, 3)"
                  :key="c"
                  size="small"
                  >{{ c }}</Tag
                >
              </template>
              <span v-else>-</span>
            </template>
            <template v-else-if="column.key === 'action'">
              <Space>
                <Button
                  type="link"
                  size="small"
                  @click="emit('openDetail', record)"
                  >查看</Button
                >
                <Button
                  type="link"
                  size="small"
                  danger
                  @click="emit('deleteChapter', index)"
                  >删除</Button
                >
              </Space>
            </template>
          </template>
        </Table>
        <div style="text-align: center; margin-top: 16px">
          <Space>
            <Button
              size="small"
              :disabled="outlinePage <= 1"
              @click="emit('update:outlinePage', outlinePage - 1)"
              >上一页</Button
            >
            <span
              >第 {{ outlinePage }} /
              {{ Math.ceil(outlineChapters.length / outlinePageSize) }} 页</span
            >
            <Button
              size="small"
              :disabled="
                outlinePage >=
                Math.ceil(outlineChapters.length / outlinePageSize)
              "
              @click="emit('update:outlinePage', outlinePage + 1)"
              >下一页</Button
            >
          </Space>
        </div>
      </template>

      <StageConfirm
        v-if="shouldShowStageConfirm && outline && outlineChapters.length > 0"
        class="stage-action-card"
        :stage-name="stageConfirmName"
        :loading="stageActionLoading"
        @confirm="(action) => emit('confirm', action)"
      />
    </div>
  </div>
</template>

<style scoped>
@import "@/assets/styles/project-stages.css";

.stage-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
