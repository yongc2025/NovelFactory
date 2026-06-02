<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Card,
  Button,
  Tag,
  Space,
  Typography,
  Tabs,
  TabPane,
  Spin,
  Progress,
  Table,
  Modal,
  Popconfirm,
  InputNumber,
  Empty,
  Collapse,
  message,
} from "ant-design-vue";
import {
  ArrowLeftOutlined,
  PlayCircleOutlined,
  BulbOutlined,
  GlobalOutlined,
  TeamOutlined,
  FileTextOutlined,
  ReadOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  EditOutlined,
  CloseOutlined,
  BlockOutlined,
  SyncOutlined,
} from "@ant-design/icons-vue";
import AppLayout from "@/components/layout/AppLayout.vue";
import PipelineProgress from "@/components/project/PipelineProgress.vue";
import TopicCard from "@/components/project/TopicCard.vue";
import WorldPanel from "@/components/project/WorldPanel.vue";
import CharacterCard from "@/components/project/CharacterCard.vue";
import OutlineEditor from "@/components/project/OutlineEditor.vue";
import MetadataEditor from "@/components/project/MetadataEditor.vue";
import ChapterReader from "@/components/project/ChapterReader.vue";
import ReviewReport from "@/components/project/ReviewReport.vue";
import StageConfirm from "@/components/common/StageConfirm.vue";
import ProjectOverview from "@/components/project/ProjectOverview.vue";
import TopicSection from "@/components/project/TopicSection.vue";
import CharacterSection from "@/components/project/CharacterSection.vue";
import OutlineSection from "@/components/project/OutlineSection.vue";
import SceneSection from "@/components/project/SceneSection.vue";
import DraftSection from "@/components/project/DraftSection.vue";
import MetadataSection from "@/components/project/MetadataSection.vue";
import ChapterSection from "@/components/project/ChapterSection.vue";
import ReviewSection from "@/components/project/ReviewSection.vue";
import { useTaskPoller } from "@/composables/useTaskPoller";
import { useProjectStore } from "@/stores/project";
import type { ConfirmAction, BookMetadata } from "@/types";

const { Title, Text } = Typography;

const route = useRoute();
const router = useRouter();
const store = useProjectStore();
const taskPoller = useTaskPoller();

const projectId = computed(() => route.params.id as string);
const activeTab = computed(() => (route.meta.tab as string) || "overview");
const stageActionLoading = ref(false);
const stageActionText = ref("");
const taskLoading = computed(
  () => taskPoller.isActive.value || taskPoller.isPolling.value,
);
const globalLoading = computed(
  () => store.loading || stageActionLoading.value || taskLoading.value,
);
const loadingTip = computed(
  () => stageActionText.value || taskPoller.statusText.value || "加载中...",
);
const currentChapterNum = computed(() => {
  const num = route.params.num;
  return num ? parseInt(num as string) : 1;
});

// 大纲表格相关
const outlinePage = ref(1);
const outlinePageSize = 10;
const outlineDrawerVisible = ref(false);
const outlineDrawerChapter = ref<any>(null);
const outlineBatchDialogVisible = ref(false);
const outlineBatchSize = ref(10);

// 阶段名称映射
const stageNames: Record<string, string> = {
  topic: "选题方案",
  world: "世界观",
  character: "角色设定",
  characters: "角色设定",
  outline: "大纲",
  metadata: "书籍元数据",
  draft: "正文",
  scene: "场景细纲",
  chapters: "正文",
  review: "审校报告",
};

// 横向 Tab 配置
const tabItems = [
  { key: "overview", label: "项目概览", icon: BulbOutlined },
  { key: "topic", label: "选题方案", icon: BulbOutlined },
  { key: "world", label: "世界观", icon: GlobalOutlined },
  { key: "characters", label: "角色列表", icon: TeamOutlined },
  { key: "outline", label: "大纲编辑", icon: FileTextOutlined },
  { key: "scene", label: "场景细纲", icon: BlockOutlined },
  { key: "metadata", label: "书籍元数据", icon: ReadOutlined },
  { key: "chapters", label: "正文阅读", icon: ReadOutlined },
  { key: "review", label: "审校报告", icon: CheckCircleOutlined },
];

