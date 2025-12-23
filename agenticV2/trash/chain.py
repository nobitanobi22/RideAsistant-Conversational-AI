
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

prompt_template = PromptTemplate(
    template= "Call {utility} agent",  #utility could be Booking, Tracking, etc.
    input_variables= ['utility']
)

model = ChatGroq(model='llama-3.1-8b-instant')

parser = StrOutputParser()

chain = prompt_template | model | parser

inp = input("What may I help you with? \n1. Booking\n2. Tracking\n3. Something Else\n")

response = chain.invoke({'utility' : inp})

print(response)

