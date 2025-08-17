from pydantic import BaseModel, Field


class AgenticRequest(BaseModel):
    prompt: str = Field(
        description="The task the user wants to accomplish"
    )