// 阶段顺序（用于自动切换）
const tabOrder = [
  "topic",
  "world",
  "characters",
  "outline",
  "scene",
  "metadata",
  "chapters",
  "review",
];
const tabToStage: Record<string, string> = {
  topic: "topic",
  world: "world",
  characters: "character",
  outline: "outline",
  scene: "scene",
  metadata: "metadata",
  chapters: "draft",
  review: "review",
};
const activeBackendStage = computed(() => tabToStage[activeTab.value] ?? null);
const currentStageStatus = computed(() => {
  const stage = activeBackendStage.value;
  if (!stage) return null;
  return (
    store.pipelineStatus?.stages?.find((item) => item.stage === stage) ?? null
  );
});
const isCurrentStageWaitingConfirm = computed(() => {
  const stage = activeBackendStage.value;
  if (!stage) return false;
  const stageStatus = currentStageStatus.value?.status;
  // 该阶段本身是 waiting_confirm，或流水线处于 confirming 状态
  return (
    stageStatus === "waiting_confirm" ||
    (store.pipelineStatus?.status === "confirming" &&
      store.pipelineStatus?.current_stage === stage)
  );
});
const shouldShowStageConfirm = computed(
  () => activeTab.value !== "overview" && isCurrentStageWaitingConfirm.value,
);
const canApproveCurrentStage = computed(() => shouldShowStageConfirm.value);
const approveButtonTitle = computed(() =>
  canApproveCurrentStage.value ? "采用当前阶段内容" : "当前阶段不在待确认状态",
);
const stageConfirmName = computed(
  () =>
    stageNames[activeBackendStage.value ?? ""] ||
    stageNames[activeTab.value] ||
    "",
);
const stageConfirmDescription = computed(() => {
  if (activeTab.value === "topic") {
    return "请选择一个方案采用，或提交反馈后重新生成选题方案。";
  }
  return "请审阅当前阶段内容，确认采用、提交反馈或重新生成。";
});

// 大纲表格
const outlineChapters = computed(() => store.outline?.chapters || []);
// 总章节数：优先用项目参数（生成目标），其次 outline 的 total_chapters，最后兜底当前章节数
const outlineTotalChapters = computed(() => {
  const fromProject = (store.currentProject as any)?.target_chapters;
  if (fromProject && fromProject > 0) return fromProject;
  const fromOutline = store.outline?.total_chapters;
  if (fromOutline && fromOutline > 0) return fromOutline;
  return outlineChapters.value.length || 0;
});
const outlineGeneratedCount = computed(() => outlineChapters.value.length);
const outlinePagedChapters = computed(() => {
  const start = (outlinePage.value - 1) * outlinePageSize;
  return outlineChapters.value.slice(start, start + outlinePageSize);
});
const outlineColumns = [
  { title: "序号", key: "index", width: 60 },
  { title: "章节标题", dataIndex: "title", key: "title", ellipsis: true },
  {
    title: "核心事件",
    dataIndex: "core_event",
    key: "core_event",
    ellipsis: true,
  },
  {
    title: "出场角色",
    dataIndex: "characters_present",
    key: "characters_present",
    width: 120,
  },
  { title: "操作", key: "action", width: 140 },
];

function openOutlineDetail(chapter: any) {
  outlineDrawerChapter.value = chapter;
  outlineDrawerVisible.value = true;
}

function closeOutlineDetail() {
  outlineDrawerVisible.value = false;
  outlineDrawerChapter.value = null;
}

async function deleteOutlineChapter(index: number) {
  const realIndex = (outlinePage.value - 1) * outlinePageSize + index;
  if (!store.outline) return;
  store.outline.chapters.splice(realIndex, 1);
  // total_chapters 保持不变（代表生成目标，不是当前数量）
  // 持久化到后端
  try {
    const { updateOutline } = await import("@/api");
    await updateOutline(projectId.value, store.outline);
  } catch {
    message.error("删除失败");
  }
}

async function deleteAllOutlineChapters() {
  if (!store.outline || outlineChapters.value.length === 0) return;
  // 保留 total_chapters 作为生成目标
  store.outline.chapters = [];
  // 持久化到后端
  try {
    const { updateOutline } = await import("@/api");
    await updateOutline(projectId.value, store.outline);
    message.success("已清空全部大纲");
  } catch {
    message.error("清空失败");
  }
}

async function handleOutlineBatchGenerate() {
  const maxRemaining = outlineTotalChapters.value - outlineGeneratedCount.value;
  if (maxRemaining <= 0) {
    message.info("大纲已全部生成");
    return;
  }
  outlineBatchDialogVisible.value = true;
}

async function confirmOutlineBatchGenerate() {
  const maxRemaining = outlineTotalChapters.value - outlineGeneratedCount.value;
  const batchSize = Math.min(outlineBatchSize.value, maxRemaining);
  if (batchSize < 1) {
    message.warning("请输入有效的章节数");
    return;
  }
  outlineBatchDialogVisible.value = false;
  stageActionLoading.value = true;
  stageActionText.value = `正在生成第 ${outlineGeneratedCount.value + 1}-${outlineGeneratedCount.value + batchSize} 章大纲...`;
  try {
    const task = await taskPoller.submitTask(() =>
      store.generateOutlineBatch(projectId.value, batchSize),
    );
    if (task.status === "failed") throw new Error(task.error || "大纲生成失败");
    if (task.status === "cancelled") throw new Error("大纲生成已取消");
    await handleTaskComplete("outline");
    message.success("大纲生成完成");
  } catch (error: any) {
    message.error(error.message || "大纲生成失败");
  } finally {
    stageActionLoading.value = false;
    stageActionText.value = "";
  }
}

