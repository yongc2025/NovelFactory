<script setup lang="ts">
import { Typography, Space, Button } from "ant-design-vue";
import {
  TeamOutlined,
  BulbOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons-vue";
import CharacterCard from "./CharacterCard.vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { Character } from "@/types";

defineProps<{
  projectId: string;
  characters: Character[];
  globalLoading: boolean;
  taskLoading: boolean;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
  stageActionLoading: boolean;
  canApproveCurrentStage: boolean;
  approveButtonTitle: string;
}>();

const emit = defineEmits<{
  (e: "generate"): void;
  (e: "confirm", action: "approve" | "edit" | "regenerate"): void;
  (e: "update"): void;
  (e: "delete"): void;
}>();
</script>

<template>
  <div class="stage-container">
    <!-- 顶部操作栏 -->
    <div class="stage-top-bar">
      <span class="stage-top-title"><TeamOutlined /> 角色列表</span>
      <Space>
        <Button
          v-if="characters.length"
          class="stage-action-button btn-adopt"
          :loading="stageActionLoading"
          :disabled="!canApproveCurrentStage || stageActionLoading"
          :title="approveButtonTitle"
          @click="emit('confirm', 'approve')"
        >
          <CheckCircleOutlined /> 采用
        </Button>
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
      <!-- 空状态 -->
      <div v-if="!characters.length" class="empty-framework">
        <div class="empty-card-placeholder" v-for="i in 3" :key="i">
          <div
            style="
              display: flex;
              align-items: center;
              gap: 12px;
              margin-bottom: 12px;
            "
          >
            <div class="empty-avatar"></div>
            <div class="empty-card-line title" style="flex: 1"></div>
          </div>
          <div class="empty-card-line"></div>
          <div class="empty-card-line short"></div>
        </div>
      </div>

      <!-- 角色列表 -->
      <CharacterCard
        v-for="char in characters"
        :key="char.id"
        :character="char"
        :project-id="projectId"
        @update="emit('update')"
        @delete="emit('delete')"
      />

      <!-- 阶段确认 -->
      <StageConfirm
        v-if="shouldShowStageConfirm && characters.length"
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
