<script setup lang="ts">
import {ref, h} from 'vue'
import { Button, Space, Modal, Input } from 'ant-design-vue'
import {
  EditOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons-vue'
import type { ConfirmAction } from '@/types'

const props = withDefaults(defineProps<{
  stageName: string
  loading?: boolean
}>(), {
  loading: false,
})

const emit = defineEmits<{
  confirm: [action: ConfirmAction, feedback?: string]
}>()

const showEditModal = ref(false)
const editFeedback = ref('')

function handleEdit() {
  if (props.loading) return
  showEditModal.value = true
}

function submitEdit() {
  if (props.loading) return
  emit('confirm', 'edit', editFeedback.value)
  showEditModal.value = false
  editFeedback.value = ''
}

function handleRegenerate() {
  if (props.loading) return
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
    <Space size="middle">
      <Button :loading="loading" :disabled="loading" @click="handleEdit">
        <EditOutlined /> 编辑反馈
      </Button>
      <Button danger :loading="loading" :disabled="loading" @click="handleRegenerate">
        <ReloadOutlined /> 重新生成
      </Button>
    </Space>

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
  margin-bottom: 8px;
}
</style>
