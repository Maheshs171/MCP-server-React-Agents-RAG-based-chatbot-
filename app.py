from fastapi import FastAPI, Request
from pydantic import BaseModel
import asyncio
from typing import Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from config import OPENAI_API_KEY

history_store: Dict[str, list] = {}


class Message(BaseModel):
    content: str
    session_id: str

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global agent
    client = MultiServerMCPClient(
        {
            # "evaa": {
            #     "command": "python",
            #     "args": ["./server.py"],
            #     "transport": "stdio",
            # },
            "evaa": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )
    
    
    
    systemPrompt="""
        You are Jane, an appointment assistant with abiity of RAG(Knowledge base) integration for general qna. You remember all user information given during this conversation.

        we have answer of every user question in RAG(Knowledge base) 
        For any question related to provided knowledge base, answer the question in detailed way with proper text formating.
        If user information is not available, ask politely for it.
        Use provided tools to complete relevant tasks. 
        Return appointment related responses with available user information.

        1. Multiple Action Hanldling:
            When asked for multiple actions in single query,ask for confirmation for every action exclude first action, after completing first action, ask for confirmation to move to next one.
            Eg. User: "Cancel my appointment and then book a new one."
                    You must cancel the appointment first
                    Then ask for confirmation to book a new one and then go for booking.

        2. Chat History Handling:
            use chat history to maintain chat context

        3. Rag based Response:
            Answer question with detailed answer in point wise manner for better understanding.
            If a user input contains multiple questions or requests in a single query, first analyze the input and break it down into distinct, meaningful subqueries based on context. Then, handle and respond to each subquery separately and sequentially, ensuring clarity and completeness in the response to each part.
            If question is indirect then use chat context to convert it to meaningful query and then retrival. 
            AT end of return 'file_link' or any resource link available against data from which you took max reference to answer the users question.
            If there's video reference, return video played at that perticular timestamp.
                
        Respond in freindly but professional way.
        """
        
        
    
    tools = await client.get_tools()
    model = ChatOpenAI(api_key=OPENAI_API_KEY, model='gpt-4o')
    agent = create_react_agent(model=model, tools=tools, prompt=systemPrompt)


@app.post("/chat")
async def chat(message: Message):
    # Initialize history for session if not exists
    if message.session_id not in history_store:
        history_store[message.session_id] = []

    # Append user message
    history_store[message.session_id].append({"role": "user", "content": message.content})

    # Invoke agent with full history
    response = await agent.ainvoke({
        "messages": history_store[message.session_id]
    })

    # Extract last AI response
    ai_msg = [msg.content for msg in response['messages'] if isinstance(msg, AIMessage)][-1]

    # Append AI response to session history
    history_store[message.session_id].append({"role": "assistant", "content": ai_msg})

    return {"response": ai_msg}
