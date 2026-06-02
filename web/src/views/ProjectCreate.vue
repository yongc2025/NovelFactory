<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Steps, Button, message } from "ant-design-vue";
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  RocketOutlined,
  ReloadOutlined,
} from "@ant-design/icons-vue";
import AppLayout from "@/components/layout/AppLayout.vue";
import ModeSelector from "@/components/creation/ModeSelector.vue";
import QuickStep1 from "@/components/creation/QuickStep1.vue";
import QuickStep2 from "@/components/creation/QuickStep2.vue";
import QuickStep3 from "@/components/creation/QuickStep3.vue";
import QuickStep4 from "@/components/creation/QuickStep4.vue";
import StepGender from "@/components/creation/StepGender.vue";
import StepGenre from "@/components/creation/StepGenre.vue";
import StepConflict from "@/components/creation/StepConflict.vue";
import StepPlatform from "@/components/creation/StepPlatform.vue";
import StepCharacter from "@/components/creation/StepCharacter.vue";
import StepRomance from "@/components/creation/StepRomance.vue";
import StepStyle from "@/components/creation/StepStyle.vue";
import StepReview from "@/components/creation/StepReview.vue";
import { useProjectStore } from "@/stores/project";
import {
  PLATFORM_CARDS,
  GENRE_CARDS,
  PROTAGONIST_TEMPLATES,
  HEROINE_TEMPLATES,
  ROMANCE_MODES,
} from "@/components/creation/presets";
import http from "@/api";
import type { CreateProjectParams } from "@/types";
import type { InspirationVersion } from "@/components/creation/QuickStep3.vue";

const router = useRouter();
const store = useProjectStore();
const submitting = ref(false);
const slideDirection = ref<"left" | "right">("left");

// ========== 模式选择 ==========
const selectedMode = ref<"quick" | "full" | null>(null);

// ========== 快速模式状态 ==========
const quickStep = ref(0);
const quickStep1Ref = ref<InstanceType<typeof QuickStep1> | null>(null);
const quickStep2Ref = ref<InstanceType<typeof QuickStep2> | null>(null);

const quick = reactive({
  // Step 1
  gender: null as "male" | "female" | "both" | null,
  genreId: null as string | null,
  // Step 2
  platformId: null as string | null,
  protagonistName: "",
  protagonistId: null as string | null,
  heroineId: null as string | null,
  romanceMode: null as string | null,
  storyBackground: "",
  styleText: "",
  referenceWorks: "",
  forbiddenElements: "",
  // Step 3
  inspirationVersions: [] as InspirationVersion[],
  inspirationGenerated: false,
  inspirationLoading: false,
});

// ========== 完整模式状态 ==========
const fullStep = ref(0);
const showAdvanced = ref(false);

const guided = reactive({
  gender: null as "male" | "female" | "both" | null,
  genreText: "",
  conflictText: "",
  platformCard: null as string | null,
  protagonistId: null as string | null,
  heroineId: null as string | null,
  characterText: "",
  romanceMode: null as string | null,
  styleText: "",
  generatedPremise: "",
});

const advancedForm = reactive({
  inspiration: "",
  platform: "番茄小说",
  word_count_target: 90000,
  genre: "",
  sub_genre: "",
});

const genreOptions = [
  {
    label: "古言",
    value: "古言",
    children: [
      "重生复仇",
      "宅斗权谋",
      "甜宠宫斗",
      "穿书逆袭",
      "种田经商",
      "古言仙侠",
    ],
  },
  {
    label: "现代",
    value: "现代",
    children: [
      "总裁豪门",
      "娱乐圈",
      "职场逆袭",
      "都市情感",
      "悬疑推理",
      "医疗/法律",
    ],
  },
  {
    label: "玄幻",
    value: "玄幻",
    children: [
      "系统流",
      "重生修仙",
      "异世大陆",
      "灵异悬疑",
      "末日生存",
      "魔法工业",
      "理工科穿越",
      "种田基建",
    ],
  },
  {
    label: "科幻",
    value: "科幻",
    children: [
      "星际",
      "赛博朋克",
      "时间循环",
      "末日废土",
      "硬科幻",
      "科技种田",
    ],
  },
  {
    label: "年代",
    value: "年代",
    children: ["70-80年代", "90年代经商", "年代重生"],
  },
  {
    label: "都市",
    value: "都市",
    children: ["校园", "职场", "家庭伦理", "情感婚姻", "学霸/科研"],
  },
  {
    label: "男频",
    value: "男频",
    children: [
      "玄幻修仙",
      "都市异能",
      "游戏竞技",
      "科幻机甲",
      "历史架空",
      "末日求生",
    ],
  },
  { label: "其他", value: "其他", children: ["自定义"] },
];

