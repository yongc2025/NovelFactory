<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  PlusOutlined,
  FolderOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons-vue'
import { Layout, Menu, Button, theme } from 'ant-design-vue'

const { Header, Sider, Content } = Layout

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const selectedKeys = computed(() => {
  const path = route.path
  if (path === '/') return ['dashboard']
  if (path === '/projects/create') return ['create']
  if (path.startsWith('/projects/')) return ['projects']
  return []
})

const menuItems = [
  { key: 'dashboard', icon: () => h(DashboardOutlined), label: '仪表盘' },
  { key: 'create', icon: () => h(PlusOutlined), label: '新建项目' },
  { key: 'projects', icon: () => h(FolderOutlined), label: '项目列表' },
]

function onMenuClick({ key }: { key: string }) {
  switch (key) {
    case 'dashboard':
      router.push('/')
      break
    case 'create':
      router.push('/projects/create')
      break
    case 'projects':
      router.push('/')
      break
  }
}
</script>

<template>
  <Layout class="app-layout">
    <Sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      breakpoint="lg"
      class="app-sider"
      :style="{ overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0 }"
    >
      <div class="logo">
        <span v-if="!collapsed" class="logo-text">📖 NovelFactory</span>
        <span v-else class="logo-icon">📖</span>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        :selected-keys="selectedKeys"
        :items="menuItems"
        @click="onMenuClick"
      />
    </Sider>
    <Layout :style="{ marginLeft: collapsed ? '80px' : '200px', transition: 'margin-left 0.2s' }">
      <Header class="app-header">
        <Button
          type="text"
          @click="collapsed = !collapsed"
          class="collapse-btn"
        >
          <template #icon>
            <MenuUnfoldOutlined v-if="collapsed" />
            <MenuFoldOutlined v-else />
          </template>
        </Button>
        <div class="header-right">
          <SettingOutlined class="header-icon" />
        </div>
      </Header>
      <Content class="app-content">
        <slot />
      </Content>
    </Layout>
  </Layout>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-sider {
  background: #001529;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.logo-icon {
  font-size: 24px;
}

.app-header {
  background: var(--color-bg-elevated);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.collapse-btn {
  font-size: 18px;
  width: 48px;
  height: 48px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.header-icon:hover {
  color: var(--color-primary);
}

.app-content {
  padding: 24px;
  min-height: calc(100vh - 64px);
  background: var(--color-bg);
}
</style>
