<script setup lang="ts">
import { ConfigProvider } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'

const theme = {
  token: {
    colorPrimary: '#6C5CE7',
    colorLink: '#6C5CE7',
    colorSuccess: '#00B894',
    colorWarning: '#FDCB6E',
    colorError: '#FF7675',
    colorInfo: '#74B9FF',
    borderRadius: 8,
    fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif`,
    colorBgContainer: '#1A1A2E',
    colorBgElevated: '#1A1A2E',
    colorBgLayout: '#0F0F23',
    colorText: '#E2E8F0',
    colorTextSecondary: '#94A3B8',
    colorTextTertiary: '#64748B',
    colorBorder: '#2D2D44',
    colorBorderSecondary: '#3D3D5C',
    controlHeight: 36,
    wireframe: false,
  },
  algorithm: undefined, // 不使用内置暗色算法，用自定义 token
}
</script>

<template>
  <ConfigProvider :locale="zhCN" :theme="theme">
    <router-view />
  </ConfigProvider>
</template>

<style>
:root {
  --color-bg: #0F0F23;
  --color-bg-elevated: #1A1A2E;
  --color-bg-hover: #252542;
  --color-bg-active: #2D2D4E;
  --color-text: #E2E8F0;
  --color-text-secondary: #94A3B8;
  --color-text-tertiary: #64748B;
  --color-border: #2D2D44;
  --color-primary: #6C5CE7;
  --color-primary-light: #A29BFE;
  --color-primary-dark: #5A4BD1;
  --color-secondary: #00B894;
  --color-accent: #FD79A8;
  --color-success: #00B894;
  --color-warning: #FDCB6E;
  --color-error: #FF7675;
}
</style>
