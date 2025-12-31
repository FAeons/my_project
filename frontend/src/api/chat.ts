import axios from 'axios'

/**
 * 向后端发送聊天内容
 * 等价于 Python 的 requests.post(...)
 */
export async function sendChatMessage(text: string) {
    const respose = await axios.post(
        "http://127.0.0.1:8000/chat", 
        {
            query: text
        },
        {
            timeout: 60000
        }   
    )
    return respose.data
}