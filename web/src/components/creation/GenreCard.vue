<script setup lang="ts">
import { computed } from 'vue'
import { Tag } from 'ant-design-vue'

const props = defineProps<{
  emoji: string
  name: string
  desc: string
  tags: string[]
  selected?: boolean
}>()

const emit = defineEmits<{
  click: []
}>()

const cardClass = computed(() => ({
  'genre-card': true,
  'genre-card--selected': props.selected,
}))
</script>

<template>
  <div :class="cardClass" @click="emit('click')">
    <div class="genre-card__icon">{{ emoji }}</div>
    <div class="genre-card__name">{{ name }}</div>
    <div class="genre-card__desc">{{ desc }}</div>
    <div class="genre-card__tags">
      <Tag v-for="tag in tags" :key="tag" class="genre-card__tag">{{ tag }}</Tag>
    </div>
    <div class="genre-card__check" v-if="selected">✓</div>
  </div>
</template>

<style scoped lang="less">
.genre-card {
  position: relative;
  background: #1a1a2e;
  border: 2px solid rgba(108, 92, 231, 0.15);
  border-radius: 12px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;
  user-select: none;

  &:hover {
    border-color: rgba(108, 92, 231, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(108, 92, 231, 0.15);
  }

  &--selected {
    border-color: #6c5ce7;
    background: rgba(108, 92, 231, 0.1);
    box-shadow: 0 0 20px rgba(108, 92, 231, 0.2);

    &:hover {
      border-color: #6c5ce7;
    }
  }

  &__icon {
    font-size: 36px;
    margin-bottom: 8px;
    line-height: 1;
  }

  &__name {
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 6px;
  }

  &__desc {
    font-size: 12px;
    color: #888;
    margin-bottom: 10px;
    line-height: 1.4;
  }

  &__tags {
    display: flex;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
  }

  &__tag {
    font-size: 11px;
    background: rgba(108, 92, 231, 0.15);
    border: 1px solid rgba(108, 92, 231, 0.3);
    color: #a29bfe;
    border-radius: 4px;
    padding: 0 6px;
    line-height: 20px;
  }

  &__check {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    background: #6c5ce7;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 14px;
    font-weight: bold;
  }
}
</style>
