<script setup lang="ts">
import { Card, Space, Button, Empty, Typography } from "ant-design-vue";
import {
  ReadOutlined,
  BulbOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons-vue";
import MetadataEditor from "@/components/project/MetadataEditor.vue";
import StageConfirm from "@/components/common/StageConfirm.vue";

const { Text } = Typography;

const props = defineProps<{
  projectId: string;
  metadata: any;
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
  (e: "update", val: any): void;
  (e: "regenerate"): void;
  (e: "confirmMetadata"): void;
  (e: "confirmStage", action: any): void;
}>();
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><ReadOutlined /> 书籍元数据</span>
      <Space>
        <Button
          v-if="metadata"
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
      <div v-if="!metadata" class="empty-framework">
        <div class="empty-card-placeholder">
          <div class="empty-card-line title"></div>
          <div class="empty-card-line"></div>
          <div class="empty-card-line"></div>
          <div class="empty-card-line short"></div>
        </div>
      </div>

      <MetadataEditor
        v-if="metadata"
        :project-id="projectId"
        :metadata="metadata"
        @update="(val) => emit('update', val)"
        @regenerate="emit('regenerate')"
        @confirm="emit('confirmMetadata')"
      />

      <StageConfirm
        v-if="shouldShowStageConfirm && metadata"
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
