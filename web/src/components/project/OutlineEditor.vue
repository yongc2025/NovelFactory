<script setup lang="ts">
import { ref, computed } from "vue";
import {
  Card,
  Tag,
  Input,
  Button,
  Collapse,
  Empty,
  Space,
  InputNumber,
  Popconfirm,
  message,
} from "ant-design-vue";
import {
  EditOutlined,
  SaveOutlined,
  BookOutlined,
  UserOutlined,
  CloseOutlined,
  PlusOutlined,
  DeleteOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from "@ant-design/icons-vue";
import type { Outline, OutlineChapter } from "@/types";

const props = defineProps<{
  outline: Outline | null;
  loading?: boolean;
  projectId: string;
  showConfirm?: boolean;
  hideActions?: boolean;
}>();

const emit = defineEmits<{
  update: [data: Outline];
  confirm: [];
}>();

const editing = ref(false);
const editData = ref<Outline | null>(null);

// 单章编辑（查看模式下）
const editingIndex = ref<number | null>(null);
const editForm = ref<OutlineChapter | null>(null);

function startEdit() {
  editData.value = JSON.parse(JSON.stringify(props.outline));
  editing.value = true;
  editingIndex.value = null;
  editForm.value = null;
}

function cancelEdit() {
  editing.value = false;
  editData.value = null;
}

async function saveEdit() {
  if (!editData.value) return;
  try {
    const { updateOutline } = await import("@/api");
    // 重新编号
    editData.value.chapters.forEach((ch, i) => {
      ch.chapter_number = i + 1;
    });
    // total_chapters 保持不变（生成目标），不随编辑覆盖
    await updateOutline(props.projectId, editData.value);
    emit("update", editData.value);
    editing.value = false;
    editData.value = null;
    message.success("大纲已保存");
  } catch {
    message.error("保存失败");
  }
}

// 查看模式下编辑单章
function startEditChapter(index: number, chapter: OutlineChapter) {
  editingIndex.value = index;
  editForm.value = JSON.parse(JSON.stringify(chapter));
}

function cancelEditChapter() {
  editingIndex.value = null;
  editForm.value = null;
}

async function saveEditChapter() {
  if (!editForm.value || editingIndex.value === null || !props.outline) return;
  try {
    const updated = JSON.parse(JSON.stringify(props.outline));
    updated.chapters[editingIndex.value] = editForm.value;
    const { updateOutline } = await import("@/api");
    await updateOutline(props.projectId, updated);
    emit("update", updated);
    editingIndex.value = null;
    editForm.value = null;
    message.success("章节已保存");
  } catch {
    message.error("保存失败");
  }
}

// 编辑模式：章节操作
function moveChapter(index: number, direction: -1 | 1) {
  if (!editData.value) return;
  const chapters = editData.value.chapters;
  const newIndex = index + direction;
  if (newIndex < 0 || newIndex >= chapters.length) return;
  const temp = chapters[index];
  chapters[index] = chapters[newIndex];
  chapters[newIndex] = temp;
}

function addChapter() {
  if (!editData.value) return;
  const nextNum = editData.value.chapters.length + 1;
  editData.value.chapters.push({
    chapter_number: nextNum,
    title: `第${nextNum}章`,
    core_event: "",
    characters_present: [],
    emotion_position: "",
    hook: "",
    foreshadow_ops: [],
  });
}

function deleteChapter(index: number) {
  if (!editData.value) return;
  editData.value.chapters.splice(index, 1);
}

function addForeshadow(chapterIndex: number) {
  if (!editData.value) return;
  editData.value.chapters[chapterIndex].foreshadow_ops.push("");
}

function removeForeshadow(chapterIndex: number, eventIndex: number) {
  if (!editData.value) return;
  editData.value.chapters[chapterIndex].foreshadow_ops.splice(eventIndex, 1);
}

const collapseItems = computed(() => {
  if (!props.outline) return [];
  return props.outline.chapters.map((ch, i) => ({
    key: String(i),
    label: ch.title?.startsWith("第")
      ? ch.title
      : `第${ch.chapter_number}章 ${ch.title}`,
    children: ch,
  }));
});

defineExpose({ startEdit, cancelEdit, editing });
</script>

<template>
  <div class="outline-editor">
    <Empty v-if="!outline && !loading" description="大纲尚未生成" />
    <Spin :spinning="loading" v-else-if="loading">
      <div style="height: 200px" />
    </Spin>
    <template v-else-if="outline">
      <!-- 操作栏 -->
      <div class="outline-header">
        <span class="outline-info">
          <BookOutlined />
          共 {{ outline.total_chapters }} 章
        </span>
        <Space v-if="!hideActions">
          <template v-if="!editing">
            <Button @click="startEdit"><EditOutlined /> 编辑全部</Button>
            <Button
              v-if="showConfirm !== false"
              type="primary"
              @click="emit('confirm')"
              >✅ 采用</Button
            >
          </template>
          <template v-else>
            <Button @click="cancelEdit"><CloseOutlined /> 取消</Button>
            <Button type="primary" @click="saveEdit"
              ><SaveOutlined /> 保存全部</Button
            >
          </template>
        </Space>
      </div>

      <!-- 查看模式 -->
      <template v-if="!editing">
        <Collapse accordion>
          <Collapse.Panel
            v-for="(ch, index) in outline.chapters"
            :key="index"
            :header="
              ch.title?.startsWith('第')
                ? ch.title
                : `第${ch.chapter_number}章 ${ch.title}`
            "
          >
            <template v-if="editingIndex === index && editForm">
              <div class="edit-form">
                <div class="form-item">
                  <label>标题</label>
                  <Input v-model:value="editForm.title" />
                </div>
                <div class="form-item">
                  <label>核心事件</label>
                  <Input.TextArea
                    v-model:value="editForm.core_event"
                    :rows="3"
                  />
                </div>
                <div class="form-item">
                  <label>出场角色（逗号分隔）</label>
                  <Input
                    :value="
                      Array.isArray(editForm.characters_present)
                        ? editForm.characters_present.join('、')
                        : ''
                    "
                    @update:value="
                      (v: string) =>
                        (editForm!.characters_present = v
                          .split(/[、,，]/)
                          .filter(Boolean))
                    "
                    placeholder="角色1、角色2"
                  />
                </div>
                <div class="form-item">
                  <label>情绪定位</label>
                  <Input
                    v-model:value="editForm.emotion_position"
                    placeholder="如：压抑-释然"
                  />
                </div>
                <div class="form-item">
                  <label>钩子</label>
                  <Input.TextArea v-model:value="editForm.hook" :rows="2" />
                </div>
                <div class="form-item">
                  <label>伏笔操作（每行一个）</label>
                  <Input.TextArea
                    :value="
                      (editForm.foreshadow_ops || [])
                        .map((op) =>
                          typeof op === 'string'
                            ? op
                            : `${op.action === 'plant' ? '埋设' : '回收'}：${op.content}${op.id ? ' [ID:' + op.id + ']' : ''}`,
                        )
                        .join('\n')
                    "
                    @update:value="
                      (v: string) =>
                        (editForm!.foreshadow_ops = v
                          .split('\\n')
                          .filter(Boolean))
                    "
                    :rows="3"
                    placeholder="每行一个伏笔"
                  />
                </div>
                <Space style="margin-top: 12px">
                  <Button type="primary" size="small" @click="saveEditChapter">
                    <SaveOutlined /> 保存
                  </Button>
                  <Button size="small" @click="cancelEditChapter">取消</Button>
                </Space>
              </div>
            </template>
            <template v-else>
              <div class="chapter-info">
                <p class="chapter-summary">
                  {{ ch.core_event || ch.summary || "-" }}
                </p>
                <div class="chapter-meta">
                  <template
                    v-if="ch.characters_present && ch.characters_present.length"
                  >
                    <Tag
                      v-for="c in ch.characters_present"
                      :key="c"
                      color="blue"
                    >
                      <UserOutlined /> {{ c }}
                    </Tag>
                  </template>
                  <Tag v-if="ch.emotion_position" color="purple">{{
                    ch.emotion_position
                  }}</Tag>
                </div>
                <p v-if="ch.hook" class="chapter-hook">🪝 {{ ch.hook }}</p>
                <div
                  class="chapter-events"
                  v-if="ch.foreshadow_ops && ch.foreshadow_ops.length"
                >
                  <div class="events-label">伏笔操作：</div>
                  <ul>
                    <li v-for="(item, i) in ch.foreshadow_ops" :key="i">
                      <template v-if="typeof item === 'string'">{{
                        item
                      }}</template>
                      <template v-else>
                        <Tag
                          :color="item.action === 'plant' ? 'orange' : 'cyan'"
                          size="small"
                        >
                          {{ item.action === "plant" ? "埋设" : "回收" }}
                        </Tag>
                        <span
                          v-if="item.id"
                          style="color: #8c8c8c; margin-right: 4px"
                          >[ID:{{ item.id }}]</span
                        >
                        {{ item.content }}
                      </template>
                    </li>
                  </ul>
                </div>
                <Button
                  type="link"
                  size="small"
                  @click="startEditChapter(index, ch)"
                  style="padding: 0; margin-top: 8px"
                >
                  <EditOutlined /> 编辑
                </Button>
              </div>
            </template>
          </Collapse.Panel>
        </Collapse>
      </template>

      <!-- 编辑全部模式 -->
      <template v-else-if="editData">
        <div class="chapters-edit">
          <div
            v-for="(ch, index) in editData.chapters"
            :key="index"
            class="chapter-edit-card"
          >
            <Card size="small">
              <template #title>
                <div class="chapter-edit-header">
                  <span>第{{ index + 1 }}章</span>
                  <Space>
                    <Button
                      size="small"
                      :disabled="index === 0"
                      @click="moveChapter(index, -1)"
                    >
                      <ArrowUpOutlined />
                    </Button>
                    <Button
                      size="small"
                      :disabled="index === editData.chapters.length - 1"
                      @click="moveChapter(index, 1)"
                    >
                      <ArrowDownOutlined />
                    </Button>
                    <Popconfirm
                      title="确定删除此章？"
                      @confirm="deleteChapter(index)"
                    >
                      <Button size="small" danger><DeleteOutlined /></Button>
                    </Popconfirm>
                  </Space>
                </div>
              </template>

              <div class="edit-form">
                <div class="form-item">
                  <label>标题</label>
                  <Input v-model:value="ch.title" />
                </div>
                <div class="form-item">
                  <label>核心事件</label>
                  <Input.TextArea v-model:value="ch.core_event" :rows="3" />
                </div>
                <div class="form-row">
                  <div class="form-item" style="flex: 1">
                    <label>出场角色（逗号分隔）</label>
                    <Input
                      :value="
                        Array.isArray(ch.characters_present)
                          ? ch.characters_present.join('、')
                          : ''
                      "
                      @update:value="
                        (v: string) =>
                          (ch.characters_present = v
                            .split(/[、,，]/)
                            .filter(Boolean))
                      "
                      placeholder="角色1、角色2"
                    />
                  </div>
                  <div class="form-item" style="width: 200px">
                    <label>情绪定位</label>
                    <Input
                      v-model:value="ch.emotion_position"
                      placeholder="如：压抑-释然"
                    />
                  </div>
                </div>
                <div class="form-item">
                  <label>钩子</label>
                  <Input.TextArea v-model:value="ch.hook" :rows="2" />
                </div>
                <div class="form-item">
                  <label>伏笔操作</label>
                  <div
                    v-for="(item, ei) in ch.foreshadow_ops"
                    :key="ei"
                    class="list-edit-item"
                  >
                    <Input
                      :value="
                        typeof ch.foreshadow_ops[ei] === 'string'
                          ? ch.foreshadow_ops[ei]
                          : (ch.foreshadow_ops[ei] as any).content
                      "
                      @update:value="
                        (v: string) => {
                          if (typeof ch.foreshadow_ops[ei] === 'string') {
                            ch.foreshadow_ops[ei] = v;
                          } else {
                            (ch.foreshadow_ops[ei] as any).content = v;
                          }
                        }
                      "
                      placeholder="伏笔描述"
                    />
                    <Button
                      type="text"
                      danger
                      @click="removeForeshadow(index, ei)"
                    >
                      <DeleteOutlined />
                    </Button>
                  </div>
                  <Button
                    type="dashed"
                    size="small"
                    @click="addForeshadow(index)"
                    style="margin-top: 4px"
                  >
                    <PlusOutlined /> 添加伏笔
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          <Button
            type="dashed"
            block
            @click="addChapter"
            style="margin-top: 16px"
          >
            <PlusOutlined /> 添加新章节
          </Button>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.outline-editor {
  padding: 8px 0;
}

.outline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.outline-info {
  font-size: 16px;
  font-weight: 500;
}

.chapter-summary {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.chapter-hook {
  color: var(--color-text-secondary);
  font-style: italic;
  margin-bottom: 8px;
}

.chapter-meta {
  margin-bottom: 8px;
}

.events-label {
  color: var(--color-text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

.chapter-events ul {
  padding-left: 20px;
  margin: 0;
}

.chapter-events li {
  margin-bottom: 4px;
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

.form-row {
  display: flex;
  gap: 12px;
}

.chapter-edit-card {
  margin-bottom: 12px;
}

.chapter-edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
