<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Tabs,
  Input,
  Select,
  InputNumber,
  Button,
  Space,
  Form,
  Card,
  Tag,
  message,
  Spin,
} from 'ant-design-vue'
import { ArrowLeftOutlined, ArrowRightOutlined, RocketOutlined } from '@ant-design/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useProjectStore } from '@/stores/project'
import type { CreateProjectParams, CharacterPreset } from '@/types'

const router = useRouter()
const store = useProjectStore()
const activeTab = ref('1')
const submitting = ref(false)

// Tab 1: 基础信息
const form = reactive<CreateProjectParams>({
  inspiration: '',
  platform: '起点中文网',
  word_count_target: 300000,
  genre: '',
  sub_genre: '',
  character_presets: [],
  world_constraints: '',
  generation_strategy: undefined,
})

// 题材选项
const genreOptions = [
  { label: '玄幻', value: '玄幻', children: ['东方玄幻', '异界大陆', '高武世界', '远古神话'] },
  { label: '仙侠', value: '仙侠', children: ['修真文明', '洪荒封神', '古典仙侠', '幻想修仙'] },
  { label: '都市', value: '都市', children: ['都市生活', '都市异能', '商战职场', '青春校园'] },
  { label: '科幻', value: '科幻', children: ['星际文明', '时空穿梭', '未来世界', '超级科技'] },
  { label: '历史', value: '历史', children: ['架空历史', '秦汉三国', '唐宋元明', '清史民国'] },
  { label: '游戏', value: '游戏', children: ['虚拟网游', '游戏系统', '游戏异界', '电子竞技'] },
  { label: '悬疑', value: '悬疑', children: ['推理侦探', '恐怖惊悚', '悬疑探险', '诡秘悬疑'] },
]

const currentSubGenres = computed(() => {
  const genre = genreOptions.find((g) => g.value === form.genre)
  return genre?.children.map((c) => ({ label: c, value: c })) || []
})

// 平台选项
const platformOptions = [
  { label: '起点中文网', value: '起点中文网' },
  { label: '番茄小说', value: '番茄小说' },
  { label: '晋江文学城', value: '晋江文学城' },
  { label: '纵横中文网', value: '纵横中文网' },
  { label: '七猫小说', value: '七猫小说' },
  { label: '自定义', value: '自定义' },
]

// 篇幅选项
const wordCountOptions = [
  { label: '短篇（10万字以内）', value: 100000 },
  { label: '中篇（10-30万字）', value: 300000 },
  { label: '长篇（30-100万字）', value: 1000000 },
  { label: '超长篇（100万字以上）', value: 2000000 },
]

// Tab 3: 角色预设
const characterPresets = ref<CharacterPreset[]>([])

function addCharacter() {
  characterPresets.value.push({
    name: '',
    role: 'protagonist',
    traits: [],
    background: '',
  })
}

function removeCharacter(index: number) {
  characterPresets.value.splice(index, 1)
}

// 生成策略
const strategyForm = reactive({
  model: 'gpt-4o',
  temperature: 0.8,
  style: '网文风格',
  pacing: 'medium' as 'fast' | 'medium' | 'slow',
  tone: '轻松热血',
})

const canProceed = computed(() => {
  switch (activeTab.value) {
    case '1':
      return form.inspiration && form.platform && form.word_count_target
    case '2':
      return !!form.genre
    default:
      return true
  }
})

function nextTab() {
  const num = parseInt(activeTab.value)
  if (num < 5) activeTab.value = String(num + 1)
}

function prevTab() {
  const num = parseInt(activeTab.value)
  if (num > 1) activeTab.value = String(num - 1)
}