function onTabChange(key: string | number) {
  const tabKey = String(key);
  if (tabKey === "overview") {
    router.push(`/projects/${projectId.value}`);
  } else {
    router.push(`/projects/${projectId.value}/${tabKey}`);
  }
}

// 加载数据
onMounted(async () => {
  await store.fetchProject(projectId.value);
  await store.fetchPipelineStatus(projectId.value);
  const activeTask = await store.fetchActiveTask(projectId.value);
  if (
    activeTask?.task_id &&
    ["pending", "running"].includes(activeTask.status)
  ) {
    taskPoller.activeTask.value = activeTask;
    void taskPoller
      .pollTask(activeTask.task_id)
      .then((task) =>
        handleTaskComplete(task.stage || activeBackendStage.value || ""),
      )
      .catch(() => undefined);
  }
});

watch(taskPoller.activeTask, (task) => {
  store.setActiveTask(task);
});

// 根据 tab 加载对应数据
watch(
  [activeTab, currentChapterNum],
  async ([tab, chapterNum]) => {
    const id = projectId.value;
    switch (tab) {
      case "topic":
        await store.fetchTopic(id);
        break;
      case "world":
        await store.fetchWorld(id);
        break;
      case "characters":
        await store.fetchCharacters(id);
        break;
      case "outline":
        await store.fetchOutline(id);
        break;
      case "scene":
        await store.fetchOutline(id);
        // 加载所有章节的场景数据
        if (store.outline?.chapters) {
          for (const ch of store.outline.chapters) {
            await loadSceneData(ch.chapter_number);
          }
        }
        break;
      case "metadata":
        await store.fetchMetadata(id);
        break;
      case "chapters":
        await store.fetchChapter(id, chapterNum);
        break;
      case "review":
        await store.fetchReview(id);
        break;
    }
  },
  { immediate: true },
);

// 章节导航
function prevChapter() {
  if (currentChapterNum.value > 1) {
    router.push(
      `/projects/${projectId.value}/chapters/${currentChapterNum.value - 1}`,
    );
  }
}

function nextChapter() {
  const total = store.outline?.total_chapters || 999;
  if (currentChapterNum.value < total) {
    router.push(
      `/projects/${projectId.value}/chapters/${currentChapterNum.value + 1}`,
    );
  }
}

// 启动流水线
async function handleStartPipeline() {
  if (stageActionLoading.value) return;
  stageActionLoading.value = true;
  stageActionText.value = "正在启动生成流水线...";
  try {
    await store.startPipeline(projectId.value);
    message.success("流水线已启动！");
  } catch (error: any) {
    message.error(error.message || "启动失败");
  } finally {
    stageActionLoading.value = false;
    stageActionText.value = "";
  }
}

async function loadStageData(stage: string) {
  switch (stage) {
    case "topic":
      await store.fetchTopic(projectId.value);
      break;
    case "world":
      await store.fetchWorld(projectId.value);
      break;
    case "character":
      await store.fetchCharacters(projectId.value);
      break;
    case "outline":
      await store.fetchOutline(projectId.value);
      break;
    case "scene":
      await store.fetchOutline(projectId.value);
      if (store.outline?.chapters) {
        for (const ch of store.outline.chapters) {
          await loadSceneData(ch.chapter_number);
        }
      }
      break;
    case "metadata":
      await store.fetchMetadata(projectId.value);
      break;
    case "draft":
      await store.fetchChapter(projectId.value, 1);
      break;
    case "review":
      await store.fetchReview(projectId.value);
      break;
  }
}

async function handleTaskComplete(stage: string) {
  await store.fetchPipelineStatus(projectId.value);
  if (stage) await loadStageData(stage);
}

function getNextTabKey(tab: string): string | null {
  const currentIdx = tabOrder.indexOf(tab);
  if (currentIdx < 0 || currentIdx >= tabOrder.length - 1) return null;
  return tabOrder[currentIdx + 1];
}

async function runStageInternal(stage: string, feedback?: string) {
  const task = await taskPoller.submitTask(() =>
    store.runStage(projectId.value, stage, feedback),
  );
  if (task.status === "failed") throw new Error(task.error || "阶段生成失败");
  if (task.status === "cancelled") throw new Error("阶段生成已取消");
  await handleTaskComplete(stage);
}

