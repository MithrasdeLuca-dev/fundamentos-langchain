from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.5)

message = model.invoke("Hello, how are you?")

print(message.content)
