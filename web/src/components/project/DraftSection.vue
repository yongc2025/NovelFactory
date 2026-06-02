<script setup lang="ts">
import {
  Typography,
  Card,
  Tag,
  Space,
  Button,
  List,
  Empty,
  Badge,
  Pagination,
} from "ant-design-vue";
import {
  BookOutlined,
  BulbOutlined,
  ReadOutlined,
  FormOutlined,
} from "@ant-design/icons-vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { Draft } from "@/types";

const props = defineProps<{
  projectId: string;
  drafts: Draft[];
  draftPage: number;
  draftPageSize: number;
  globalLoading: boolean;
  taskLoading: boolean;
  stageActionLoading: boolean;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
}>();

const emit = defineEmits<{
  (e: "update:draftPage", val: number): void;
  (e: "generate"): void;
  (e: "read", draft: Draft): void;
  (e: "confirm", action: any): void;
}>();
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><BookOutlined /> 正文创作</span>
      <Space>
        <Button
          v-if="shouldShowStageConfirm && drafts.length > 0"
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
          <BulbOutlined /> AI写正文
        </Button>
      </Space>
    </div>

    <div class="stage-content">
      <div v-if="drafts.length === 0" class="empty-framework">
        <Empty
          description="正文库尚空。请先完成大纲和场景细化，然后点击上方按钮生成正文。"
        />
      </div>

      <List
        v-else
        :data-source="
          drafts.slice(
            (draftPage - 1) * draftPageSize,
            draftPage * draftPageSize,
          )
        "
        class="draft-list"
      >
        <template #renderItem="{ item }">
          <List.Item>
            <Card class="draft-card" hoverable>
              <div class="draft-card-inner">
                <div class="draft-info">
                  <div class="draft-title-row">
                    <span class="draft-title">{{ item.title }}</span>
                    <Badge
                      :status="
                        item.status === 'completed' ? 'success' : 'processing'
                      "
                      :text="item.status === 'completed' ? '已完成' : '创作中'"
                    />
                  </div>
                  <div class="draft-meta">
                    <Tag color="blue">第 {{ item.chapter_number }} 章</Tag>
                    <Tag v-if="item.word_count">{{ item.word_count }} 字</Tag>
                  </div>
                </div>
                <div class="draft-actions">
                  <Button type="primary" ghost @click="emit('read', item)">
                    <ReadOutlined />
                    {{ item.status === "completed" ? "阅读正文" : "查看进度" }}
                  </Button>
                </div>
              </div>
            </Card>
          </List.Item>
        </template>
      </List>

      <div
        v-if="drafts.length > draftPageSize"
        style="text-align: right; margin-top: 16px"
      >
        <Pagination
          :current="draftPage"
          :total="drafts.length"
          :page-size="draftPageSize"
          size="small"
          @change="(val) => emit('update:draftPage', val)"
        />
      </div>

      <StageConfirm
        v-if="shouldShowStageConfirm && drafts.length > 0"
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
.draft-list {
  background: white;
  border-radius: 8px;
}
.draft-card {
  width: 100%;
  margin-bottom: 8px;
}
.draft-card-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.draft-title {
  font-size: 16px;
  font-weight: bold;
  margin-right: 12px;
}
.draft-meta {
  margin-top: 8px;
}
</style>