// 运行阶段
async function handleRunStage(stage: string) {
  if (stageActionLoading.value || taskLoading.value) return;
  stageActionLoading.value = true;
  stageActionText.value = `正在生成${stageNames[stage] || "当前阶段"}...`;
  try {
    await runStageInternal(stage);
    message.success("生成完成");
  } catch (error: any) {
    message.error(error.message || "生成失败");
  } finally {
    stageActionLoading.value = false;
    stageActionText.value = "";
  }
}

// 阶段确认
async function handleStageConfirm(action: ConfirmAction, feedback?: string) {
  const stage = activeBackendStage.value;
  if (!stage || stageActionLoading.value) return;
  if (action === "approve" && !canApproveCurrentStage.value) {
    message.warning("当前阶段不在待确认状态，暂不能采用");
    return;
  }

  stageActionLoading.value = true;
  stageActionText.value =
    action === "regenerate"
      ? `正在重新生成${stageNames[stage]}...`
      : action === "edit"
        ? `正在根据反馈重新生成${stageNames[stage]}...`
        : "正在提交阶段操作...";
  try {
    if (action === "approve") {
      await store.confirmStage(projectId.value, action, stage, feedback);
      message.success("已采用");
      const nextTab = getNextTabKey(activeTab.value);
      if (nextTab) {
        const nextStage = tabToStage[nextTab];
        router.push(`/projects/${projectId.value}/${nextTab}`);
        stageActionText.value = `正在生成${stageNames[nextStage]}...`;
        await runStageInternal(nextStage);
      }
    } else if (action === "edit") {
      // 编辑反馈：先 confirm(edit) 设 idle，再 runStage 带 feedback
      await store.confirmStage(projectId.value, action, stage, feedback);
      await runStageInternal(stage, feedback);
      message.success("根据反馈重新生成完成");
    } else if (action === "regenerate") {
      await store.confirmStage(projectId.value, action, stage);
      await runStageInternal(stage);
      message.success("重新生成完成");
    }
  } catch (error: any) {
    message.error(error.message || "操作失败");
  } finally {
    stageActionLoading.value = false;
    stageActionText.value = "";
  }
}

// 选题采用处理
async function handleTopicSelect(topicId: string) {
  if (stageActionLoading.value) return;
  stageActionLoading.value = true;
  stageActionText.value = "正在保存选题选择...";
  try {
    const nextPlans = store.topicPlans.map((t) => ({
      ...t,
      selected: t.id === topicId,
    }));
    store.topicPlans = nextPlans;
    const { updateTopic } = await import("@/api");
    await Promise.all(
      nextPlans.map((topic) => updateTopic(projectId.value, topic)),
    );
  } catch (error: any) {
    message.error(error.message || "保存选题失败");
    stageActionLoading.value = false;
    stageActionText.value = "";
    return;
  }
  stageActionLoading.value = false;
  stageActionText.value = "";
  await handleStageConfirm("approve");
}

// 选题更新
function onTopicUpdate(data: any) {
  store.topicPlans = store.topicPlans.map((t) =>
    t.id === data.id ? { ...t, ...data } : t,
  );
}

// 世界观更新
function onWorldUpdate(data: any) {
  store.worldSetting = { ...store.worldSetting, ...data };
}

// 角色更新
function onCharacterUpdate(data: any) {
  store.characters = store.characters.map((c) =>
    c.id === data.id ? { ...c, ...data } : c,
  );
}

// 角色删除
async function onCharacterDelete(id: string) {
  try {
    const { updateCharacters } = await import("@/api");
    const remaining = store.characters.filter((c) => c.id !== id);
    await updateCharacters(projectId.value, remaining);
    store.characters = remaining;
    message.success("角色已删除");
  } catch {
    message.error("删除失败");
  }
}

// 大纲更新
function onOutlineUpdate(data: any) {
  store.outline = { ...store.outline, ...data };
}

// 场景数据缓存
const sceneCache = ref<Record<number, any[]>>({});

function getSceneData(chNum: number): any[] {
  return sceneCache.value[chNum] || [];
}

async function loadSceneData(chNum: number) {
  try {
    const { getScene } = await import("@/api");
    const res = await getScene(projectId.value, chNum);
    const data = res.data.data ?? res.data;
    sceneCache.value[chNum] = Array.isArray(data) ? data : data?.scenes || [];
  } catch {
    sceneCache.value[chNum] = [];
  }
}

async function onSceneChapterChange(key: any) {
  if (key) {
    const chNum = Number(key);
    if (!sceneCache.value[chNum]) {
      await loadSceneData(chNum);
    }
  }
}