const currentSubGenres = computed(() => {
  const genre = genreOptions.find((g) => g.value === advancedForm.genre);
  return genre?.children.map((c) => ({ label: c, value: c })) || [];
});

// ========== localStorage 自动保存 ==========
const DRAFT_KEY = "novelfactory_project_draft";

interface DraftData {
  mode: "quick" | "full";
  step: number;
  data: Record<string, any>;
  timestamp: number;
}

function saveDraft() {
  const draft: DraftData = {
    mode: selectedMode.value || "quick",
    step: selectedMode.value === "quick" ? quickStep.value : fullStep.value,
    data: selectedMode.value === "quick" ? { ...quick } : { ...guided },
    timestamp: Date.now(),
  };
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  } catch {}
}

function loadDraft(): DraftData | null {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    const draft: DraftData = JSON.parse(raw);
    // 7 天过期
    if (Date.now() - draft.timestamp > 7 * 24 * 60 * 60 * 1000) {
      localStorage.removeItem(DRAFT_KEY);
      return null;
    }
    return draft;
  } catch {
    return null;
  }
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
}

function restoreDraft() {
  const draft = loadDraft();
  if (!draft) return;

  selectedMode.value = draft.mode;
  if (draft.mode === "quick") {
    quickStep.value = draft.step;
    Object.assign(quick, draft.data);
  } else {
    fullStep.value = draft.step;
    Object.assign(guided, draft.data);
  }
}

function resetAll() {
  clearDraft();
  selectedMode.value = null;
  quickStep.value = 0;
  fullStep.value = 0;
  Object.assign(quick, {
    gender: null,
    genreId: null,
    platformId: null,
    protagonistName: "",
    protagonistId: null,
    heroineId: null,
    romanceMode: null,
    storyBackground: "",
    styleText: "",
    referenceWorks: "",
    forbiddenElements: "",
    inspirationVersions: [],
    inspirationGenerated: false,
    inspirationLoading: false,
  });
  Object.assign(guided, {
    gender: null,
    genreText: "",
    conflictText: "",
    platformCard: null,
    protagonistId: null,
    heroineId: null,
    characterText: "",
    romanceMode: null,
    styleText: "",
    generatedPremise: "",
  });
}

// 自动保存（watch 深度监听）
watch(
  [
    () => ({ ...quick }),
    () => ({ ...guided }),
    selectedMode,
    quickStep,
    fullStep,
  ],
  () => {
    if (selectedMode.value) saveDraft();
  },
  { deep: true },
);

onMounted(() => {
  restoreDraft();
});

// ========== 快速模式步骤配置 ==========
const quickSteps = [
  { title: "快速定位" },
  { title: "补充信息" },
  { title: "AI 灵感" },
  { title: "确认创作" },
];

const quickCanProceed = computed(() => {
  switch (quickStep.value) {
    case 0:
      return !!quick.gender && !!quick.genreId;
    case 1:
      return !!quick.platformId;
    case 2:
      return (
        quick.inspirationGenerated &&
        !!quick.inspirationVersions.find((v) => v.selected)
      );
    case 3:
      return true;
    default:
      return false;
  }
});

