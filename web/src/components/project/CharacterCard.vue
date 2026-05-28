<script setup lang="ts">
import { ref, h } from 'vue'
import { Card, Tag, Avatar, Descriptions, List, Button, Input, Space, Select, message } from 'ant-design-vue'
import {
  UserOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  DeleteOutlined,
  PlusOutlined,
} from '@ant-design/icons-vue'
import type { Character } from '@/types'

const props = defineProps<{
  character: Character
  projectId: string
}>()

const emit = defineEmits<{
  update: [data: Character]
  delete: [id: string]
}>()

const editing = ref(false)
const editData = ref<Character | null>(null)

const roleColors: Record<string, string> = {
  protagonist: 'blue',
  antagonist: 'red',
  supporting: 'green',
}

const roleLabels: Record<string, string> = {
  protagonist: '主角',
  antagonist: '反派',
  supporting: '配角',
}

const roleOptions = [
  { value: 'protagonist', label: '主角' },
  { value: 'antagonist', label: '反派' },
  { value: 'supporting', label: '配角' },
]

function startEdit() {
  editData.value = JSON.parse(JSON.stringify(props.character))
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editData.value = null
}

async function saveEdit() {
  if (!editData.value) return
  try {
    const { updateCharacters } = await import('@/api')
    await updateCharacters(props.projectId, [editData.value])
    emit('update', editData.value)
    editing.value = false
    editData.value = null
    message.success('角色已保存')
  } catch {
    message.error('保存失败')
  }
}

function addTrait() {
  if (editData.value) editData.value.traits.push('')
}

function removeTrait(index: number) {
  if (editData.value) editData.value.traits.splice(index, 1)
}

function addRelationship() {
  if (editData.value) {
    editData.value.relationships.push({
      target_id: '',
      target_name: '',
      relation: '',
      description: '',
    })
  }
}

function removeRelationship(index: number) {
  if (editData.value) editData.value.relationships.splice(index, 1)
}
</script>

<template>
  <Card class="character-card" hoverable>
    <template #title>
      <div class="char-title">
        <Avatar
          :size="40"
          :style="{
            backgroundColor:
              roleColors[character.role] === 'blue'
                ? '#1d39c4'
                : roleColors[character.role] === 'red'
                  ? '#cf1322'
                  : '#389e0d',
          }"
        >
          <template #icon><UserOutlined /></template>
        </Avatar>
        <div class="char-name-block">
          <template v-if="!editing">
            <span class="char-name">{{ character.name }}</span>
            <Tag :color="roleColors[character.role]">
              {{ roleLabels[character.role] }}
            </Tag>
          </template>
          <template v-else>
            <Input v-model:value="editData!.name" style="width: 150px" />
            <Select v-model:value="editData!.role" :options="roleOptions" style="width: 100px" />
          </template>
        </div>
      </div>
    </template>

    <!-- 查看模式 -->
    <template v-if="!editing">
      <Descriptions :column="1" size="small" bordered>
        <Descriptions.Item label="性格">{{ character.personality }}</Descriptions.Item>
        <Descriptions.Item label="外貌">{{ character.appearance }}</Descriptions.Item>
        <Descriptions.Item label="背景">{{ character.background }}</Descriptions.Item>
        <Descriptions.Item label="人物弧光">{{ character.arc }}</Descriptions.Item>
      </Descriptions>

      <div class="char-traits" v-if="character.traits.length">
        <span class="traits-label">特质：</span>
        <Tag v-for="trait in character.traits" :key="trait" color="purple">
          {{ trait }}
        </Tag>
      </div>

      <div class="char-relationships" v-if="character.relationships.length">
        <div class="rel-title">人物关系</div>
        <List
          :data-source="character.relationships"
          size="small"
          :render-item="({ item: rel }: any) => h(List.Item, null, () => [
            h(Tag, { color: 'cyan' }, () => rel.target_name),
            h('span', null, ` ${rel.relation}：${rel.description}`),
          ])"
        />
      </div>
    </template>

    <!-- 编辑模式 -->
    <template v-else-if="editData">
      <div class="edit-form">
        <div class="form-item">
          <label>性格</label>
          <Input.TextArea v-model:value="editData.personality" :rows="2" />
        </div>
        <div class="form-item">
          <label>外貌</label>
          <Input.TextArea v-model:value="editData.appearance" :rows="2" />
        </div>
        <div class="form-item">
          <label>背景</label>
          <Input.TextArea v-model:value="editData.background" :rows="2" />
        </div>
        <div class="form-item">
          <label>人物弧光</label>
          <Input.TextArea v-model:value="editData.arc" :rows="2" />
        </div>

        <div class="form-item">
          <label>特质</label>
          <div v-for="(trait, i) in editData.traits" :key="i" class="list-edit-item">
            <Input v-model:value="editData.traits[i]" placeholder="特质" />
            <Button type="text" danger @click="removeTrait(i)"><DeleteOutlined /></Button>
          </div>
          <Button type="dashed" size="small" @click="addTrait" style="margin-top: 4px">
            <PlusOutlined /> 添加特质
          </Button>
        </div>

        <div class="form-item">
          <label>人物关系</label>
          <div v-for="(rel, i) in editData.relationships" :key="i" class="rel-edit-item">
            <Input v-model:value="editData.relationships[i].target_name" placeholder="关系人" style="width: 100px" />
            <Input v-model:value="editData.relationships[i].relation" placeholder="关系" style="width: 80px" />
            <Input v-model:value="editData.relationships[i].description" placeholder="描述" style="flex: 1" />
            <Button type="text" danger @click="removeRelationship(i)"><DeleteOutlined /></Button>
          </div>
          <Button type="dashed" size="small" @click="addRelationship" style="margin-top: 4px">
            <PlusOutlined /> 添加关系
          </Button>
        </div>
      </div>
    </template>

    <template #actions>
      <Space>
        <template v-if="!editing">
          <Button type="link" size="small" @click="startEdit">
            <EditOutlined /> 编辑
          </Button>
          <Button type="link" size="small" danger @click="emit('delete', character.id)">
            <DeleteOutlined /> 删除
          </Button>
        </template>
        <template v-else>
          <Button type="link" size="small" @click="cancelEdit">
            <CloseOutlined /> 取消
          </Button>
          <Button type="link" size="small" @click="saveEdit">
            <SaveOutlined /> 保存
          </Button>
        </template>
      </Space>
    </template>
  </Card>
</template>

<style scoped>
.character-card {
  margin-bottom: 16px;
}

.char-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.char-name-block {
  display: flex;
  align-items: center;
  gap: 8px;
}

.char-name {
  font-size: 16px;
  font-weight: 600;
}

.char-traits {
  margin-top: 12px;
}

.traits-label {
  color: var(--color-text-secondary);
  margin-right: 4px;
}

.char-relationships {
  margin-top: 12px;
}

.rel-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-text-secondary);
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

.rel-edit-item {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}
</style>