// 章节更新
function onChapterUpdate(data: any) {
  store.currentChapter = { ...store.currentChapter, ...data };
}

// 元数据更新
async function onMetadataUpdate(data: Partial<BookMetadata>) {
  try {
    await store.updateMetadata(projectId.value, data);
    message.success("元数据已更新");
  } catch {
    message.error("更新失败");
  }
}

// 元数据重新生成
async function onMetadataRegenerate() {
  try {
    await store.regenerateMetadata(projectId.value);
    message.success("元数据已重新生成");
  } catch {
    message.error("重新生成失败");
  }
}

// 元数据确认
function onMetadataConfirm() {
  handleStageConfirm("approve");
}

// 操作日志（模拟数据，后续可接入真实日志）
const operationLogs = ref([
  { time: "10:30", action: "项目创建完成", status: "done" as const },
]);

const activeTask = computed(
  () => taskPoller.activeTask.value || store.activeTask,
);
const hasTaskStatus = computed(() => !!activeTask.value?.task_id);
const taskStatusColor = computed(() => {
  const status = activeTask.value?.status;
  if (status === "running" || status === "pending") return "blue";
  if (status === "success") return "green";
  if (status === "failed") return "red";
  if (status === "cancelled") return "default";
  return "default";
});
const activeTaskStageName = computed(
  () =>
    stageNames[activeTask.value?.stage || ""] ||
    activeTask.value?.stage ||
    "未知阶段",
);
const activeTaskProgress = computed(
  () => activeTask.value?.progress?.percent ?? 0,
);

async function cancelActiveTask() {
  try {
    await taskPoller.cancelTask();
    await store.fetchActiveTask(projectId.value);
    message.info("取消请求已提交");
  } catch (error: any) {
    message.error(error.message || "取消失败");
  }
}

async function retryActiveTask() {
  const stage = activeTask.value?.stage;
  if (!stage) return;
  await handleRunStage(stage);
}

// 组件 ref（用于触发编辑模式）
const worldPanelRef = ref<InstanceType<typeof WorldPanel> | null>(null);
const outlineEditorRef = ref<InstanceType<typeof OutlineEditor> | null>(null);
</script>

