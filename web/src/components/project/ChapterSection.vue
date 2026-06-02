<script setup lang="ts">
import { Card, Space, Button, Empty, Typography } from "ant-design-vue";
import {
  ReadOutlined,
  BulbOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons-vue";
import ChapterReader from "@/components/project/ChapterReader.vue";
import StageConfirm from "@/components/common/StageConfirm.vue";

const props = defineProps<{
  projectId: string;
  currentChapter: any;
  totalChapters: number;
  globalLoading: boolean;
  taskLoading: boolean;
  stageActionLoading: boolean;
  canApproveCurrentStage: boolean;
  approveButtonTitle: string;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
}>();

const emit = defineEmits<{
  (e: "runStage"): void;
  (e: "prev"): void;
  (e: "next"): void;
  (e: "update", val: any): void;
  (e: "confirmStage", action: any): void;
}>();
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><ReadOutlined /> 正文阅读</span>
      <Space>
        <Button
          v-if="currentChapter"
          class="stage-action-button btn-adopt"
          :loading="stageActionLoading"
          :disabled="!canApproveCurrentStage || stageActionLoading"
          :title="approveButtonTitle"
          @click="emit('confirmStage', 'approve')"
        >
          <CheckCircleOutlined /> 采用
        </Button>
        <Button
          class="stage-action-button btn-generate"
          type="primary"
          :loading="globalLoading"
          :disabled="taskLoading"
          @click="emit('runStage')"
        >
          <BulbOutlined /> AI生成
        </Button>
      </Space>
    </div>

    <div class="stage-content">
      <div v-if="!currentChapter" class="empty-framework">
        <div class="empty-card-placeholder" v-for="i in 5" :key="i">
          <div class="empty-card-line"></div>
          <div class="empty-card-line"></div>
          <div class="empty-card-line short"></div>
        </div>
      </div>

      <ChapterReader
        v-if="currentChapter"
        :chapter="currentChapter"
        :loading="globalLoading"
        :total-chapters="totalChapters"
        :project-id="projectId"
        @prev="emit('prev')"
        @next="emit('next')"
        @update="(val) => emit('update', val)"
      />

      <StageConfirm
        v-if="shouldShowStageConfirm && currentChapter"
        class="stage-action-card"
        :stage-name="stageConfirmName"
        :loading="stageActionLoading"
        @confirm="(action) => emit('confirmStage', action)"
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