// ========== 完整模式步骤配置 ==========
const steps = computed(() => {
  const base = [
    { title: "读者定位" },
    { title: "题材方向" },
    { title: "核心冲突" },
    { title: "平台篇幅" },
    { title: "角色设定" },
  ];

  if (guided.gender === "male" && guided.romanceMode !== "none") {
    base.push({ title: "感情线" });
    base.push({ title: "风格偏好" });
    base.push({ title: "确认创作" });
  } else {
    base.push({ title: "风格偏好" });
    base.push({ title: "确认创作" });
  }

  return base;
});

const canProceed = computed(() => {
  switch (fullStep.value) {
    case 0:
      return !!guided.gender;
    case 1:
      return guided.genreText.trim().length > 0;
    case 2:
      return guided.conflictText.trim().length > 0;
    case 3:
      return !!guided.platformCard;
    case 4:
      return true;
    case 5:
      return true;
    case 6:
      return true;
    default:
      return true;
  }
});

function isRomanceStep(stepIdx: number): boolean {
  return (
    guided.gender === "male" && guided.romanceMode !== "none" && stepIdx === 5
  );
}

function isStyleStep(stepIdx: number): boolean {
  if (guided.gender === "male" && guided.romanceMode !== "none")
    return stepIdx === 6;
  return stepIdx === 5;
}

function isReviewStep(stepIdx: number): boolean {
  return stepIdx === steps.value.length - 1;
}

// ========== 快速模式：AI 生成灵感 ==========
async function generateInspiration() {
  quick.inspirationLoading = true;

  const genreCard = GENRE_CARDS.find((c) => c.id === quick.genreId);
  const platformCard = PLATFORM_CARDS.find((c) => c.id === quick.platformId);
  const protagonist = PROTAGONIST_TEMPLATES.find(
    (t) => t.id === quick.protagonistId,
  );
  const heroine = HEROINE_TEMPLATES.find((t) => t.id === quick.heroineId);

  try {
    const res = await http.post("/generate/inspiration", {
      gender: quick.gender,
      genre_name: genreCard?.name || "",
      genre_desc: genreCard?.desc || "",
      protagonist_name: quick.protagonistName,
      protagonist_desc: protagonist
        ? protagonist.name + "（" + protagonist.desc + "）"
        : "",
      heroine_desc: heroine ? heroine.name + "（" + heroine.desc + "）" : "",
      romance_mode: quick.romanceMode || "",
      story_background: quick.storyBackground,
      style_text: quick.styleText,
      reference_works: quick.referenceWorks,
      forbidden_elements: quick.forbiddenElements,
      platform_name: platformCard?.name || "",
      target_words: platformCard?.targetWords || 120000,
      direction: "",
    });

    const data = res.data.data || res.data;
    quick.inspirationVersions = (data.versions || []).map(
      (v: any, i: number) => ({
        id: v.id || "v" + (i + 1),
        synopsis: v.synopsis || "",
        titles: v.titles || [],
        selected: i === 0,
      }),
    );

    if (quick.inspirationVersions.length === 0) {
      throw new Error("AI 未返回灵感");
    }

    quick.inspirationGenerated = true;
    message.success("灵感生成完成！");
  } catch (e: any) {
    message.error(
      e.response?.data?.detail || e.message || "灵感生成失败，请重试",
    );
  } finally {
    quick.inspirationLoading = false;
  }
}

async function regenerateInspiration() {
  quick.inspirationGenerated = false;
  quick.inspirationVersions = [];
  await generateInspiration();
}