<template>
  <AppLayout>
    <div class="project-detail" v-if="store.currentProject">
      <!-- 顶部 -->
      <div class="detail-header">
        <Space align="center">
          <Button @click="router.push('/')">
            <ArrowLeftOutlined /> 返回
          </Button>
          <Title :level="3" style="margin: 0">
            {{ store.currentProject.title }}
          </Title>
          <Tag
            :color="
              store.currentProject.status === 'completed' ? 'green' : 'blue'
            "
          >
            {{ store.currentProject.status }}
          </Tag>
        </Space>

        <Button
          v-if="store.currentProject.status === 'draft'"
          type="primary"
          @click="handleStartPipeline"
          :loading="globalLoading"
        >
          <PlayCircleOutlined /> 启动生成流水线
        </Button>
      </div>

      <!-- 流水线进度 -->
      <Card class="pipeline-card" size="small">
        <PipelineProgress :status="store.pipelineStatus" />
      </Card>

      <!-- 横向 Tab 导航 -->
      <Tabs :active-key="activeTab" @change="onTabChange" class="detail-tabs">
        <TabPane v-for="tab in tabItems" :key="tab.key" :tab="tab.label" />
      </Tabs>

      <!-- 主体区域：内容 + 右侧面板 -->
      <div class="detail-body">
        <!-- 内容区 -->
        <div class="detail-content">
          <Spin
            :spinning="globalLoading"
            :tip="loadingTip"
            class="content-spin"
          >
            <!-- 概览 -->
            <template v-if="activeTab === 'overview'">
              <ProjectOverview
                :project="store.currentProject"
                @next="onTabChange('topic')"
              />
            </template>

            <!-- 选题方案 -->
            <template v-if="activeTab === 'topic'">
              <TopicSection
                :project-id="projectId"
                :topic-plans="store.topicPlans"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :loading-tip="loadingTip"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                :stage-action-loading="stageActionLoading"
                @generate="handleRunStage('topic')"
                @select="handleTopicSelect"
                @update="onTopicUpdate"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 世界观 -->
            <template v-if="activeTab === 'world'">
              <!-- 顶部操作栏 -->
              <div class="stage-top-bar">
                <span class="stage-top-title"
                  ><GlobalOutlined /> 世界观设定</span
                >
                <Space>
                  <Button
                    v-if="store.worldSetting"
                    class="stage-action-button btn-adopt"
                    :loading="stageActionLoading"
                    :disabled="!canApproveCurrentStage || stageActionLoading"
                    :title="approveButtonTitle"
                    @click="handleStageConfirm('approve')"
                  >
                    <CheckCircleOutlined /> 采用
                  </Button>
                  <Button
                    v-if="store.worldSetting && worldPanelRef?.editing"
                    class="stage-action-button btn-cancel"
                    @click="worldPanelRef?.cancelEdit()"
                  >
                    <CloseOutlined /> 取消
                  </Button>
                  <Button
                    v-if="store.worldSetting && !worldPanelRef?.editing"
                    class="stage-action-button btn-edit"
                    @click="worldPanelRef?.startEdit()"
                  >
                    <EditOutlined /> 编辑
                  </Button>
                  <Button
                    class="stage-action-button btn-generate"
                    type="primary"
                    :loading="globalLoading"
                    :disabled="taskLoading"
                    @click="handleRunStage('world')"
                  >
                    <BulbOutlined /> AI生成
                  </Button>
                </Space>
              </div>
              <!-- 空状态 -->
              <div v-if="!store.worldSetting" class="empty-framework">
                <div class="empty-card-placeholder">
                  <div class="empty-card-line title"></div>
                  <div class="empty-card-line"></div>
                  <div class="empty-card-line"></div>
                  <div class="empty-card-line short"></div>
                </div>
                <div class="empty-card-placeholder">
                  <div class="empty-card-line title"></div>
                  <div class="empty-card-line"></div>
                  <div class="empty-card-line short"></div>
                </div>
              </div>
              <!-- 有数据 -->
              <WorldPanel
                v-if="store.worldSetting"
                ref="worldPanelRef"
                :world="store.worldSetting"
                :loading="globalLoading"
                :project-id="projectId"
                :show-confirm="false"
                :hide-actions="true"
                @update="onWorldUpdate"
              />
              <StageConfirm
                v-if="shouldShowStageConfirm && store.worldSetting"
                class="stage-action-card"
                :stage-name="stageConfirmName"
                :loading="stageActionLoading"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 角色列表 -->
            <template v-if="activeTab === 'characters'">
              <CharacterSection
                :project-id="projectId"
                :characters="store.characters"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                :stage-action-loading="stageActionLoading"
                :can-approve-current-stage="canApproveCurrentStage"
                :approve-button-title="approveButtonTitle"
                @generate="handleRunStage('character')"
                @confirm="handleStageConfirm"
                @update="onCharacterUpdate"
                @delete="onCharacterDelete"
              />
            </template>

            <!-- 大纲编辑 -->
            <template v-if="activeTab === 'outline'">
              <OutlineSection
                v-model:outline-page="outlinePage"
                :project-id="projectId"
                :outline="store.outline"
                :outline-chapters="outlineChapters"
                :outline-paged-chapters="outlinePagedChapters"
                :outline-page-size="outlinePageSize"
                :outline-generated-count="outlineGeneratedCount"
                :outline-total-chapters="outlineTotalChapters"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :stage-action-loading="stageActionLoading"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                @open-detail="openOutlineDetail"
                @delete-chapter="deleteOutlineChapter"
                @delete-all="deleteAllOutlineChapters"
                @generate-batch="handleOutlineBatchGenerate"
                @confirm="handleStageConfirm"
              />
            </template>

            <!-- 场景细纲 -->
            <template v-if="activeTab === 'scene'">
              <!-- 顶部操作栏 -->
              <div class="stage-top-bar">
                <span class="stage-top-title"><BlockOutlined /> 场景细纲</span>
                <Space>
                  <Button
                    class="stage-action-button btn-generate"
                    type="primary"
                    :loading="globalLoading"
                    :disabled="taskLoading"
                    @click="handleRunStage('scene')"
                  >
                    <SyncOutlined /> AI生成
                  </Button>
                </Space>
              </div>
              <!-- 空状态 -->
              <div
                v-if="!store.outline || outlineChapters.length === 0"
                class="empty-framework"
              >
                <Empty description="请先生成大纲" />
              </div>
              <!-- 场景列表 -->
              <template v-else>
                <Collapse accordion @change="onSceneChapterChange">
                  <Collapse.Panel
                    v-for="ch in outlineChapters"
                    :key="String(ch.chapter_number)"
                    :header="`第${ch.chapter_number}章 ${ch.title}`"
                  >
                    <div
                      v-if="
                        getSceneData(ch.chapter_number) &&
                        getSceneData(ch.chapter_number).length
                      "
                    >
                      <div
                        v-for="(scene, si) in getSceneData(ch.chapter_number)"
                        :key="si"
                        class="scene-card"
                      >
                        <p>
                          <strong>场景 {{ si + 1 }}：</strong
                          >{{ scene.location || "-" }}
                        </p>
                        <p v-if="scene.atmosphere">
                          <strong>氛围：</strong>{{ scene.atmosphere }}
                        </p>
                        <p v-if="scene.conflict">
                          <strong>冲突：</strong>{{ scene.conflict }}
                        </p>
                        <p v-if="scene.turning_point">
                          <strong>转折：</strong>{{ scene.turning_point }}
                        </p>
                        <p v-if="scene.emotion_start">
                          <strong>情绪：</strong>{{ scene.emotion_start }} →
                          {{ scene.emotion_end }}
                        </p>
                      </div>
                    </div>
                    <Empty v-else description="暂无场景细纲" />
                  </Collapse.Panel>
                </Collapse>
              </template>
            </template>

            <!-- 书籍元数据 -->
            <template v-if="activeTab === 'metadata'">
              <MetadataSection
                :project-id="projectId"
                :metadata="store.metadata"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :stage-action-loading="stageActionLoading"
                :can-approve-current-stage="canApproveCurrentStage"
                :approve-button-title="approveButtonTitle"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                @run-stage="handleRunStage('metadata')"
                @update="onMetadataUpdate"
                @regenerate="onMetadataRegenerate"
                @confirm-metadata="onMetadataConfirm"
                @confirm-stage="handleStageConfirm"
              />
            </template>

            <!-- 正文阅读 -->
            <template v-if="activeTab === 'chapters'">
              <ChapterSection
                :project-id="projectId"
                :current-chapter="store.currentChapter"
                :total-chapters="store.outline?.total_chapters"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :stage-action-loading="stageActionLoading"
                :can-approve-current-stage="canApproveCurrentStage"
                :approve-button-title="approveButtonTitle"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                @run-stage="handleRunStage('draft')"
                @prev="prevChapter"
                @next="nextChapter"
                @update="onChapterUpdate"
                @confirm-stage="handleStageConfirm"
              />
            </template>

            <!-- 审校报告 -->
            <template v-if="activeTab === 'review'">
              <ReviewSection
                :project-id="projectId"
                :review-report="store.reviewReport"
                :global-loading="globalLoading"
                :task-loading="taskLoading"
                :stage-action-loading="stageActionLoading"
                :can-approve-current-stage="canApproveCurrentStage"
                :approve-button-title="approveButtonTitle"
                :should-show-stage-confirm="shouldShowStageConfirm"
                :stage-confirm-name="stageConfirmName"
                @run-stage="handleRunStage('review')"
                @confirm-stage="handleStageConfirm"
              />
            </template>
          </Spin>
        </div>

        <!-- 右侧面板 -->
        <div class="right-panel">
          <!-- 当前阶段 -->
          <Card title="当前阶段" size="small" class="panel-card">
            <div class="current-stage-info">
              <Text strong>
                {{
                  stageNames[store.pipelineStatus?.current_stage || ""] ||
                  "待启动"
                }}
              </Text>
              <Tag
                :color="
                  store.pipelineStatus?.status === 'confirming'
                    ? 'orange'
                    : store.pipelineStatus?.status === 'running'
                      ? 'blue'
                      : 'default'
                "
                style="margin-left: 8px"
              >
                {{ store.pipelineStatus?.status || "idle" }}
              </Tag>
            </div>
          </Card>

          <!-- 任务状态 -->
          <Card
            title="任务状态"
            size="small"
            class="panel-card"
            style="margin-top: 12px"
          >
            <template v-if="hasTaskStatus && activeTask">
              <div class="task-status-card">
                <div class="task-status-header">
                  <Text strong>{{ activeTaskStageName }}</Text>
                  <Tag :color="taskStatusColor">{{ activeTask.status }}</Tag>
                </div>
                <Progress
                  :percent="activeTaskProgress"
                  size="small"
                  :status="
                    activeTask.status === 'failed'
                      ? 'exception'
                      : activeTask.status === 'success'
                        ? 'success'
                        : 'active'
                  "
                />
                <div class="task-status-text">{{ taskPoller.statusText }}</div>
                <div class="task-status-meta">
                  <span>耗时：{{ taskPoller.formatElapsed() }}</span>
                  <span v-if="activeTask.progress?.label">{{
                    activeTask.progress.label
                  }}</span>
                </div>
                <Space
                  v-if="
                    activeTask.status === 'pending' ||
                    activeTask.status === 'running'
                  "
                  style="margin-top: 10px"
                >
                  <Button size="small" danger @click="cancelActiveTask"
                    >取消任务</Button
                  >
                </Space>
                <Space
                  v-else-if="activeTask.status === 'failed'"
                  style="margin-top: 10px"
                >
                  <Button size="small" type="primary" @click="retryActiveTask"
                    >重试</Button
                  >
                </Space>
              </div>
            </template>
            <Text v-else type="secondary">暂无运行中的任务</Text>
          </Card>

          <!-- 操作日志 -->
          <Card
            title="操作日志"
            size="small"
            class="panel-card"
            style="margin-top: 12px"
          >
            <div class="logs-list">
              <div
                v-for="(log, index) in operationLogs"
                :key="index"
                class="log-item"
              >
                <span class="log-time">{{ log.time }}</span>
                <span class="log-action">{{ log.action }}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>

    <!-- 大纲章节详情弹窗 -->
    <Modal
      v-model:open="outlineDrawerVisible"
      :title="
        outlineDrawerChapter
          ? `第 ${outlineDrawerChapter.chapter_number} 章：${outlineDrawerChapter.title}`
          : '章节详情'
      "
      width="500px"
      :footer="null"
      :mask-closable="true"
      @cancel="closeOutlineDetail"
    >
      <div v-if="outlineDrawerChapter">
        <p>
          <strong>核心事件：</strong
          >{{ outlineDrawerChapter.core_event || "-" }}
        </p>
        <p>
          <strong>出场角色：</strong
          >{{
            Array.isArray(outlineDrawerChapter.characters_present)
              ? outlineDrawerChapter.characters_present.join("、")
              : outlineDrawerChapter.characters_present || "-"
          }}
        </p>
        <p>
          <strong>情绪定位：</strong
          >{{ outlineDrawerChapter.emotion_position || "-" }}
        </p>
        <p v-if="outlineDrawerChapter.emotion_arc">
          <strong>情绪弧线：</strong>{{ outlineDrawerChapter.emotion_arc }}
        </p>
        <p><strong>钩子：</strong>{{ outlineDrawerChapter.hook || "-" }}</p>
        <div
          v-if="
            outlineDrawerChapter.foreshadow_ops &&
            outlineDrawerChapter.foreshadow_ops.length
          "
          style="margin-top: 12px"
        >
          <p><strong>伏笔操作：</strong></p>
          <ul>
            <li
              v-for="(item, i) in outlineDrawerChapter.foreshadow_ops"
              :key="i"
            >
              {{ item }}
            </li>
          </ul>
        </div>
        <div
          v-if="
            outlineDrawerChapter.plot_lines_progress &&
            Object.keys(outlineDrawerChapter.plot_lines_progress).length
          "
          style="margin-top: 12px"
        >
          <p><strong>情节线推进：</strong></p>
          <ul>
            <li
              v-for="(val, key) in outlineDrawerChapter.plot_lines_progress"
              :key="key"
            >
              {{ key }}：{{ val }}
            </li>
          </ul>
        </div>
      </div>
    </Modal>

    <!-- 大纲分批生成弹窗 -->
    <Modal
      v-model:open="outlineBatchDialogVisible"
      title="生成大纲"
      @ok="confirmOutlineBatchGenerate"
      :confirm-loading="stageActionLoading"
    >
      <p>已生成 {{ outlineGeneratedCount }} / {{ outlineTotalChapters }} 章</p>
      <p>本次生成章节数：</p>
      <InputNumber
        v-model:value="outlineBatchSize"
        :min="1"
        :max="Math.max(1, outlineTotalChapters - outlineGeneratedCount)"
        style="width: 100%"
      />
      <p style="color: #999; font-size: 12px; margin-top: 8px">
        建议不要一次性生成太多，一是时间太长，二是调整起来麻烦。
      </p>
    </Modal>
  </AppLayout>
</template>

<style scoped>
@import "@/assets/styles/project-stages.css";

.project-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.pipeline-card {
  margin-bottom: 16px;
}

.detail-tabs {
  margin-bottom: 16px;
}

.detail-body {
  display: flex;
  gap: 16px;
}

.detail-content {
  flex: 1;
  min-width: 0;
}

.content-spin {
  display: block;
}

.content-spin :deep(.ant-spin-container) {
  min-height: 200px;
}

.stage-action-card {
  position: sticky;
  top: 80px;
  z-index: 5;
  margin-bottom: 4px;
}

.right-panel {
  width: 280px;
  flex-shrink: 0;
}

.panel-card {
  position: sticky;
  top: 16px;
}

.current-stage-info {
  display: flex;
  align-items: center;
}

.task-status-card {
  font-size: 13px;
}

.task-status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.task-status-text {
  color: #334155;
  margin-top: 6px;
}

.task-status-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: #64748b;
  margin-top: 6px;
}

.logs-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.log-time {
  color: #999;
  flex-shrink: 0;
}

.log-action {
  color: #333;
}

@media (max-width: 1024px) {
  .right-panel {
    display: none;
  }
}
</style>
