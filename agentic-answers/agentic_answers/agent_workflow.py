import json
import re
from typing import Annotated, Any, AsyncGenerator

from autogen import ConversableAgent, register_function  # type: ignore - ignore stub file
from pydantic import BaseModel

from shared.chroma.chroma_client import ChromaClient
from shared.embedding.embedding_client import EmbeddingClient
from shared.rag.rag_client import RagClient
from shared.web_search.ddg_search import ddg_search

from .config import get_config
from .dtos.response import EventResponse
from .  import prompts

class AgentWorkflow():
    def __init__(self, prompt: str, max_plan_steps: int):
        self.config = get_config()

        self.max_plan_steps = max_plan_steps

        chroma_client = ChromaClient(self.config.chroma_config)
        embedding_client = EmbeddingClient(self.config.embedding_config)
        self.rag_client = RagClient(chroma_client, embedding_client)
        
        self.prompt = prompt

        self.create_agents()
        self.add_tools()

        

    def create_agents(self):
        llm_config: dict[str, Any] = {
            "model": self.config.model_id,
            "client_host": self.config.api_url,
            "api_type": "ollama",
            "temperature": self.config.tempature
        }

        class Plan(BaseModel):
            steps: list[str]
        planner_llm_config: dict[str, Any] = {
            **llm_config,
            "response_format": Plan
        }

        # Provides the initial high level plan
        self.planner = ConversableAgent(
            name="Planner",
            system_message=prompts.PLANNER_MESSAGE.format(max_plan_steps=self.max_plan_steps),
            llm_config=planner_llm_config,
            human_input_mode="NEVER",
        )

        # Responsible for executing each step of the plan, including calling tools
        self.research_assistant = ConversableAgent(
            name="Research_Assistant",
            system_message=prompts.RESEARCH_ASSISTANT_PROMPT,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

        # Decides whether the output of the previous step satisfactorily fulfilled the instruction it was given. 
        self.step_critic = ConversableAgent(
            name="Step_Critic",
            llm_config=llm_config,
            human_input_mode="NEVER",
        )

        # Reflect on plan progress and give the next step
        self.reflection_assistant = ConversableAgent(
            name="ReflectionAssistant",
            system_message=prompts.REFLECTION_ASSISTANT_PROMPT,
            llm_config=llm_config,
            human_input_mode="NEVER",
        )

        self.user_proxy = ConversableAgent(
            name="User",
            system_message=prompts.USER_PROMPT.format(goal=self.prompt),
            human_input_mode="NEVER",
            llm_config=llm_config,
            is_termination_msg=lambda msg: "<ANSWER>" in msg["content"]
                or "<TERMINATE>" in msg["content"]
                or ("tool_calls" not in msg and msg["content"] == ""),
        )
    
    def add_tools(self):
        async def do_web_search(
            search_instruction: Annotated[str, prompts.SEARCH_INSTRUCTION]
            ) -> str:
            if not search_instruction:
                return "Please provide a search query."

            search_results = ddg_search(search_instruction)
            return str(search_results)

        async def do_knowledge_search(search_instruction: Annotated[str, prompts.SEARCH_INSTRUCTION]) -> str:
            if not search_instruction:
                return "Please provide a search query."
            results = await self.rag_client.get_documents(search_instruction)
            return str([x.document for x in results])
        
        register_function(
            f=do_knowledge_search,
            caller=self.research_assistant,
            executor=self.user_proxy,
            description= """Use this tool if you need to obtain information that is unique to the user and cannot be found on the internet.
            Given an instruction on what knowledge you need to find, search the user's documents for information particular to them, their projects, and their domain.
            This is simple document search, it cannot perform any other complex tasks.
            This will not give you any results from the internet. Do not assume it can retrieve the latest news pertaining to any subject.
            """
        )
        register_function(
            f=do_web_search,
            caller=self.research_assistant,
            executor=self.user_proxy,
            description="""This function is used for searching the web for information that can only be found on the internet,
            not in the users personal notes.
            """
        )
    

    async def emit_event(self, message: str) -> AsyncGenerator[EventResponse, None]:
        event_data: EventResponse = {
            "type": "message",
            "data": {"content": message + "\n"},
        }
        yield event_data

    async def run_workflow(self) -> AsyncGenerator[EventResponse, None]:
        def summarize_research_assistant(user_agent: ConversableAgent, research_assistant_agent: ConversableAgent, _: Any):
            """
            Finds that last message that the research assistant sent.
            """
            for message in reversed(user_agent.chat_messages[research_assistant_agent]):
                if ("name" in message and "content" in message
                    and message["name"] == research_assistant_agent.name
                    and "TERMINATE" not in message["content"]):
                    summary = message["content"]
                    if "<think>" and "</think>" in message["content"]:
                        summary = re.sub(r"<think>.*<\/think>", "", summary, flags=re.DOTALL)
                    return summary
            return ""

        #########################
        # Begin Agentic Workflow
        #########################
        # Create the plan, using structured outputs
        self.emit_event(message="Creating a plan...")
        try:
            output = await self.user_proxy.a_initiate_chat(
                message=self.prompt,
                recipient=self.planner,
                max_turns=1,
            )
            planner_output: list[str] = json.loads(output.summary)["steps"]
        except Exception as e:
            raise Exception(f"Unable to assemble a plan based on the input. Please try re-formulating your query! Error: \n\n{e}")
        # Start executing plan
        answer_output: list[str] = []  # This variable tracks the output of previous successful steps as context for executing the next step
        steps_taken: list[str] = []  # A list of steps already executed
        
        step_count = 0
        instruction_index = 0
        instruction = planner_output[instruction_index]
        while step_count < self.max_plan_steps:
            self.emit_event(message="Executing step: " + instruction)
            research_prompt = instruction
            if answer_output:
                research_prompt += f"""
                These steps have been completed: 
                {str(answer_output)}
                """
            output = await self.user_proxy.a_initiate_chat(
                recipient=self.research_assistant,
                message=research_prompt,
                summary_method=summarize_research_assistant,
                max_turns=3
            )

            # The previous instruction and its output will be recorded for the next iteration to inspect before determining the next step of the plan
            research_output = output.summary
            if not research_output:
                raise Exception("No output provided by agent")

            self.emit_event(message="Planning the next step...")
            
            # Ask the critic if the previous step was properly accomplished
            output = await self.user_proxy.a_initiate_chat(
                recipient=self.step_critic,
                message=prompts.STEP_CRITIC_PROMPT.format(
                    last_step=instruction,
                    last_output=research_output,
                ),
                max_turns=1
            )
            # If it was not accomplished, make sure an explanation is provided for the reflection assistant
            if "<NO>" in output.summary:
                self.emit_event(message="Revising previous step...")
                reflection_message = f"The previous step was {instruction} but it was not accomplished satisfactorily due to the following reason: \n {output.summary}."
                # Then, ask the reflection agent for the next step
                message = {
                    "Goal": self.prompt,
                    "Plan": str(planner_output),
                    "Last Step": reflection_message,
                    "Last Step Output": research_output,
                    "Steps Taken": str(steps_taken),
                }
                output = await self.user_proxy.a_initiate_chat(
                        recipient=self.reflection_assistant,
                        message=f"(```{str(message)}```",
                        max_turns=1
                    )
                instruction = output.summary
            else:
                reflection_message = instruction
                # Only append the previous step and its output to the record if it accomplished its task successfully.
                # It was found that storing information about unsuccessful steps causes more confusion than help to the agents
                answer_output.append(research_output)
                steps_taken.append(instruction)
                instruction_index += 1
                if len(planner_output) == instruction_index:
                    # End of plan reached
                    break
                instruction = planner_output[instruction_index]

            step_count += 1

        self.emit_event(message="Summing up findings...")
        # Now that we've gathered all the information we need, we will summarize it to directly answer the original prompt
        final_prompt = f"Answer the user's query: {self.prompt}. Use the following information only. Do NOT supplement with your own knowledge: {answer_output}"
        yield {
            "type": "final",
            "data": {
                "content": final_prompt
            }
        }