async function regenerateWithDirection(direction: string) {
  quick.inspirationLoading = true;

  const genreCard = GENRE_CARDS.find((c) => c.id === quick.genreId);
  const platformCard = PLATFORM_CARDS.find((c) => c.id === quick.platformId);
  const protagonist = PROTAGONIST_TEMPLATES.find(
    (t) => t.id === quick.protagonistId,
  );
  const heroine = HEROINE_TEMPLATES.find((t) => t.id === quick.heroineId);

  try {
    const res = await http.post("/generate/inspiration", {
      gender: quick.gender,
      genre_name: genreCard?.name || "",
      genre_desc: genreCard?.desc || "",
      protagonist_name: quick.protagonistName,
      protagonist_desc: protagonist
        ? protagonist.name + "（" + protagonist.desc + "）"
        : "",
      heroine_desc: heroine ? heroine.name + "（" + heroine.desc + "）" : "",
      romance_mode: quick.romanceMode || "",
      story_background: quick.storyBackground,
      style_text: quick.styleText,
      reference_works: quick.referenceWorks,
      forbidden_elements: quick.forbiddenElements,
      platform_name: platformCard?.name || "",
      target_words: platformCard?.targetWords || 120000,
      direction: direction,
    });

    const data = res.data.data || res.data;
    quick.inspirationVersions = (data.versions || []).map(
      (v: any, i: number) => ({
        id: v.id || "v" + (i + 1),
        synopsis: v.synopsis || "",
        titles: v.titles || [],
        selected: i === 0,
      }),
    );

    quick.inspirationGenerated = true;
    message.success("按“" + direction + "”方向重新生成完成！");
  } catch (e: any) {
    message.error(e.response?.data?.detail || e.message || "重新生成失败");
  } finally {
    quick.inspirationLoading = false;
  }
}

function selectInspirationVersion(id: string) {
  quick.inspirationVersions.forEach((v) => {
    v.selected = v.id === id;
  });
}

function updateSynopsis(id: string, text: string) {
  const version = quick.inspirationVersions.find((v) => v.id === id);
  if (version) version.synopsis = text;
}

function updateTitle(id: string, index: number, text: string) {
  const version = quick.inspirationVersions.find((v) => v.id === id);
  if (version && version.titles[index] !== undefined) {
    version.titles[index] = text;
  }
}

// ========== 快速模式：构建 API 参数 ==========
function buildQuickParams(): CreateProjectParams {
  const genreCard = GENRE_CARDS.find((c) => c.id === quick.genreId);
  const platformCard = PLATFORM_CARDS.find((c) => c.id === quick.platformId);
  const selectedVersion = quick.inspirationVersions.find((v) => v.selected);

  const premise = selectedVersion?.synopsis || genreCard?.desc || "";
  const bookTitle = selectedVersion?.titles?.[0] || "";

  const params: CreateProjectParams = {
    premise,
    platforms: [platformCard?.platform || "番茄小说"],
    length_type: (platformCard?.lengthType as any) || "medium",
    target_words: platformCard?.targetWords || undefined,
    target_chapters: platformCard?.targetChapters || undefined,
    target_audience: quick.gender === "male" ? "male" : "female",
    book_title: bookTitle || undefined,
    book_synopsis: selectedVersion?.synopsis || undefined,
  };

  if (genreCard) {
    params.genre_major = genreCard.name;
  }

  if (quick.protagonistName) {
    params.protagonist_name = quick.protagonistName;
  }

  const protagonist = PROTAGONIST_TEMPLATES.find(
    (t) => t.id === quick.protagonistId,
  );
  if (protagonist) {
    params.protagonist_desc = `${protagonist.name}（${protagonist.desc}）`;
  }

  if (quick.romanceMode && quick.romanceMode !== "none") {
    params.has_romance = quick.romanceMode;
  }

  const heroine = HEROINE_TEMPLATES.find((t) => t.id === quick.heroineId);
  if (heroine) {
    params.romance_desc = `${heroine.name}（${heroine.desc}）`;
  }

  if (quick.storyBackground) {
    params.world_setting = quick.storyBackground;
  }

  if (quick.styleText) {
    params.tone = quick.styleText;
  }

  if (quick.referenceWorks) {
    params.reference_works = quick.referenceWorks;
  }

  if (quick.forbiddenElements) {
    params.forbidden_elements = quick.forbiddenElements
      .split(/[,，]/)
      .map((s) => s.trim())
      .filter(Boolean);
  }

  return params;
}

