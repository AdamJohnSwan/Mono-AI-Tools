from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv

from .agent_workflow import AgentWorkflow, dict_to_str
from .dtos.request import AgenticRequest
from .dtos.response import EventResponse

app = FastAPI(
    title="Agentic Answers API",
    version="1.0.0",
    description="Takes a question and uses agentic RAG to provide an answer.",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv() 

# -------------------------------
# Routes
# -------------------------------

@app.post("/agentic-answers", summary="Complete a task using AI agents")
async def run_agentic_answers(req: AgenticRequest, stream: bool = Query(default=False, description="Whether or not to stream the response")):
    agent_workflow = AgentWorkflow(req.prompt)
    if (stream):
        return StreamingResponse(dict_to_str(agent_workflow.run_workflow()), media_type="text/event-stream")
    else:
        events: list[EventResponse] = []
        async for event in agent_workflow.run_workflow():
            events.append(event)
        return events