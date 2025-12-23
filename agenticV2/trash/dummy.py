from pydantic import BaseModel
from langchain_groq import 

class BookingInfo(BaseModel):
    pickup: str | None
    drop: str | None
    schedule_time: str | None

parser = PydanticOutputParser(pydantic_object=BookingInfo)

booking_prompt = PromptTemplate(
    template = 
"""
You are a ride booking assistant. Extract the following from the user's message:
- pickup location
- drop location
- schedule_time (if the user specifies a time; otherwise null)

Respond in this exact format:
{format_instructions}

User message: {input}
""",
    
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

llm = ChatGroq(model = 'llama-3.1-8b-instant')

booking_chain = booking_prompt | llm | parser

response = booking_chain.invoke("Book a ride from delhi to gurgaon")
print(response)