// ========== 完整模式：生成灵感描述 ==========
function generatePremise(): string {
  const parts: string[] = [];

  if (guided.conflictText) parts.push(guided.conflictText);

  const protagonist = PROTAGONIST_TEMPLATES.find(
    (t) => t.id === guided.protagonistId,
  );
  if (protagonist)
    parts.push(`主角性格：${protagonist.name}（${protagonist.desc}）`);

  if (guided.characterText) parts.push(`角色补充：${guided.characterText}`);

  const heroine = HEROINE_TEMPLATES.find((t) => t.id === guided.heroineId);
  if (
    heroine &&
    guided.gender === "male" &&
    guided.romanceMode &&
    guided.romanceMode !== "none"
  ) {
    parts.push(`女主性格：${heroine.name}（${heroine.desc}）`);
  }

  if (guided.genreText) parts.push(`题材方向：${guided.genreText}`);

  const platform = PLATFORM_CARDS.find((c) => c.id === guided.platformCard);
  if (platform)
    parts.push(
      `发布场景：${platform.name}，目标${(platform.targetWords / 10000).toFixed(0)}万字/${platform.targetChapters}章`,
    );

  if (guided.styleText) parts.push(`写作风格：${guided.styleText}`);

  return parts.join("\n");
}

function buildFullParams(): CreateProjectParams {
  const platform = PLATFORM_CARDS.find((c) => c.id === guided.platformCard);

  return {
    premise: guided.conflictText || guided.genreText,
    platforms: [platform?.platform || "番茄小说"],
    length_type: (platform?.lengthType as any) || "medium",
    genre_major:
      (guided.genreText.split("（")[0] || "").slice(0, 20) || undefined,
    target_words: platform?.targetWords || undefined,
    target_chapters: platform?.targetChapters || undefined,
    target_audience: guided.gender === "male" ? "male" : "female",
  };
}

// ========== 提交 ==========
async function handleSubmit() {
  submitting.value = true;
  try {
    const params =
      selectedMode.value === "quick"
        ? buildQuickParams()
        : showAdvanced.value
          ? {
              premise: advancedForm.inspiration,
              platforms: [advancedForm.platform],
              length_type: "medium" as const,
              genre_major: advancedForm.genre || undefined,
              genre_minor: advancedForm.sub_genre || undefined,
              target_words: advancedForm.word_count_target || undefined,
            }
          : buildFullParams();

    const project = await store.createProject(params);
    message.success("项目创建成功！");
    clearDraft();
    // 自动启动流水线
    try {
      await store.startPipeline(project.id);
    } catch {
      // 启动失败不影响创建，用户可在详情页手动启动
    }
    router.push(`/projects/${project.id}`);
  } catch (e: any) {
    console.error("创建项目失败:", e);
    message.error(e.response?.data?.detail || e.message || "创建失败，请重试");
  } finally {
    submitting.value = false;
  }
}

// ========== 快速模式步骤导航 ==========
function quickNext() {
  if (quickStep.value < 3) {
    slideDirection.value = "left";
    quickStep.value++;
  }
}

function quickPrev() {
  if (quickStep.value > 0) {
    slideDirection.value = "right";
    quickStep.value--;
  }
}

// ========== 完整模式步骤导航 ==========
function nextStep() {
  if (isReviewStep(fullStep.value + 1)) {
    guided.generatedPremise = generatePremise();
  }
  if (fullStep.value < steps.value.length - 1) {
    slideDirection.value = "left";
    fullStep.value++;
  }
}

function prevStep() {
  if (fullStep.value > 0) {
    slideDirection.value = "right";
    fullStep.value--;
  }
}

// ========== 完整模式切换 ==========
function switchToAdvanced() {
  showAdvanced.value = true;
  if (guided.conflictText) advancedForm.inspiration = guided.conflictText;
  const platform = PLATFORM_CARDS.find((c) => c.id === guided.platformCard);
  if (platform) {
    advancedForm.platform = platform.platform;
    advancedForm.word_count_target = platform.targetWords;
  }
}

