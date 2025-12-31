from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from typing import Literal
import requests
load_dotenv()
user_id="user_001"
model_01 = ChatOpenAI(model="deepseek-chat", temperature=0, base_url=os.getenv("DEEPSEEK_API_BASE"), api_key=os.getenv("DEEPSEEK_API_KEY"))





@tool(description="只有需要了解实时信息或者不知道的事情的时候才会使用这个工具")
def search(query: str) -> str:
    serp = SerpAPIWrapper()
    response = serp.run(query)
    # print("response的类型",type(response))
    return  response

# @tool
# def get_info_from_local_db(query: str) -> str:
#     """从本地数据库获取信息的工具"""
#     # 连接本地 Qdrant 服务（已持久化）
#     client = QdrantClient(
#         url="http://localhost:6333",
#         api_key=None,
#     )

#     collection_name = "day0_first_system"

# # 创建 Collection
#     client.create_collection(
#         collection_name=collection_name,
#         vectors_config=models.VectorParams(
#             size=4, 
#             distance=models.Distance.COSINE,
#         ),
#     )

# # 建立 payload 索引（用于过滤）
#     client.create_payload_index(
#         collection_name=collection_name,
#         field_name="category",
#         field_schema=models.PayloadSchemaType.KEYWORD,
#     )

# @tool
# def get_info_from_local_db(query:str):
#     """只有回答与2024年运势或者龙年运势相关的问题的时候，会使用这个工具，必须输入用户的生日."""
#     client = Qdrant(
#         QdrantClient(path="/Users/tomiezhang/Desktop/shensuan-教学/bot/local_qdrand"),
#         "local_documents",
#         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
#     )
#     retriever = client.as_retriever(search_type="mmr")
#     result = retriever.get_relevant_documents(query)
#     return result

@tool
def get_info_from_local_db(query:str) -> str:
    """当用户提到“财位”“风水”“家居布局”“提升财运”“客厅摆放”等关键词时，必须调用本工具，从本地风水知识库中检索内容。不得自行编造。"""
    # """只有回答跟财位有关的问题时，才会使用这个本地知识库工具"""
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    client = QdrantClient(path="./local_qdrant")
    # client.create_collection(
    #     collection_name="Web_documents",
    #     vectors_config=VectorParams(size = 3072, distance = Distance.COSINE),
    # )
    print("Web_document: \n",client.count("Web_document"))
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="Web_document",
        embedding=embedding,
    )
    result = vector_store.similarity_search(query)#这里返回的是List[Document]，要变成str
    if not result:
        print("没有找到相关信息")
        return "没有找到相关信息"
    text = "\n\n".join(m.page_content for m in result)
    print("搜素结果:",text)
    return text


class BaziRequest(BaseModel):
    # api_key: str = Field(description="",default=os.getenv("YUANFENJU_API_KEY")),
    name: str = Field(description="姓名")
    sex: Literal[0,1] = Field(description="性别，0表示男，1表示女，根据姓名判断")
    type: Literal[0,1] = Field(description="日历类型，0表示农历，1表示公历，默认1",default=1),
    year: int = Field(description="出生年份 例：1998")
    month: int = Field(description="出生月份 例 8")
    day: int = Field(description="出生日期，例：8")
    hours: int = Field(description="出生小时 例 14")
    minute: int = Field(description="出生分钟 默认0", default=0)

@tool 
def bazi_cesuan(query: str) -> str:
    """只有做八字测算的时候才会使用这个工具,需要输入用户姓名和出生年月日时，如果缺少用户姓名和出生年月日时,则不可用"""
    url = "https://api.yuanfenju.com/index.php/v1/Bazi/cesuan"
    api_key = os.getenv("YUANFENJU_API_KEY")
    prompt = ChatPromptTemplate.from_template(
                """你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。JSON字段如下： - "name":"姓名", - "sex":"性别，0表示男，1表示女，根据姓名判断", - "type":"日历类型，0农历，1公里，默认1"，- "year":"出生年份 例：1998", - "month":"出生月份 例 8", - "day":"出生日期，例：8", - "hours":"出生小时 例 14", - "minute":"出生分钟 默认0"，如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论，用户输入:{query}""")
    parser = JsonOutputParser(pydantic_object=BaziRequest)
    chain = prompt | model_01 | parser
    data = chain.invoke({"query":query})
    print("八字参数提取为: ", data)
    result = requests.post(url, data={**data, "api_key": api_key})
    if result.status_code == 200:
        print("=====返回数据=====")
        print(result.json())
        try:
            json_content = result.json()#内置json解析更简洁
            returnstring = "八字为:"+json_content["data"]["bazi_info"]["bazi"]
        
            return returnstring
        except Exception as e:
            return "八字测算失败，请检查输入参数是否完整或正确。"
    else:
        return "八字测算请求失败，请稍后再试。"
    
if __name__ == "__main__": # 测试工具
    print(search.name)
    print(search.description)
    print(search.args_schema)
    print(search.args_schema.model_json_schema)
    result = search.invoke({"query":"今天腾讯股价是多少？"})
    print(result)