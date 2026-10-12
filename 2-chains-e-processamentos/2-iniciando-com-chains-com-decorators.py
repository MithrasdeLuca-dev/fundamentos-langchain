from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import chain

from dotenv import load_dotenv
load_dotenv()

@chain
def square(input_dict : dict) -> dict:
    x = input_dict["x"]
    return{"square_result": x * x} 


# result = square.invoke({"x": 10})
# print(result)


question_template = PromptTemplate(
    input_variables=["name"],
    template="Hi, I'm {name}! Tell me a joke with my name!"    
)

question_template2 = PromptTemplate(
    input_variables=["square_result"],
    template="Tell me about the number {square_result}"    
)


model = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.5)

chain = question_template | model
chain2 = square | question_template2 | model

result = chain2.invoke({"x": 10})

print(result.content)
