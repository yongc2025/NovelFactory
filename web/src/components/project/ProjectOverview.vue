<script setup lang="ts">
import { Typography, Card, Button } from "ant-design-vue";
import type { Project } from "@/types";

const { Title } = Typography;

defineProps<{
  project: Project;
}>();

defineEmits<{
  (e: "next"): void;
}>();
</script>

<template>
  <Card title="项目信息" class="content-card">
    <p><strong>灵感：</strong>{{ project.inspiration }}</p>
    <p><strong>题材：</strong>{{ project.genre }}</p>
    <p>
      <strong>平台：</strong
      >{{ project.platforms?.join("、") || project.platform || "未设置" }}
    </p>
    <p>
      <strong>目标字数：</strong
      >{{
        (
          (project.target_words || project.word_count_target || 0) / 10000
        ).toFixed(0)
      }}万字
    </p>
    <p>
      <strong>每章字数：</strong
      >{{
        project.chapter_word_count || 3000
      }}字（实际字数以正文为准，允许±100字浮动）
    </p>
    <p>
      <strong>预计章节数：</strong
      >{{
        Math.floor(
          (project.target_words || 0) / (project.chapter_word_count || 3000),
        )
      }}章
    </p>
    <p>
      <strong>创建时间：</strong
      >{{ new Date(project.created_at).toLocaleString("zh-CN") }}
    </p>
    <p style="color: #999; font-size: 12px; margin-top: 8px">
      * 实际字数以选题方案确认的为准
    </p>
    <div style="text-align: center; margin-top: 24px">
      <Button type="primary" size="large" @click="$emit('next')">
        下一步：选题方案 →
      </Button>
    </div>
  </Card>
</template>

<style scoped>
.content-card {
  margin-bottom: 24px;
}
p {
  margin-bottom: 12px;
  line-height: 1.6;
}
</style>
