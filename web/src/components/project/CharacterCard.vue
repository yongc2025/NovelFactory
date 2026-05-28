<script setup lang="ts">
import { Card, Tag, Avatar, Descriptions, List } from 'ant-design-vue'
import { UserOutlined } from '@ant-design/icons-vue'
import type { Character } from '@/types'

defineProps<{
  character: Character
}>()

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
</script>

<template>
  <Card class="character-card" hoverable>
    <template #title>
      <div class="char-title">
        <Avatar :size="40" :style="{ backgroundColor: roleColors[character.role] === 'blue' ? '#1d39c4' : roleColors[character.role] === 'red' ? '#cf1322' : '#389e0d' }">
          <template #icon><UserOutlined /></template>
        </Avatar>
        <div class="char-name-block">
          <span class="char-name">{{ character.name }}</span>
          <Tag :color="roleColors[character.role]">
            {{ roleLabels[character.role] }}
          </Tag>
        </div>
      </div>
    </template>

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
        :render-item="(rel: any) => h(List.Item, null, () => [
          h(Tag, { color: 'cyan' }, () => rel.target_name),
          h('span', null, ` ${rel.relation}：${rel.description}`),
        ])"
      />
    </div>
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
</style>
