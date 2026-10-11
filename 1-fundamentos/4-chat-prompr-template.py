from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()


system = ("system", "you are an assistant that answer questions in a {style} style")

user = ("user", "{question}")

prompt = ChatPromptTemplate.from_messages([system, user])

messages = prompt.format_messages(style="funny", question="Quando ocorreu o ataque as torres gêmeas?")

for msg in messages:
    print(f"{msg.type}: {msg.content}")


model = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.5)
result = model.invoke(messages)

print(result.content)