function switchToGuided() {
  showAdvanced.value = false;
}

// ========== 模式选择处理 ==========
function handleModeSelect(mode: "quick" | "full") {
  selectedMode.value = mode;
  clearDraft();
}
</script>

<template>
  <AppLayout>
    <div class="project-create">
      <!-- 头部 -->
      <div class="create-header">
        <Button
          @click="selectedMode ? (selectedMode = null) : router.push('/')"
        >
          <ArrowLeftOutlined /> {{ selectedMode ? "返回选择" : "返回" }}
        </Button>
        <h2>✨ 新建小说项目</h2>
        <Button v-if="selectedMode" size="small" @click="resetAll">
          <ReloadOutlined /> 重新开始
        </Button>
      </div>

      <!-- 模式选择 -->
      <ModeSelector v-if="!selectedMode" @select="handleModeSelect" />

      <!-- 快速模式 -->
      <div v-else-if="selectedMode === 'quick'" class="quick-mode">
        <!-- 步骤条 -->
        <div class="steps-bar">
          <Steps :current="quickStep" size="small" class="custom-steps">
            <Steps.Step
              v-for="step in quickSteps"
              :key="step.title"
              :title="step.title"
            />
          </Steps>
        </div>

        <!-- 步骤内容 -->
        <div class="step-content">
          <Transition
            :name="slideDirection === 'left' ? 'slide-left' : 'slide-right'"
            mode="out-in"
          >
            <div :key="quickStep">
              <QuickStep1
                v-if="quickStep === 0"
                ref="quickStep1Ref"
                :gender="quick.gender"
                :genre-id="quick.genreId"
                @update:gender="quick.gender = $event"
                @update:genre-id="quick.genreId = $event"
              />

              <QuickStep2
                v-else-if="quickStep === 1"
                ref="quickStep2Ref"
                :gender="quick.gender || 'male'"
                :platform-id="quick.platformId"
                :protagonist-name="quick.protagonistName"
                :protagonist-id="quick.protagonistId"
                :heroine-id="quick.heroineId"
                :romance-mode="quick.romanceMode"
                :story-background="quick.storyBackground"
                :style-text="quick.styleText"
                :reference-works="quick.referenceWorks"
                :forbidden-elements="quick.forbiddenElements"
                @update:platform-id="quick.platformId = $event"
                @update:protagonist-name="quick.protagonistName = $event"
                @update:protagonist-id="quick.protagonistId = $event"
                @update:heroine-id="quick.heroineId = $event"
                @update:romance-mode="quick.romanceMode = $event"
                @update:story-background="quick.storyBackground = $event"
                @update:style-text="quick.styleText = $event"
                @update:reference-works="quick.referenceWorks = $event"
                @update:forbidden-elements="quick.forbiddenElements = $event"
              />

              <QuickStep3
                v-else-if="quickStep === 2"
                :versions="quick.inspirationVersions"
                :loading="quick.inspirationLoading"
                :generated="quick.inspirationGenerated"
                @generate="generateInspiration"
                @regenerate="regenerateInspiration"
                @select-version="selectInspirationVersion"
                @update-synopsis="updateSynopsis"
                @update-title="updateTitle"
                @regenerate-with-direction="regenerateWithDirection"
              />

              <QuickStep4
                v-else-if="quickStep === 3"
                :gender="quick.gender"
                :genre-id="quick.genreId"
                :platform-id="quick.platformId"
                :protagonist-name="quick.protagonistName"
                :protagonist-id="quick.protagonistId"
                :heroine-id="quick.heroineId"
                :romance-mode="quick.romanceMode"
                :story-background="quick.storyBackground"
                :style-text="quick.styleText"
                :reference-works="quick.referenceWorks"
                :forbidden-elements="quick.forbiddenElements"
                :selected-inspiration="
                  quick.inspirationVersions.find((v) => v.selected) || null
                "
                :loading="submitting"
                @submit="handleSubmit"
              />
            </div>
          </Transition>
        </div>

        <!-- 底部导航（Step 3 确认页不显示） -->
        <div v-if="quickStep < 3" class="step-actions">
          <Button v-if="quickStep > 0" @click="quickPrev">
            <ArrowLeftOutlined /> 上一步
          </Button>
          <div v-else></div>

          <Button
            type="primary"
            :disabled="!quickCanProceed"
            @click="quickNext"
          >
            下一步 <ArrowRightOutlined />
          </Button>
        </div>
      </div>

      <!-- 完整模式 -->
      <div v-else-if="selectedMode === 'full'" class="full-mode">
        <!-- 引导模式 -->
        <div v-if="!showAdvanced" class="guided-mode">
          <!-- 步骤条 -->
          <div class="steps-bar">
            <Steps :current="fullStep" size="small" class="custom-steps">
              <Steps.Step
                v-for="step in steps"
                :key="step.title"
                :title="step.title"
              />
            </Steps>
          </div>

          <!-- 步骤内容 -->
          <div class="step-content">
            <Transition
              :name="slideDirection === 'left' ? 'slide-left' : 'slide-right'"
              mode="out-in"
            >
              <div :key="fullStep">
                <StepGender
                  v-if="fullStep === 0"
                  :selected="guided.gender"
                  @select="guided.gender = $event"
                />

                <StepGenre
                  v-else-if="fullStep === 1"
                  v-model:free-text="guided.genreText"
                  :gender="guided.gender"
                />

                <StepConflict
                  v-else-if="fullStep === 2"
                  v-model:free-text="guided.conflictText"
                  :gender="guided.gender"
                  :genre-name="guided.genreText?.split('（')[0]"
                />

                <StepPlatform
                  v-else-if="fullStep === 3"
                  :selected-id="guided.platformCard"
                  @select="guided.platformCard = $event"
                />

                <StepCharacter
                  v-else-if="fullStep === 4"
                  :gender="guided.gender || 'male'"
                  :selected-protagonist="guided.protagonistId"
                  :selected-heroine="guided.heroineId"
                  :romance-mode="guided.romanceMode"
                  v-model:free-text="guided.characterText"
                  @select:protagonist="guided.protagonistId = $event"
                  @select:heroine="guided.heroineId = $event"
                />

                <StepRomance
                  v-else-if="isRomanceStep(fullStep)"
                  :selected="guided.romanceMode"
                  @select="guided.romanceMode = $event"
                />

                <StepStyle
                  v-else-if="isStyleStep(fullStep)"
                  v-model:free-text="guided.styleText"
                />

                <StepReview
                  v-else-if="isReviewStep(fullStep)"
                  :genre-text="guided.genreText"
                  :conflict-text="guided.conflictText"
                  :platform-card-id="guided.platformCard"
                  :character-text="guided.characterText"
                  :style-text="guided.styleText"
                  :generated-premise="guided.generatedPremise"
                  :loading="submitting"
                  @submit="handleSubmit"
                />
              </div>
            </Transition>
          </div>

          <!-- 底部导航 -->
          <div v-if="!isReviewStep(fullStep)" class="step-actions">
            <Button v-if="fullStep > 0" @click="prevStep">
              <ArrowLeftOutlined /> 上一步
            </Button>
            <div v-else></div>

            <div class="step-actions__right">
              <span class="skip-link" @click="switchToAdvanced">
                跳过，直接自定义 →
              </span>
              <Button type="primary" :disabled="!canProceed" @click="nextStep">
                下一步 <ArrowRightOutlined />
              </Button>
            </div>
          </div>
        </div>

        <!-- 高级模式 -->
        <div v-else class="advanced-mode">
          <div class="advanced-header">
            <span class="back-link" @click="switchToGuided"
              >← 返回引导模式</span
            >
          </div>

          <div class="advanced-form">
            <div class="form-section">
              <div class="form-label">
                灵感描述 <span class="required">*</span>
              </div>
              <a-textarea
                v-model:value="advancedForm.inspiration"
                :rows="4"
                placeholder="描述你的小说灵感，越详细越好..."
              />
            </div>

            <div class="form-row">
              <div class="form-section">
                <div class="form-label">题材大类</div>
                <a-select
                  v-model:value="advancedForm.genre"
                  :options="
                    genreOptions.map((g) => ({
                      label: g.label,
                      value: g.value,
                    }))
                  "
                  placeholder="选择题材大类"
                  style="width: 100%"
                  @change="advancedForm.sub_genre = ''"
                />
              </div>
              <div class="form-section" v-if="advancedForm.genre">
                <div class="form-label">细分题材</div>
                <a-select
                  v-model:value="advancedForm.sub_genre"
                  :options="currentSubGenres"
                  placeholder="选择细分题材"
                  allow-clear
                  style="width: 100%"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-section">
                <div class="form-label">发布平台</div>
                <a-select
                  v-model:value="advancedForm.platform"
                  style="width: 100%"
                >
                  <a-select-option value="番茄小说">番茄小说</a-select-option>
                  <a-select-option value="起点中文网"
                    >起点中文网</a-select-option
                  >
                  <a-select-option value="晋江文学城"
                    >晋江文学城</a-select-option
                  >
                  <a-select-option value="小红书">小红书</a-select-option>
                </a-select>
              </div>
              <div class="form-section">
                <div class="form-label">目标篇幅</div>
                <a-select
                  v-model:value="advancedForm.word_count_target"
                  style="width: 100%"
                >
                  <a-select-option :value="10000"
                    >短篇（1万字以内）</a-select-option
                  >
                  <a-select-option :value="90000"
                    >中篇（10-30万字）</a-select-option
                  >
                  <a-select-option :value="300000"
                    >长篇（30-100万字）</a-select-option
                  >
                  <a-select-option :value="1000000"
                    >超长篇（100万字以上）</a-select-option
                  >
                </a-select>
              </div>
            </div>

            <div class="advanced-actions">
              <Button @click="router.push('/')">取消</Button>
              <Button
                type="primary"
                :loading="submitting"
                :disabled="!advancedForm.inspiration.trim()"
                @click="handleSubmit"
              >
                <RocketOutlined /> 开始创作
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped lang="less">
.project-create {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}

