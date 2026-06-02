<script setup lang="ts">
import { Typography, Space, Button, Card } from "ant-design-vue";
import { BulbOutlined, CheckCircleOutlined } from "@ant-design/icons-vue";
import TopicCard from "./TopicCard.vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { TopicPlan } from "@/types";

defineProps<{
  projectId: string;
  topicPlans: TopicPlan[];
  globalLoading: boolean;
  taskLoading: boolean;
  loadingTip: string;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
  stageActionLoading: boolean;
}>();

const emit = defineEmits<{
  (e: "generate"): void;
  (e: "select", id: string): void;
  (e: "update"): void;
  (e: "confirm", action: "approve" | "edit" | "regenerate"): void;
}>();
</script>

<template>
  <div class="stage-container">
    <!-- 顶部操作栏 -->
    <div class="stage-top-bar">
      <span class="stage-top-title"><BulbOutlined /> 选题方案</span>
      <Space>
        <Button
          class="stage-action-button btn-generate"
          type="primary"
          :loading="globalLoading"
          :disabled="taskLoading"
          @click="emit('generate')"
        >
          <BulbOutlined /> AI生成
        </Button>
      </Space>
    </div>

    <!-- 内容区 -->
    <div class="stage-content">
      <!-- 空状态占位 -->
      <div v-if="!topicPlans.length" class="empty-framework">
        <div class="empty-card-placeholder" v-for="i in 3" :key="i">
          <div class="empty-card-line title"></div>
          <div class="empty-card-line"></div>
          <div class="empty-card-line short"></div>
        </div>
      </div>

      <!-- 有数据列表 -->
      <TopicCard
        v-for="topic in topicPlans"
        :key="topic.id"
        :topic="topic"
        :project-id="projectId"
        @select="(id) => emit('select', id)"
        @update="emit('update')"
      />

      <!-- 阶段确认 -->
      <StageConfirm
        v-if="shouldShowStageConfirm && topicPlans.length"
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

/* 保持原有布局类名，依靠父组件样式或在此处补齐 */
.stage-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
