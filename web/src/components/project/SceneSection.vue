<script setup lang="ts">
import {
  Typography,
  Card,
  Tag,
  Space,
  Button,
  Empty,
  Row,
  Col,
  Badge,
  Progress,
} from "ant-design-vue";
import {
  PictureOutlined,
  BulbOutlined,
  EditOutlined,
  EyeOutlined,
} from "@ant-design/icons-vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import type { Scene } from "@/types";

const props = defineProps<{
  projectId: string;
  scenes: Scene[];
  globalLoading: boolean;
  taskLoading: boolean;
  stageActionLoading: boolean;
  shouldShowStageConfirm: boolean;
  stageConfirmName: string;
}>();

const emit = defineEmits<{
  (e: "generate"): void;
  (e: "openDetail", scene: Scene): void;
  (e: "confirm", action: any): void;
}>();
</script>

<template>
  <div class="stage-container">
    <div class="stage-top-bar">
      <span class="stage-top-title"><PictureOutlined /> 场景细化</span>
      <Space>
        <Button
          v-if="shouldShowStageConfirm && scenes.length > 0"
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
          <BulbOutlined /> AI细化场景
        </Button>
      </Space>
    </div>

    <div class="stage-content">
      <div v-if="scenes.length === 0" class="empty-framework">
        <Empty description="暂无场景。请先生成或点击上方按钮进行场景细化。" />
      </div>

      <Row v-else :gutter="[16, 16]">
        <Col
          v-for="scene in scenes"
          :key="scene.scene_id"
          :xs="24"
          :sm="12"
          :md="8"
        >
          <Card hoverable class="scene-card" @click="emit('openDetail', scene)">
            <template #title>
              <div class="scene-card-header">
                <span class="scene-title">{{ scene.title }}</span>
                <Badge
                  :status="
                    scene.status === 'completed' ? 'success' : 'processing'
                  "
                  :text="scene.status === 'completed' ? '已完成' : '待处理'"
                />
              </div>
            </template>
            <div class="scene-body">
              <div class="scene-desc">{{ scene.description }}</div>
              <div class="scene-meta">
                <Tag v-if="scene.location">{{ scene.location }}</Tag>
                <Tag v-if="scene.time_of_day">{{ scene.time_of_day }}</Tag>
              </div>
            </div>
            <template #actions>
              <EditOutlined key="edit" />
              <EyeOutlined key="view" />
            </template>
          </Card>
        </Col>
      </Row>

      <StageConfirm
        v-if="shouldShowStageConfirm && scenes.length > 0"
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
.scene-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.scene-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.scene-title {
  font-weight: bold;
}
.scene-body {
  flex: 1;
}
.scene-desc {
  color: rgba(0, 0, 0, 0.45);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
  font-size: 13px;
}
</style>