.create-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;

  h2 {
    font-size: 24px;
    color: #e0e0e0;
    margin: 0;
    flex: 1;
  }
}

.steps-bar {
  margin-bottom: 32px;
}

.step-content {
  min-height: 400px;
  margin-bottom: 24px;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #2d2d44;

  &__right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.skip-link {
  font-size: 13px;
  color: #888;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #a29bfe;
  }
}

// 步骤过渡动画
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

// 高级模式
.advanced-mode {
  .advanced-header {
    margin-bottom: 24px;
  }

  .back-link {
    font-size: 13px;
    color: #a29bfe;
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }
}

.advanced-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;

  @media (max-width: 600px) {
    flex-direction: column;
  }
}

.form-label {
  font-size: 14px;
  color: #ccc;

  .required {
    color: #ff6b6b;
  }
}

.advanced-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

:deep(.ant-steps-item-title) {
  color: #888 !important;
}

:deep(.ant-steps-item-process .ant-steps-item-title) {
  color: #e0e0e0 !important;
}

:deep(.ant-steps-item-finish .ant-steps-item-title) {
  color: #6c5ce7 !important;
}

:deep(.ant-steps-item-finish .ant-steps-item-icon) {
  background: #6c5ce7;
  border-color: #6c5ce7;
}

:deep(.ant-steps-item-process .ant-steps-item-icon) {
  background: #6c5ce7;
  border-color: #6c5ce7;
}

:deep(.ant-input),
:deep(.ant-select-selector),
:deep(.ant-input-affix-wrapper) {
  background: #1a1a2e !important;
  border-color: rgba(108, 92, 231, 0.3) !important;
  color: #e0e0e0 !important;
}

:deep(.ant-input::placeholder) {
  color: #555 !important;
}
</style>