async function handleSubmit() {
  submitting.value = true
  try {
    const params: CreateProjectParams = {
      ...form,
      character_presets: characterPresets.value.length ? characterPresets.value : undefined,
      generation_strategy: strategyForm,
    }
    const project = await store.createProject(params)
    message.success('项目创建成功！')
    router.push(`/projects/${project.id}`)
  } catch {
    message.error('创建失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="project-create">
      <div class="create-header">
        <Button @click="router.push('/')">
          <ArrowLeftOutlined /> 返回
        </Button>
        <h2>✨ 新建小说项目</h2>
      </div>

      <Card class="create-card">
        <Tabs v-model:activeKey="activeTab" type="card">
          <!-- Tab 1: 基础信息 -->
          <Tabs.TabPane key="1" tab="📝 基础信息" :force-render="true">
            <Form layout="vertical" class="create-form">
              <Form.Item label="灵感描述" required>
                <Input.TextArea
                  v-model:value="form.inspiration"
                  :rows="4"
                  placeholder="描述你的小说灵感，越详细越好。例如：一个现代程序员穿越到修仙世界，利用编程思维破解阵法..."
                />
              </Form.Item>

              <Form.Item label="发布平台" required>
                <Select
                  v-model:value="form.platform"
                  :options="platformOptions"
                  placeholder="选择目标平台"
                />
              </Form.Item>

              <Form.Item label="目标篇幅" required>
                <Select
                  v-model:value="form.word_count_target"
                  :options="wordCountOptions"
                  placeholder="选择预期篇幅"
                />
              </Form.Item>
            </Form>
          </Tabs.TabPane>

          <!-- Tab 2: 题材选择 -->
          <Tabs.TabPane key="2" tab="🎭 题材选择" :force-render="true">
            <Form layout="vertical" class="create-form">
              <Form.Item label="题材大类" required>
                <Select
                  v-model:value="form.genre"
                  :options="genreOptions.map(g => ({ label: g.label, value: g.value }))"
                  placeholder="选择题材大类"
                  @change="form.sub_genre = ''"
                />
              </Form.Item>

              <Form.Item label="细分题材" v-if="form.genre">
                <Select
                  v-model:value="form.sub_genre"
                  :options="currentSubGenres"
                  placeholder="选择细分题材（可选）"
                  allow-clear
                />
              </Form.Item>

              <div class="genre-preview" v-if="form.genre">
                <p>
                  已选题材：
                  <Tag color="blue">{{ form.genre }}</Tag>
                  <Tag v-if="form.sub_genre" color="purple">{{ form.sub_genre }}</Tag>
                </p>
              </div>
            </Form>
          </Tabs.TabPane>

          <!-- Tab 3: 角色预设 -->
          <Tabs.TabPane key="3" tab="👥 角色预设" :force-render="true">
            <div class="character-presets">
              <p class="tab-hint">预设角色（可跳过，系统将自动生成）</p>

              <div
                v-for="(char, index) in characterPresets"
                :key="index"
                class="preset-item"
              >
                <Card size="small">
                  <Form layout="vertical">
                    <Space align="start" style="width: 100%">
                      <Form.Item label="姓名" style="width: 150px">
                        <Input v-model:value="char.name" placeholder="角色名" />
                      </Form.Item>
                      <Form.Item label="角色" style="width: 150px">
                        <Select v-model:value="char.role">
                          <Select.Option value="protagonist">主角</Select.Option>
                          <Select.Option value="antagonist">反派</Select.Option>
                          <Select.Option value="supporting">配角</Select.Option>
                        </Select>
                      </Form.Item>
                      <Form.Item label=" " style="margin-bottom: 0">
                        <Button danger @click="removeCharacter(index)">删除</Button>
                      </Form.Item>
                    </Space>
                    <Form.Item label="背景">
                      <Input.TextArea v-model:value="char.background" :rows="2" placeholder="简要描述角色背景" />
                    </Form.Item>
                  </Form>
                </Card>
              </div>

              <Button type="dashed" block @click="addCharacter" style="margin-top: 16px">
                + 添加角色
              </Button>
            </div>
          </Tabs.TabPane>

          <!-- Tab 4: 世界观约束 -->
          <Tabs.TabPane key="4" tab="🌍 世界观约束" :force-render="true">
            <Form layout="vertical" class="create-form">
              <p class="tab-hint">设定世界观约束条件（可跳过，系统将自动构建）</p>
              <Form.Item label="世界观约束">
                <Input.TextArea
                  v-model:value="form.world_constraints"
                  :rows="6"
                  placeholder="例如：&#10;- 故事发生在未来 2300 年的火星殖民地&#10;- 修炼体系基于量子力学&#10;- 不允许出现时间旅行&#10;- 社会分为五个阶层..."
                />
              </Form.Item>
            </Form>
          </Tabs.TabPane>

          <!-- Tab 5: 生成策略 -->
          <Tabs.TabPane key="5" tab="⚙️ 生成策略" :force-render="true">
            <Form layout="vertical" class="create-form">
              <p class="tab-hint">高级设置（可跳过，使用默认值）</p>

              <Form.Item label="AI 模型">
                <Select v-model:value="strategyForm.model">
                  <Select.Option value="gpt-4o">GPT-4o（推荐）</Select.Option>
                  <Select.Option value="gpt-4o-mini">GPT-4o Mini（快速）</Select.Option>
                  <Select.Option value="claude-3.5-sonnet">Claude 3.5 Sonnet</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="创造力（Temperature）">
                <InputNumber
                  v-model:value="strategyForm.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  style="width: 200px"
                />
              </Form.Item>

              <Form.Item label="叙事节奏">
                <Select v-model:value="strategyForm.pacing">
                  <Select.Option value="fast">快节奏</Select.Option>
                  <Select.Option value="medium">中等节奏</Select.Option>
                  <Select.Option value="slow">慢节奏</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="写作风格">
                <Input v-model:value="strategyForm.style" placeholder="如：网文风格、文学风格" />
              </Form.Item>

              <Form.Item label="基调">
                <Input v-model:value="strategyForm.tone" placeholder="如：轻松热血、黑暗严肃" />
              </Form.Item>
            </Form>
          </Tabs.TabPane>
        </Tabs>

        <div class="create-actions">
          <Space size="middle">
            <Button @click="router.push('/')">取消</Button>
            <Button v-if="activeTab !== '1'" @click="prevTab">
              <ArrowLeftOutlined /> 上一步
            </Button>
            <Button v-if="activeTab !== '5'" type="primary" :disabled="!canProceed" @click="nextTab">
              下一步 <ArrowRightOutlined />
            </Button>
            <Button
              v-if="activeTab === '5'"
              type="primary"
              size="large"
              :loading="submitting"
              @click="handleSubmit"
            >
              <RocketOutlined /> 开始生成
            </Button>
          </Space>
        </div>
      </Card>
    </div>
  </AppLayout>
</template>

<style scoped>
.project-create {
  max-width: 800px;
  margin: 0 auto;
}

.create-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.create-header h2 {
  margin: 0;
}

.create-card {
  min-height: 500px;
}

.create-form {
  max-width: 600px;
}

.tab-hint {
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.genre-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f6f8fa;
  border-radius: 6px;
}

.character-presets {
  max-width: 600px;
}

.preset-item {
  margin-bottom: 12px;
}

.create-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}
</style>
