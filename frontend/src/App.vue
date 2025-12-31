
<script setup lang="ts">
import { ref } from 'vue'
import { sendChatMessage } from './api/chat'
import AudioButton from './components/AudioButton.vue'
import ChatBubble from './components/ChatBubble.vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  text: string

  // 后端返回的 unique_id
  audioId?: string

}



const messages = ref<ChatMessage[]>([])
const inputText = ref('')


async function sendMessage() {
  if (!inputText.value.trim()) return
  
  const userText = inputText.value

  //添加“用户消息”
  messages.value.push({
    role: 'user',
    text: inputText.value
  })


  //ai 占位消息
  const aiMessage:ChatMessage = {
    role: 'assistant',
    text: '（AI 思考中……）'

  }
  messages.value.push(aiMessage)

  //清空输入框
  inputText.value = ''

  try {
    const result = await sendChatMessage(userText)
    console.log(result)
    aiMessage.text = result.msg
    aiMessage.audioId = result.unique_id
    
  } catch (error) {
    aiMessage.text = '出错了，请稍后再试'
    console.error(error)
  }
  messages.value = [...messages.value] //在更新 AI 内容后，强制触发一次数组更新：Vue 对 数组替换 一定会重新渲染.但对 数组里对象属性的修改，有时不会触发列表更新


}

</script>

<template>
  <div style="padding: 20px">
    <h2>AI 聊天</h2>

    <!-- 聊天记录区域-->
    <div 
      style="
        border: 1px solid #ccc;
        height: 300px;
        overflow-y: auto;
        padding: 10px;
        margin-bottom: 10px;
      "
    >     

      <!--v-for：把数组里的每一条信息画出来-->
      <ChatBubble
        v-for="(msg, index) in messages"
        :key="index"
        :role="msg.role"
        :text="msg.text"
      >
        <AudioButton
          v-if="msg.role === 'assistant' && msg.audioId"
          :audio-id="msg.audioId"
        />
      </ChatBubble>

    </div>
    
    <!-- 输入框(v-model：让 inputText 和输入框双向绑定)-->
    <input
      v-model="inputText"
      placeholder="请输入内容"
      style="width: 300px; padding: 8px"
      @keyup.enter="sendMessage"
    />

    <button @click="sendMessage" style="margin-left: 10px">
      发送
    </button>
  </div>
</template>



