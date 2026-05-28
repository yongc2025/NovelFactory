<script setup lang="ts">
import { ConfigProvider } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'

const theme = {
  token: {
    colorPrimary: '#1d39c4',
    colorLink: '#1d39c4',
    borderRadius: 6,
    fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
      'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
      'Noto Color Emoji'`,
  },
}
</script>

<template>
  <ConfigProvider :locale="zhCN" :theme="theme">
    <router-view />
  </ConfigProvider>
</template>

<style>
:root {
  --color-bg: #f5f5f5;
  --color-bg-elevated: #ffffff;
  --color-text: #1f1f1f;
  --color-text-secondary: #8c8c8c;
  --color-border: #d9d9d9;
  --color-primary: #1d39c4;
  --color-primary-hover: #2547cf;
}

[data-theme='dark'] {
  --color-bg: #141414;
  --color-bg-elevated: #1f1f1f;
  --color-text: #ffffffd9;
  --color-text-secondary: #ffffff73;
  --color-border: #424242;
  --color-primary: #3251c4;
  --color-primary-hover: #4162d4;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
}

#app {
  min-height: 100vh;
}
</style>
