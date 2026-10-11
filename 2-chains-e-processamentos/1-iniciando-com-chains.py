from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

question_template = PromptTemplate(
    input_variables=["name"],
    template="Hi, I'm {name}! Tell me a joke with my name!"    
)


model = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.5)

chain = question_template | model

result = chain.invoke({"name": "Mithras"})

print(result.content)