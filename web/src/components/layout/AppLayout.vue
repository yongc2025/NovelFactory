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
import { Layout, Menu, Button } from 'ant-design-vue'

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
]

function onMenuClick({ key }: any) {
  switch (key) {
    case 'dashboard':
      router.push('/')
      break
    case 'create':
      router.push('/projects/create')
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
      :width="220"
      :collapsed-width="72"
    >
      <!-- Logo 区域 -->
      <div class="logo-area">
        <div class="logo-icon">📖</div>
        <transition name="fade">
          <div v-if="!collapsed" class="logo-text-group">
            <span class="logo-text">NovelFactory</span>
            <span class="logo-version">v1.0</span>
          </div>
        </transition>
      </div>

      <!-- 导航菜单 -->
      <div class="nav-section">
        <Menu
          theme="dark"
          mode="inline"
          :selected-keys="selectedKeys"
          :items="menuItems"
          @click="onMenuClick"
          class="nav-menu"
        />
      </div>

      <!-- 底部区域 -->
      <div class="sider-footer">
        <div class="footer-item" title="设置">
          <SettingOutlined class="footer-icon" />
          <transition name="fade">
            <span v-if="!collapsed" class="footer-label">设置</span>
          </transition>
        </div>
      </div>
    </Sider>

    <Layout class="main-layout" :class="{ 'main-layout--collapsed': collapsed }">
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
        <div class="header-title">
          <slot name="header" />
        </div>
      </Header>

      <Content class="app-content">
        <slot />
      </Content>
    </Layout>
  </Layout>
</template>

<style scoped lang="less">
@import '@/styles/design-tokens.less';

.app-layout {
  min-height: 100vh;
}

.app-sider {
  background: @color-bg-elevated !important;
  border-right: 1px solid @color-border;
  position: fixed !important;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  // 微光效果
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: linear-gradient(180deg, rgba(108, 92, 231, 0.05) 0%, transparent 100%);
    pointer-events: none;
  }
}

// Logo 区域
.logo-area {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: @space-sm;
  padding: 0 @space-md;
  border-bottom: 1px solid @color-border;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 28px;
  line-height: 1;
}

.logo-text-group {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-text {
  color: @color-text;
  font-size: @font-size-lg;
  font-weight: @font-weight-bold;
  white-space: nowrap;
  background: @gradient-primary;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-version {
  font-size: @font-size-xs;
  color: @color-text-tertiary;
  white-space: nowrap;
}

// 导航区域
.nav-section {
  flex: 1;
  padding: @space-md 0;
  overflow-y: auto;
}

.nav-menu {
  background: transparent !important;
  border-right: none !important;

  :deep(.ant-menu-item) {
    margin: 4px 8px;
    border-radius: @radius-md;
    height: 44px;
    line-height: 44px;
    transition: all @transition-fast;

    &:hover {
      background: @color-bg-hover !important;
    }

    &.ant-menu-item-selected {
      background: @color-primary-bg !important;
      color: @color-primary-light !important;

      &::after {
        display: none;
      }
    }
  }
}

// 底部区域
.sider-footer {
  padding: @space-md;
  border-top: 1px solid @color-border;
  flex-shrink: 0;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: @space-sm;
  padding: @space-sm @space-md;
  border-radius: @radius-md;
  cursor: pointer;
  transition: all @transition-fast;
  color: @color-text-secondary;

  &:hover {
    background: @color-bg-hover;
    color: @color-text;
  }
}

.footer-icon {
  font-size: 18px;
}

.footer-label {
  font-size: @font-size-sm;
  white-space: nowrap;
}

// 主布局
.main-layout {
  margin-left: 220px;
  transition: margin-left @transition-normal;

  &--collapsed {
    margin-left: 72px;
  }
}

// 顶部栏
.app-header {
  background: @color-bg-elevated !important;
  padding: 0 @space-lg;
  display: flex;
  align-items: center;
  gap: @space-md;
  border-bottom: 1px solid @color-border;
  height: 64px;
  line-height: 64px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.collapse-btn {
  font-size: 18px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: @color-text-secondary;
  border-radius: @radius-md;
  transition: all @transition-fast;

  &:hover {
    color: @color-text;
    background: @color-bg-hover;
  }
}

.header-title {
  flex: 1;
}

// 内容区
.app-content {
  padding: @space-lg;
  min-height: calc(100vh - 64px);
  background: @color-bg;
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity @transition-fast;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 响应式
@media (max-width: @screen-lg) {
  .main-layout {
    margin-left: 0 !important;
  }
}
</style>
