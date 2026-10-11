from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

template = PromptTemplate(
    input_variables=["name"],
    template="Hi, I'm {name}! Tell me a joke with my name!"    
)

text = template.format(name="Mithras")

print(text)