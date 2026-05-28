<script setup lang="ts">
import { Card, Descriptions, Tag, List, Empty } from 'ant-design-vue'
import {
  EnvironmentOutlined,
  ThunderboltOutlined,
  BankOutlined,
  ClusterOutlined,
} from '@ant-design/icons-vue'
import type { WorldSetting } from '@/types'

defineProps<{
  world: WorldSetting | null
  loading?: boolean
}>()
</script>

<template>
  <div class="world-panel">
    <Empty v-if="!world && !loading" description="世界观尚未生成" />
    <Spin :spinning="loading" v-else-if="loading">
      <div style="height: 200px" />
    </Spin>
    <template v-else-if="world">
      <Card title="🌍 世界观设定" class="world-card">
        <Descriptions :column="{ xs: 1, sm: 2 }" bordered size="small">
          <Descriptions.Item label="时代背景">
            <EnvironmentOutlined /> {{ world.era }}
          </Descriptions.Item>
          <Descriptions.Item label="地理环境">
            <BankOutlined /> {{ world.geography }}
          </Descriptions.Item>
          <Descriptions.Item label="力量体系" :span="2">
            <ThunderboltOutlined /> {{ world.power_system }}
          </Descriptions.Item>
          <Descriptions.Item label="社会结构" :span="2">
            <ClusterOutlined /> {{ world.social_structure }}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="📍 关键地点" class="world-card" style="margin-top: 16px">
        <List
          :data-source="world.key_locations"
          size="small"
          :render-item="(item: string) => h(List.Item, null, () => h(Tag, { color: 'blue' }, () => item))"
        />
      </Card>

      <Card title="📜 世界规则" class="world-card" style="margin-top: 16px">
        <List
          :data-source="world.rules"
          size="small"
          :render-item="(item: string) => h(List.Item, null, () => item)"
        />
      </Card>

      <Card title="⚠️ 约束条件" class="world-card" style="margin-top: 16px">
        <List
          :data-source="world.constraints"
          size="small"
          :render-item="(item: string) => h(List.Item, null, () => h(Tag, { color: 'orange' }, () => item))"
        />
      </Card>
    </template>
  </div>
</template>

<style scoped>
.world-panel {
  padding: 8px 0;
}

.world-card {
  margin-bottom: 0;
}
</style>
