# 算命先生陈玉楼聊天系统
一个基于AI的角色扮演聊天应用，以《鬼吹灯》中“陈玉楼（陈瞎子）”为原型，提供命理测算、风水咨询等功能的智能对话系统，支持语音交互与知识库查询。


## 项目概述
本项目是一款融合**AI对话、命理工具、风水知识库**的角色扮演聊天系统：
- 以“陈玉楼”（精通阴阳五行、紫微斗数的湘西卸岭魁首）为虚拟形象，与用户自然交流；
- 支持八字测算、姓名命理、风水布局等功能，结合知识库提供专业命理咨询；
- 具备语音合成、情绪识别、用户档案管理等辅助能力，提升交互体验。


## 技术栈
| 分类       | 技术选型                          |
|------------|-----------------------------------|
| 前端框架   | Vue 3、TypeScript、Vite           |
| 后端服务   | Python、FastAPI                   |
| AI核心     | LangChain、DeepSeek API（大模型） |
| 向量数据库 | Qdrant（知识库检索）              |
| 语音合成   | DashScope TTS                     |
| 数据库     | PostgreSQL（用户/数据存储）       |


## 功能特点
1. **角色扮演对话**：模拟陈玉楼的语气、口头禅（如“某乃卸岭魁首”），实现自然的命理主题聊天；
2. **命理工具集**：支持八字测算、姓名命理、风水布局查询，对接第三方命理API；
3. **语音交互**：将文字回复转为语音（陈玉楼风格），支持播放/暂停控制；
4. **知识库检索**：内置风水、命理相关知识库，支持网页/PDF内容导入扩展；
5. **用户管理**：记录用户提供的出生信息、偏好等，实现个性化咨询。


## 快速开始

### 前置依赖
- Python 3.12+、Node.js 17+
- PostgreSQL 数据库、Qdrant 向量数据库
- 对应API密钥（DeepSeek、DashScope等）


### 环境配置
在项目根目录创建 `.env` 文件，填入以下内容：
```env
# AI API配置
DEEPSEEK_API_KEY=你的DeepSeek密钥
DEEPSEEK_API_BASE=你的DeepSeek接口地址
YUANFENJU_API_KEY=你的缘分居命理API密钥

#TTL 配置
DASHSCOPE_API_BASE = https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_API_KEY = <your-dashscope-api-key>

# 数据库配置
DB_URL=postgresql://用户名:密码@localhost:5432/数据库名

# 向量数据库配置
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=你的Qdrant密钥
```


### 后端启动
1. 安装依赖：
```bash
pip install -r requirements.txt
```
2. 启动服务：
```bash
python server.py
```
服务默认运行在 `http://localhost:8000`


### 前端启动
1. 安装依赖：
```bash
npm install
```
2. 启动开发服务器：
```bash
npm run dev
```
前端默认运行在 `http://localhost:5173`


## 项目结构
```
├── frontend/ # 前端项目目录
│ ├── index.html # 前端入口HTML文件
│ ├── src/
│ │ ├── api/chat.ts # 聊天接口封装
│ │ ├── components/ # 组件
│ │ │ ├── AudioButton.vue # 语音播放按钮
│ │ │ └── ChatBubble.vue # 聊天气泡
│ │ ├── App.vue # 根组件
│ │ └── main.ts # 前端入口
│ └── package*.json # 前端依赖
├── local_qdrant/ # Qdrant 本地向量数据库（持久化风水知识）
├── .env # 环境变量配置（API keys 等）
├── Mytools.py # 自定义工具：search / bazi_cesuan / get_info_from_local_db
├── server.py # FastAPI 后端主程序
└── requirements.txt # Python 依赖列表
```


## 核心接口说明
| 接口地址                | 方法 | 功能描述                  |
|-------------------------|------|---------------------------|
| `/chat`                 | POST | 发送聊天消息，获取AI回复  |
| `/add_urls`             | POST | 导入网页内容到知识库      |
| `/add_pdfs`             | POST | 导入PDF文件到知识库       |
| `/audio/{audio_id}`     | GET  | 获取语音合成文件          |
| `/audio/{audio_id}/played` | POST | 标记语音已播放（清理文件） |


## 🔮 未来规划

- [ ] 前端界面改版，融入民国 / 湘西风格视觉设计，提升角色沉浸感。
- [ ] 新增手相 / 面相测算功能（上传图片解析）。
- [ ] 支持多语言交互（繁体中文），适配港澳台用户。
- [ ] 实现大模型调用缓存，降低 API 调用成本。
- [ ] 完善知识库，补充《葬经》《青囊经》等经典风水文献


## 注意事项
1. 语音合成需等待几秒处理时间，建议添加加载状态提示；
2. 命理测算依赖用户提供的准确出生信息（年月日时）；
3. 知识库内容需提前导入，否则风水查询功能可能无结果；
4. 开发环境中`__pycache__`目录是Python自动生成的缓存，无需提交到Git（可在`.gitignore`中添加`__pycache__/`）。


## 📄 许可证
MIT License


## 📞 联系方式
- 如有问题或建议，欢迎提Issue或PR！

```