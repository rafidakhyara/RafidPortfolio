from fastapi import FastAPI
from pydantic import BaseModel
from chat import rag_chat

app = FastAPI()

class rag_input(BaseModel):
    input:str

@app.post("/rag_chat")
def chat(input:rag_input):
    return rag_chat(input.input)


