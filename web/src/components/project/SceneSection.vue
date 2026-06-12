<script setup lang="ts">
import {
  Typography,
  Card,
  Tag,
  Space,
  Button,
  Table,
  Empty,
  message,
} from "ant-design-vue";
import {
  BlockOutlined,
  BulbOutlined,
  SyncOutlined,
} from "@ant-design/icons-vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { OutlineChapter } from "@/types";

const props = defineProps<{
  projectId: string;
  outlineChapters: OutlineChapter[];
  outlinePagedChapters: OutlineChapter[];
  outlinePage: number;
  outlinePageSize: number;
  globalLoading: boolean;
  taskLoading: boolean;
  stageActionLoading: boolean;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
  getSceneCount: (chNum: number) => number;
}>();

const emit = defineEmits<{
  (e: "update:outlinePage", val: number): void;
  (e: "generate"): void;
  (e: "openDetail", chapter: any): void;
  (e: "confirm", action: any): void;
}>();

const sceneColumns = [
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
    title: "场景数",
    key: "scene_count",
    width: 100,
  },
  { title: "操作", key: "action", width: 120 },
];
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><BlockOutlined /> 场景细纲</span>
      <Space>
        <Button
          v-if="shouldShowStageConfirm && outlineChapters.length > 0"
          class="stage-action-button btn-adopt"
          :loading="stageActionLoading"
          @click="emit('confirm', 'approve')"
        >
          采用
        </Button>
        <Button
          class="stage-action-button btn-generate"
          type="primary"
          :loading="globalLoading"
          :disabled="taskLoading"
          @click="emit('generate')"
        >
          <SyncOutlined /> AI生成全书场景
        </Button>
      </Space>
    </div>

    <div class="stage-content">
      <div v-if="outlineChapters.length === 0" class="empty-framework">
        <Empty description="请先生成大纲，再进行场景细化。" />
      </div>

      <template v-else>
        <Table
          :columns="sceneColumns"
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
            <template v-else-if="column.key === 'scene_count'">
              <Tag color="blue">{{ getSceneCount(record.chapter_num) }}</Tag>
            </template>
            <template v-else-if="column.key === 'action'">
              <Space>
                <Button
                  type="link"
                  size="small"
                  @click="emit('openDetail', record)"
                  >场景详情</Button
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
        v-if="shouldShowStageConfirm && outlineChapters.length > 0"
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
