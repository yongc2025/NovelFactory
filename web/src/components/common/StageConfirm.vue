<script setup lang="ts">
import { ref } from 'vue'
import { Card, Button, Space, Modal, Input, Typography } from 'ant-design-vue'
import {
  CheckCircleOutlined,
  EditOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons-vue'
import type { ConfirmAction } from '@/types'

const props = defineProps<{
  stageName: string
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: [action: ConfirmAction, feedback?: string]
}>()

const showEditModal = ref(false)
const editFeedback = ref('')

function handleApprove() {
  emit('confirm', 'approve')
}

function handleEdit() {
  showEditModal.value = true
}

function submitEdit() {
  emit('confirm', 'edit', editFeedback.value)
  showEditModal.value = false
  editFeedback.value = ''
}

function handleRegenerate() {
  Modal.confirm({
    title: '确认重新生成',
    icon: h(ExclamationCircleOutlined),
    content: `确定要重新生成「${props.stageName}」吗？当前内容将被替换。`,
    onOk() {
      emit('confirm', 'regenerate')
    },
  })
}
</script>

<template>
  <div class="stage-confirm">
    <Card class="confirm-card">
      <div class="confirm-content">
        <div class="confirm-title">
          <CheckCircleOutlined class="confirm-icon" />
          <span>「{{ stageName }}」阶段已完成</span>
        </div>
        <p class="confirm-desc">请审阅生成内容，选择后续操作：</p>

        <Space size="middle" wrap>
          <Button type="primary" size="large" :loading="loading" @click="handleApprove">
            <CheckCircleOutlined /> 采用
          </Button>
          <Button size="large" :loading="loading" @click="handleEdit">
            <EditOutlined /> 编辑反馈
          </Button>
          <Button danger size="large" :loading="loading" @click="handleRegenerate">
            <ReloadOutlined /> 重新生成
          </Button>
        </Space>
      </div>
    </Card>

    <Modal
      v-model:open="showEditModal"
      title="编辑反馈"
      @ok="submitEdit"
      :confirm-loading="loading"
    >
      <p>请输入您的修改意见，系统将根据反馈进行调整：</p>
      <Input.TextArea
        v-model:value="editFeedback"
        :rows="4"
        placeholder="例如：希望增加更多关于主角内心挣扎的描写..."
      />
    </Modal>
  </div>
</template>

<style scoped>
.stage-confirm {
  margin: 16px 0;
}

.confirm-card {
  border-color: #b7eb8f;
  background: #f6ffed;
}

.confirm-content {
  text-align: center;
  padding: 8px 0;
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.confirm-icon {
  color: #52c41a;
  font-size: 24px;
}

.confirm-desc {
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}
</style>
