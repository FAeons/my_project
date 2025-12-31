<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { onUnmounted } from 'vue'

//防止组件卸载后音频还在播放，否则以后滚动 / 删除消息，会出 bug
onUnmounted(() => {
  audio.pause()
  audio.src = ''
})
/**
 * 父组件（App.vue）会传进来 audioId
 * 对应后端生成的 unique_id
 */
const props = defineProps<{
  audioId: string
}>()

/**
 * Audio 对象：浏览器自带的音频播放器
 * 它和 <audio> 标签是同一个东西
 */
const audio = new Audio()

/**
 * 当前是否正在播放
 */
const isPlaying = ref(false)

/**
 * 是否已经加载过音频
 * 避免每次点击都重新请求
 */
const isLoaded = ref(false)

/**
 * 点击按钮：播放 / 暂停
 */


//如何语音还未生成的时候点击播放按钮，提示“音还没生成好，请稍后再试”后，等语音合成好后，再点击播放按钮就再也无法播放了
async function togglePlay() {
  // 第一次播放时，才去请求后端
  if (!isLoaded.value) {
    audio.src = `http://localhost:8000/audio/${props.audioId}`
    isLoaded.value = true
  }

  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {
    try {
      await audio.play()
      isPlaying.value = true
    } catch (e) {
      alert('语音还没生成好，请稍后再试')
      console.error(e)
    }
  }
}

/**
 * 音频播放结束
 * 通知后端：可以删除 mp3 文件了
 */
audio.onended = async () => {
  isPlaying.value = false

  try {
    await axios.post(
      `http://localhost:8000/audio/${props.audioId}/played`
    )
  } catch (e) {
    console.error('通知后端删除音频失败', e)
  }
}
</script>

<template>
  <button @click="togglePlay" style="margin-top: 5px">
    {{ isPlaying ? '⏸ 暂停' : '▶ 播放语音' }}
  </button>
</template>
