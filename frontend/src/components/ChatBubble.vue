<script setup lang="ts">
/**
 * 父组件传进来一条消息
 */
defineProps<{
  role: 'user' | 'assistant'
  text: string
}>()
</script>

<template>
  <!-- 外层：控制左右对齐 -->
  <div
    :class="[
      'bubble-wrapper',
      role === 'user' ? 'right' : 'left'
    ]"
  >
    <!-- 气泡本体 -->
    <div
      :class="[
        'bubble',
        role === 'user' ? 'user' : 'assistant'
      ]"
    >
      {{ text }}
      <!-- 关键：把子内容渲染出来 -->
      <slot />   
    </div>
  </div>
</template>

<style scoped>
/* 外层容器：控制整体对齐 */
.bubble-wrapper {
  display: flex;
  margin-bottom: 10px;
}

/* 用户消息 → 右边 */
.bubble-wrapper.right {
  justify-content: flex-end;
}

/* AI 消息 → 左边 */
.bubble-wrapper.left {
  justify-content: flex-start;
}

/* 气泡通用样式 */
.bubble {
  max-width: 60%;
  padding: 8px 12px;
  border-radius: 10px;
  word-break: break-word;
}

/* 用户气泡 */
.bubble.user {
  background-color: #95ec69;
}

/* AI 气泡 */
.bubble.assistant {
  background-color: #f1f1f1;
}
</style>
