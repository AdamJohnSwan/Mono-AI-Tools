import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv

from .agent_workflow import AgentWorkflow
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

@app.post("/agentic-answers", summary="Complete a task using AI agents")
async def run_agentic_answers(req: AgenticRequest, stream: bool = Query(default=False, description="Whether or not to stream the response")):
    agent_workflow = AgentWorkflow(req.prompt, req.max_plan_steps)
    if (stream):
        async def stream_agent_workflow():
            async for event in agent_workflow.run_workflow():
                yield json.dumps(event)
        return StreamingResponse(stream_agent_workflow())
    else:
        events: list[EventResponse] = []
        async for event in agent_workflow.run_workflow():
            events.append(event)
        return events