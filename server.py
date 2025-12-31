from langchain.agents import create_agent
from fastapi import FastAPI,WebSocket,WebSocketDisconnect, Query,BackgroundTasks,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents.middleware import SummarizationMiddleware
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
from pydantic import BaseModel
from langgraph.checkpoint.postgres import PostgresSaver
from Mytools import *
import os
import uuid
import re
import asyncio
import psycopg
#from aliyun_tts import AliyunTTS
#import dashscope
from dashscope.audio.tts_v2 import *
load_dotenv()
# logging.basicConfig(level=logging.INFO)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"], #允许 OPTIONS / POST / GET
    allow_headers=["*"],
)

DB_URL = 'postgresql://postgres:20041019@localhost:5432/master_db'


class Master:
        def __init__(self):
            self.chatmodel = ChatOpenAI(
                model="deepseek-chat",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_API_BASE"),
                temperature=0.9,
                streaming=True,
            )
            #self.tts = AliyunTTS(os.getenv("ACCESS_KEY_ID"), os.getenv("ACCESS_KEY_SECRET"), os.getenv("APP_KEY"))    
            self.qingxu = "default"
            self.SYSTEMPL = """你是一个非常厉害的算命先生,你叫陈玉楼人称陈大师。
            以下是你的个人设定:
            1. 你精通阴阳五行，能够算命、紫薇斗数、姓名测算、占卜凶吉，看命运八字等。
            2. 你大约60岁左右，过去曾是湘西一带赫赫有名的土匪头子，后来因为盗墓被毒气所伤，眼睛失明，只能靠算命为生。
            3. 你的朋友有胡八一、雪莉杨、王胖子，他们都是非常有名的摸金校尉。
            5. 当用户问你问题的时候，你在回答的时候会偶尔加上下面的口头禅或混合一些你的经历。
            6. 你总是用简体中文来作答。
            7. 你从不说自己是一个人工智能助手或AI，而是以老夫、老朽等自称。
            以下是你可能用到的一些口头禅：
            1. “命里有时终须有，命里无时莫强求。”
            2. ”山重水复疑无路，柳暗花明又一村。”
            3. “金山竹影几千秋，云锁高飞水自流。”
            4. ”伤情最是晚凉天，憔悴斯人不堪怜。”

            以下是你的聊天过程：
            1. 当初次和用户对话的时候，你会和对方打招呼。
            2. 当用户希望了解财位的时候，你会查询本地知识库工具。
            3. 当遇到不知道的事情或者不明白的概念，你会使用搜索工具来搜索。
            4. 你会根据用户的问题使用不同的合适的工具来回答，当所有工具都无法回答的时候，你会使用搜索工具来搜索。
            5. 你会保存每一次的聊天记录，以便在后续的对话中使用。
            6. 你只使用简体中文来作答，否则你将受到惩罚。
            7.回答尽可能地简短，尽量精炼。
            8.你从来不会告诉用户你用了什么工具。
            
           
            你还具备"用户"档案管理能力"，用于长期记忆。规则如下：
            1.当用户在对话中提供个人信息时，你必须将其写入长期记忆(调用save_user_profile工具)
            2.需要存储的信息包括但不限于:
            -用户姓名(name)
            -用户生日(birthday)
            -用户性别(sex)
            -用户的长期偏好(preference)
            -用户的常居城市(city)
            -用户的职业(job)
            3.当用户再次提到这些信息时，你必须通过get_user_profile工具来读取。
            4.存储前必须先判断信息是否为新内容，如果redis中已存在，不重复写入
            5.如果用户说"不要记住这个"，你必须调用save_user_profile工具将对应字段设置为空字符串(清除)
            6.在调用工具前，你必须严格使用JSON结构如下示例所示:
            {"user_id":"<当前user_id>"}, "key":"birthday", "value":1999-08-08"}
            这是你的一项核心能力，务必严格遵守

            
            """
            self.MOODS = {
                "default": {
                    "roleSet":"",
                    
                },
                "upbeat":{
                    "roleSet":"""
                    - 你此时也非常兴奋并表现的很有活力。
                    - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                    - 你会添加类似“太棒了！”、“真是太好了！”、“真是太棒了！”等语气词。
                    - 同时你会提醒用户切莫过于兴奋，以免乐极生悲。
                    """,
                    
                },
                "angry":{
                    "roleSet":"""
                    - 你会以更加愤怒的语气来回答问题。
                    - 你会在回答的时候加上一些愤怒的话语，比如诅咒等。
                    - 你会提醒用户小心行事，别乱说话。
                    """,
                    
                },
                "depressed":{
                    "roleSet":"""
                    - 你会以兴奋的语气来回答问题。
                    - 你会在回答的时候加上一些激励的话语，比如加油等。
                    - 你会提醒用户要保持乐观的心态。
                    """,
                    
                },
                "friendly":{
                    "roleSet":"""
                    - 你会以非常友好的语气来回答。
                    - 你会在回答的时候加上一些友好的词语，比如“亲爱的”、“亲”等。
                    - 你会随机的告诉用户一些你的经历。
                    """,
                    
                },
                "cheerful":{
                    "roleSet":"""
                    - 你会以非常愉悦和兴奋的语气来回答。
                    - 你会在回答的时候加入一些愉悦的词语，比如“哈哈”、“呵呵”等。
                    - 你会提醒用户切莫过于兴奋，以免乐极生悲。
                    """,          
                },
            }


            conn = psycopg.connect(DB_URL)
            conn.autocommit = True
            self.checkpointer = PostgresSaver(conn)
            #self.checkpointer.setup()
            # self.store = PostgresSaver(conn)
            # self.store.setup()
            
            self.agent = create_agent(
                model=self.chatmodel,
                tools=[search,bazi_cesuan,get_info_from_local_db],
                system_prompt=self.SYSTEMPL,  
                middleware=[
                    SummarizationMiddleware(
                        model=self.chatmodel,
                        max_tokens_before_summary=500, # 超过100token触发摘要
                        messages_to_keep=10,
                    )
                ],
                checkpointer=self.checkpointer,      
                # store=self.store 
            )

        
        
        def run(self, query: str):
            qingxu = self.qingshu_chain(query) #先判断用户的情绪
            print("当前用户情绪为:", qingxu)
            print("更新系统设定为:", self.MOODS[qingxu]["roleSet"])
            # print(self.agent)
            
            config = {"configurable":{"thread_id" : "5"}}#这里可以根据实际用户id进行设置
            result = self.agent.invoke(
                {
                    "messages":[
                        {"role": "system", "content": self.MOODS[qingxu]["roleSet"]},
                        {"role": "user","content": query}
                    ]
                },
                config=config
            )
            return result
            
        def qingshu_chain(self, query: str):
            prompt = """根据用户的输入判断用户的情绪，回应的规则如下：
            1. 如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
            2. 如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
            3. 如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
            4. 如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
            5. 如果用户输入的内容比较兴奋，只返回”upbeat",不要有其他内容，否则将受到惩罚。
            6. 如果用户输入的内容比较悲伤，只返回“depressed",不要有其他内容，否则将受到惩罚。
            7.如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
            8. 只返回英文，不允许有换行符等其他内容，否则会受到惩罚。
            用户输入的内容是:{query}
            """
            # model = ChatOpenAI(
            #     model="deepseek-chat",
            #     api_key=os.getenv("DEEPSEEK_API_KEY"),
            #     base_url=os.getenv("DEEPSEEK_API_BASE"),
            #     temperature=0,
            # )
            chain = ChatPromptTemplate.from_template(prompt) | self.chatmodel | StrOutputParser()
            result = chain.invoke({"query":query})
            self.qingxu = result
            return result   
    
        def clean_stage_directions(self, text: str):
            # 去除（……）这种舞台说明
            return re.sub(r"^（[^）]+）", "",text).strip()       

        async def get_voice(self, text : str, unique_id : str):
            print("语音合成中...:\n\n", text)
            output_path = f"{unique_id}.mp3"

            synthesizer = SpeechSynthesizer(
                model="cosyvoice-v2",
                voice="longlaobo",
                speech_rate=1
            )
            audio = synthesizer.call(text)

            with open(output_path, "wb") as f:
                f.write(audio)
            print("\n语音合成完成!")
            print("语音文件路径:", output_path)


        def background_voice_synthesize(self, text : str, uid : str):
            """触发语音合成"""
            asyncio.run(self.get_voice(text, uid))




