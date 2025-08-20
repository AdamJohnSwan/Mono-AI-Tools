from pydantic import BaseModel, Field


class AgenticRequest(BaseModel):
    prompt: str = Field(
        description="The task the user wants to accomplish"
    )
    max_plan_steps: int = Field(
        default=3,
        description="This will set the maximum of steps a plan to complete the task can take. " \
        "More steps will take longer but will usually achieve better results."
    )