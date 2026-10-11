from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

model = init_chat_model(model="gemini-3.8-flash", model_provider="google_genai")

answer_gemini = model.invoke("Hello, how are you?")

print(answer_gemini.content)