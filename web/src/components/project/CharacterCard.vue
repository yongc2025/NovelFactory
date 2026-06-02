<script setup lang="ts">
import { ref, h } from "vue";
import {
  Card,
  Tag,
  Avatar,
  Descriptions,
  List,
  Button,
  Input,
  Space,
  Select,
  message,
} from "ant-design-vue";
import {
  UserOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  DeleteOutlined,
  PlusOutlined,
} from "@ant-design/icons-vue";
import type { Character } from "@/types";

const props = defineProps<{
  character: Character;
  projectId: string;
}>();

const emit = defineEmits<{
  update: [data: Character];
  delete: [id: string];
}>();

const editing = ref(false);
const editData = ref<Character | null>(null);

const roleColors: Record<string, string> = {
  protagonist: "blue",
  antagonist: "red",
  supporting: "green",
};

const roleLabels: Record<string, string> = {
  protagonist: "主角",
  antagonist: "反派",
  supporting: "配角",
};

const roleOptions = [
  { value: "protagonist", label: "主角" },
  { value: "antagonist", label: "反派" },
  { value: "supporting", label: "配角" },
];

function startEdit() {
  editData.value = JSON.parse(JSON.stringify(props.character));
  editing.value = true;
}

function cancelEdit() {
  editing.value = false;
  editData.value = null;
}

async function saveEdit() {
  if (!editData.value) return;
  try {
    const { updateCharacters } = await import("@/api");
    await updateCharacters(props.projectId, [editData.value]);
    emit("update", editData.value);
    editing.value = false;
    editData.value = null;
    message.success("角色已保存");
  } catch {
    message.error("保存失败");
  }
}

function addTrait() {
  if (editData.value) editData.value.traits.push("");
}

function removeTrait(index: number) {
  if (editData.value) editData.value.traits.splice(index, 1);
}

function addRelationship() {
  if (editData.value) {
    editData.value.relationships.push({
      target_id: "",
      target_name: "",
      relation: "",
      description: "",
    });
  }
}

function removeRelationship(index: number) {
  if (editData.value) editData.value.relationships.splice(index, 1);
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
            <Select
              v-model:value="editData!.role"
              :options="roleOptions"
              style="width: 100px"
            />
          </template>
        </div>
      </div>
    </template>

    <!-- 查看模式 -->
    <template v-if="!editing">
      <Descriptions :column="1" size="small" bordered>
        <Descriptions.Item label="性格">{{
          character.personality
        }}</Descriptions.Item>
        <Descriptions.Item label="外貌">{{
          character.appearance
        }}</Descriptions.Item>
        <Descriptions.Item label="背景">{{
          character.background
        }}</Descriptions.Item>
        <Descriptions.Item label="核心欲望">{{
          character.core_desire
        }}</Descriptions.Item>
        <Descriptions.Item label="核心恐惧">{{
          character.core_fear
        }}</Descriptions.Item>
        <Descriptions.Item label="致命弱点">{{
          character.fatal_flaw
        }}</Descriptions.Item>
        <Descriptions.Item label="创伤历史">{{
          character.wound
        }}</Descriptions.Item>
        <Descriptions.Item label="语言风格">{{
          character.speaking_style
        }}</Descriptions.Item>
        <Descriptions.Item label="人物弧光">{{
          character.arc
        }}</Descriptions.Item>
      </Descriptions>

      <div class="char-traits" v-if="character.traits?.length">
        <span class="traits-label">特质：</span>
        <Tag v-for="trait in character.traits" :key="trait" color="purple">
          {{ trait }}
        </Tag>
      </div>

      <div class="char-relationships" v-if="character.relationships?.length">
        <div class="rel-title">人物关系</div>
        <List
          :data-source="character.relationships"
          size="small"
          :render-item="
            ({ item: rel }: any) =>
              h(List.Item, null, () => [
                h(Tag, { color: 'cyan' }, () => rel.target_name),
                h('span', null, ` ${rel.relation}：${rel.description}`),
              ])
          "
        />
      </div>
    </template>

    <!-- 编辑模式 -->
    <template v-else-if="editData">
      <div class="edit-form">
        <div class="form-row">
          <div class="form-item half">
            <label>性格</label>
            <Input v-model:value="editData.personality" />
          </div>
          <div class="form-item half">
            <label>外貌</label>
            <Input v-model:value="editData.appearance" />
          </div>
        </div>
        <div class="form-item">
          <label>背景经历 (Wound)</label>
          <Input.TextArea v-model:value="editData.wound" :rows="2" />
        </div>
        <div class="form-row">
          <div class="form-item half">
            <label>核心欲望 (Desire)</label>
            <Input v-model:value="editData.core_desire" />
          </div>
          <div class="form-item half">
            <label>致命弱点 (Flaw)</label>
            <Input v-model:value="editData.fatal_flaw" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-item half">
            <label>语言风格</label>
            <Input v-model:value="editData.speaking_style" />
          </div>
          <div class="form-item half">
            <label>人物弧光 (Arc)</label>
            <Input v-model:value="editData.arc" />
          </div>
        </div>

        <div class="form-item">
          <label>特质</label>
          <div
            v-for="(trait, i) in editData.traits"
            :key="i"
            class="list-edit-item"
          >
            <Input v-model:value="editData.traits[i]" placeholder="特质" />
            <Button type="text" danger @click="removeTrait(i)"
              ><DeleteOutlined
            /></Button>
          </div>
          <Button
            type="dashed"
            size="small"
            @click="addTrait"
            style="margin-top: 4px"
          >
            <PlusOutlined /> 添加特质
          </Button>
        </div>

        <div class="form-item">
          <label>人物关系</label>
          <div
            v-for="(rel, i) in editData.relationships"
            :key="i"
            class="rel-edit-item"
          >
            <Input
              v-model:value="editData.relationships[i].target_name"
              placeholder="关系人"
              style="width: 100px"
            />
            <Input
              v-model:value="editData.relationships[i].relation"
              placeholder="关系"
              style="width: 80px"
            />
            <Input
              v-model:value="editData.relationships[i].description"
              placeholder="描述"
              style="flex: 1"
            />
            <Button type="text" danger @click="removeRelationship(i)"
              ><DeleteOutlined
            /></Button>
          </div>
          <Button
            type="dashed"
            size="small"
            @click="addRelationship"
            style="margin-top: 4px"
          >
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
          <Button
            type="link"
            size="small"
            danger
            @click="emit('delete', character.id)"
          >
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
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.char-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.char-name-block {
  display: flex;
  align-items: center;
  gap: 8px;
}

.char-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.char-traits {
  margin-top: 16px;
}

.traits-label {
  color: var(--color-text-tertiary);
  margin-right: 8px;
}

.char-relationships {
  margin-top: 16px;
  padding: 12px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.rel-title {
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

/* 编辑模式布局 */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-item.half {
  flex: 1;
}

.form-item label {
  font-size: 13px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.list-edit-item,
.rel-edit-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
</style>
