from langchain_openai import OpenAI, ChatOpenAI
import os
os.environ['OPENAI_API_KEY'] = '0000000000'

llm = OpenAI(openai_api_base="http://127.0.0.1:8000/v1", openai_api_key="0000000000", model ="aphrodite/TheBloke/Mistral-7B-v0.1-GPTQ")

s = llm.invoke(input="What is the capital of France?", temperature=0)
print(s)

llm = ChatOpenAI(openai_api_base="http://127.0.0.1:8000/v1", openai_api_key="0000000000", model ="aphrodite/TheBloke/Mistral-7B-v0.1-GPTQ")
print(llm.invoke([
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing great. How can I help you today?"},
    {"role": "user", "content": "Tell me about antartica"}
]))