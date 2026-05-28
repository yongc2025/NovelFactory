<script setup lang="ts">
import { ref, h } from 'vue'
import { Card, Descriptions, Tag, List, Empty, Spin, Button, Input, Space, message } from 'ant-design-vue'
import {
  EnvironmentOutlined,
  ThunderboltOutlined,
  BankOutlined,
  ClusterOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons-vue'
import type { WorldSetting } from '@/types'

const props = defineProps<{
  world: WorldSetting | null
  loading?: boolean
  projectId: string
}>()

const emit = defineEmits<{
  update: [data: WorldSetting]
  confirm: []
}>()

const editing = ref(false)
const editData = ref<WorldSetting | null>(null)

function startEdit() {
  editData.value = JSON.parse(JSON.stringify(props.world))
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editData.value = null
}

async function saveEdit() {
  if (!editData.value) return
  try {
    const { updateWorld } = await import('@/api')
    await updateWorld(props.projectId, editData.value)
    emit('update', editData.value)
    editing.value = false
    editData.value = null
    message.success('世界观已保存')
  } catch {
    message.error('保存失败')
  }
}

function addLocation() {
  if (editData.value) editData.value.key_locations.push('')
}

function removeLocation(index: number) {
  if (editData.value) editData.value.key_locations.splice(index, 1)
}

function addRule() {
  if (editData.value) editData.value.rules.push('')
}

function removeRule(index: number) {
  if (editData.value) editData.value.rules.splice(index, 1)
}

function addConstraint() {
  if (editData.value) editData.value.constraints.push('')
}

function removeConstraint(index: number) {
  if (editData.value) editData.value.constraints.splice(index, 1)
}
</script>

<template>
  <div class="world-panel">
    <Empty v-if="!world && !loading" description="世界观尚未生成" />
    <Spin :spinning="loading" v-else-if="loading">
      <div style="height: 200px" />
    </Spin>
    <template v-else-if="world">
      <!-- 操作栏 -->
      <div class="panel-actions">
        <template v-if="!editing">
          <Button @click="startEdit"><EditOutlined /> 编辑</Button>
          <Button type="primary" @click="emit('confirm')">✅ 采用</Button>
        </template>
        <template v-else>
          <Button @click="cancelEdit"><CloseOutlined /> 取消</Button>
          <Button type="primary" @click="saveEdit"><SaveOutlined /> 保存</Button>
        </template>
      </div>

      <!-- 查看模式 -->
      <template v-if="!editing">
        <Card title="🌍 世界观设定" class="world-card">
          <Descriptions :column="{ xs: 1, sm: 2 }" bordered size="small">
            <Descriptions.Item label="时代背景">
              <EnvironmentOutlined /> {{ world.era }}
            </Descriptions.Item>
            <Descriptions.Item label="地理环境">
              <BankOutlined /> {{ world.geography }}
            </Descriptions.Item>
            <Descriptions.Item label="力量体系" :span="2">
              <ThunderboltOutlined /> {{ world.power_system }}
            </Descriptions.Item>
            <Descriptions.Item label="社会结构" :span="2">
              <ClusterOutlined /> {{ world.social_structure }}
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Card title="📍 关键地点" class="world-card" style="margin-top: 16px">
          <List
            :data-source="world.key_locations"
            size="small"
            :render-item="({ item }: any) => h(List.Item, null, () => h(Tag, { color: 'blue' }, () => item))"
          />
        </Card>

        <Card title="📜 世界规则" class="world-card" style="margin-top: 16px">
          <List
            :data-source="world.rules"
            size="small"
            :render-item="({ item }: any) => h(List.Item, null, () => item)"
          />
        </Card>

        <Card title="⚠️ 约束条件" class="world-card" style="margin-top: 16px">
          <List
            :data-source="world.constraints"
            size="small"
            :render-item="({ item }: any) => h(List.Item, null, () => h(Tag, { color: 'orange' }, () => item))"
          />
        </Card>
      </template>

      <!-- 编辑模式 -->
      <template v-else-if="editData">
        <Card title="🌍 世界观设定" class="world-card">
          <div class="edit-form">
            <div class="form-item">
              <label>时代背景</label>
              <Input v-model:value="editData.era" placeholder="如：架空古代、未来科幻" />
            </div>
            <div class="form-item">
              <label>地理环境</label>
              <Input.TextArea v-model:value="editData.geography" :rows="2" />
            </div>
            <div class="form-item">
              <label>力量体系</label>
              <Input.TextArea v-model:value="editData.power_system" :rows="2" />
            </div>
            <div class="form-item">
              <label>社会结构</label>
              <Input.TextArea v-model:value="editData.social_structure" :rows="2" />
            </div>
          </div>
        </Card>

        <Card title="📍 关键地点" class="world-card" style="margin-top: 16px">
          <div v-for="(loc, i) in editData.key_locations" :key="i" class="list-edit-item">
            <Input v-model:value="editData.key_locations[i]" placeholder="地点名称" />
            <Button type="text" danger @click="removeLocation(i)"><DeleteOutlined /></Button>
          </div>
          <Button type="dashed" block @click="addLocation" style="margin-top: 8px">
            <PlusOutlined /> 添加地点
          </Button>
        </Card>

        <Card title="📜 世界规则" class="world-card" style="margin-top: 16px">
          <div v-for="(rule, i) in editData.rules" :key="i" class="list-edit-item">
            <Input v-model:value="editData.rules[i]" placeholder="规则描述" />
            <Button type="text" danger @click="removeRule(i)"><DeleteOutlined /></Button>
          </div>
          <Button type="dashed" block @click="addRule" style="margin-top: 8px">
            <PlusOutlined /> 添加规则
          </Button>
        </Card>

        <Card title="⚠️ 约束条件" class="world-card" style="margin-top: 16px">
          <div v-for="(c, i) in editData.constraints" :key="i" class="list-edit-item">
            <Input v-model:value="editData.constraints[i]" placeholder="约束描述" />
            <Button type="text" danger @click="removeConstraint(i)"><DeleteOutlined /></Button>
          </div>
          <Button type="dashed" block @click="addConstraint" style="margin-top: 8px">
            <PlusOutlined /> 添加约束
          </Button>
        </Card>
      </template>
    </template>
  </div>
</template>

<style scoped>
.world-panel {
  padding: 8px 0;
}

.world-card {
  margin-bottom: 0;
}

.panel-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  justify-content: flex-end;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-item label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.list-edit-item {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.list-edit-item .ant-input {
  flex: 1;
}
</style>
