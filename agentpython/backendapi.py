from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from bot import run_agent

app = FastAPI(title="employee ai agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ChatRequest(BaseModel):
    message: str
    session_id:Optional[str]="default"


@app.post("/chat")
async def chat(req: ChatRequest):
    """Process user message and return action + data"""
    response = await run_agent(req.session_id,req.message)
    return response


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)