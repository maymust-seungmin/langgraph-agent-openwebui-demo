# from dotenv import load_dotenv
# import os
# from sqlalchemy import create_engine, inspect
#
# # Load environment variables securely
# load_dotenv()
#
# # Get credentials without printing them
# db_user = os.getenv("POSTGRES_USER")
# db_password = os.getenv("POSTGRES_PASSWORD")
# db_host = os.getenv("POSTGRES_HOST", "localhost")
# db_port = os.getenv("POSTGRES_PORT", "5432")
# db_name = os.getenv("POSTGRES_DB", "postgres")
#
# # Create connection string and engine
# connection_string = (
#     f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
# )
# engine = create_engine(connection_string)
#
# # Use inspector to explore schema
# inspector = inspect(engine)
#
# # Get the list of tables in the database
# tables = inspector.get_table_names()
# print(tables)


# from langchain_community.llms import VLLMOpenAI
#
# # create model using OpenAI compatible class VLLMOpenAI
# llm = VLLMOpenAI(
#     model="Qwen/Qwen3-32B-AWQ",
#     openai_api_key="EMPTY",
#     openai_api_base="http://localhost:8000/v1",
# )
#
#
# for i in llm.stream("대한민국의 수도와 일본의 수도 차이점 한글로 답변"):
#     print(i, end="")


# from langchain_ollama import ChatOllama
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import AIMessageChunk
#
# llm = ChatOllama(model="qwen3:30b-a3b", keep_alive=-1)
#
# # prompt = ChatPromptTemplate.from_template(
# #     "Provide a brief explanation of this {topic} 한국어로 답변해"
# # )
#
# # Chaining
# # chain = prompt | llm | StrOutputParser()
#
# # response = chain.stream({"topic": "deep learning"})
#
# # Streaming response from model
# for token in llm.stream("investments 테이블 조회해줘"):
#     if isinstance(token, AIMessageChunk):
#         print(token.content, end="", flush=True)
#     elif isinstance(token, str):
#         print(token, end="", flush=True)
#