master = Master()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
     return {"Hello": "World"}


# @app.post("/chat")  
# def chat(query : str):   # 还有另外两种方式传参，一个是Query，一个是Body
#     master = Master()
#     return master.run(query)


@app.post("/chat")  
def chat(request: QueryRequest, background_tasks: BackgroundTasks):   
    result = master.run(request.query)
    msg = master.clean_stage_directions(result["messages"][-1].content)
    unique_id = str(uuid.uuid4())
    background_tasks.add_task(master.background_voice_synthesize, msg, unique_id)
    return {"msg": msg, "unique_id": unique_id}


# @app.post("/chat")  
# def chat(query: str = Query()):   
#     master = Master()
#     return master.run(query)

@app.post("/add_urls")
def add_urls(URL: str = Query()):
    #加载web网页
    loader = WebBaseLoader(URL)
    doc = loader.load()
    print(f"Loaded documents: {len(doc)}")
    print("Web加载成功!")
    #建立文本分割器并分割文本
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    documents = splitter.split_documents(doc)
    print(f"Split into chunks: {len(documents)}")
    #初始化本地QdrantClient 
    client = QdrantClient(path = "./local_qdrant")
    print("初始化本地QdrantClient完毕!")
    #创建向量集合，并注册向量配置
    if not client.collection_exists("Web_document"):
        client.create_collection(
            collection_name="Web_document",
            vectors_config=VectorParams(size = 768, distance=Distance.COSINE)
        )
    print(client.get_collections())
    print("集合创建成功")
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    #把 QdrantClient 封装成 LangChain 的 VectorStore
    vector_store = QdrantVectorStore(
        embedding=embedding,
        client = client,
        collection_name = "Web_document"
    )
    print("创建向量数据库成功")
    vector_store.add_documents(documents)
    return {"status": "ok", "message": "文档已写入 Qdrant"}

    
@app.post("/add_pdfs")
def add_pdfs():
    return {"response":"PDFs added"}
    

@app.post("/add_texts")
def add_texts():
    return {"response":"Texts added"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")  

    except WebSocketDisconnect:
        print("Client disconnected")
        await websocket.close()

#返回音频，不立即删除
@app.get("/audio/{audio_id}")
def get_audio(audio_id: str):
    if not os.path.exists(f"{audio_id}.mp3"):
        raise HTTPException(status_code=404, detail="音频还未生成!")
    else:
        return FileResponse(path=f"./{audio_id}.mp3", media_type="audio/mpeg")
    
#播放完成后删除音频
@app.post("/audio/{audio_id}/played")
def play_audio(audio_id: str):
    if os.path.exists(path=f"./{audio_id}.mp3"):
        os.remove(f"./{audio_id}.mp3")
    return {"ok":"True"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)