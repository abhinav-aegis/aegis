from uuid import UUID
from backend.agents import crud
from backend.agents.models import RunStatus, Run
from autogen_ext.models.openai import OpenAIChatCompletionClient
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from backend.agents.types import TeamResult, MessageMeta
from autogen_agentchat.base import TaskResult
from typing import Dict, Any

def get_openai_model_client(model: str) -> ChatCompletionClient:
    """
    This function creates a dummy OpenAI model client for testing purposes.
    """
    TEMP_TEST_KEY = "test_09d25e0sas6c52gf6c8181asadf6b7a9563b93asddsdef6f0f4caa6cf63b88e8d3e7"
    TEMP_BASE_URL = "http://localhost:8002/v1"

    if model.startswith("stub_"):
        return OpenAIChatCompletionClient(
            api_key=TEMP_TEST_KEY,
            base_url=TEMP_BASE_URL,
            model=model,
            model_info={"vision": True, "function_calling": True, "json_output": True, "family": "Mock"}
        )
    else:
        return OpenAIChatCompletionClient(
            api_key=TEMP_TEST_KEY,
            base_url=TEMP_BASE_URL,
            model=model,
        )

def get_mock_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    """
    This function creates a mock agent for testing purposes.
    """
    return AssistantAgent(
        name="Marking_Assisant",
        model_client=model_client,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=False,  # Enable streaming tokens from the model client.
    )

def get_team_result(task_result: TaskResult) -> TeamResult:
    """
    This function retrieves the last message from the team result.
    """
    last_message = task_result.messages[-1] if task_result.messages else None
    if last_message.content:
        if isinstance(last_message.content, str):
            try:
                last_message.content = json.loads(last_message.content)
            except json.JSONDecodeError:
                pass

    task_result.messages = [last_message] if last_message else []

    if last_message:
        return TeamResult(
            task_result=task_result,
            usage="",
            duration=0.0,
        )
    else:
        return TeamResult(
            task_result=task_result,
            usage="",
            duration=0.0,
        )

async def run_agent(agent: AssistantAgent, task: str = "Auto mark") -> str:
    result = await agent.run(
        task=task,
    )
    return result

async def run_team(run_id: UUID) -> Run:
    """
    This function is a placeholder for the actual implementation of running a team.

    It currently does nothing and is meant to be replaced with the actual logic.
    """
    run = await crud.run.get(id=run_id)
    if not run:
        raise RuntimeError(f"Run with ID {run_id} not found.")

    session = run.session
    if not session:
        raise RuntimeError(f"Session with ID {run.session_id} not found.")

    model: str
    if isinstance(session.team_metadata, dict):
        model = session.team_metadata.get("model", "gpt-4o-mini")
    elif isinstance(session.team_metadata, MessageMeta):
        model = getattr(session.team_metadata, "model", "gpt-4o-mini")
    else:
        model = "gpt-4o-mini"

    if run.status == RunStatus.CREATED:
        run.status = RunStatus.ACTIVE
        update_data: Dict[str, Any] = {}
        try:
            openai_model_client = get_openai_model_client(model)
            agent = get_mock_agent(openai_model_client)
            result = await run_agent(agent)
            update_data["status"] = RunStatus.COMPLETE
            update_data["team_result"] = get_team_result(result).model_dump()
            update_data["error_message"] = ""
            update_data["error_details"] = {}

        except Exception as e:
            run.status = RunStatus.ERROR
            error_dict = {
                "type": type(e).__name__,
                "message": getattr(e, "message", str(e)),
                "model": getattr(e, "model", None),
                "llm_provider": getattr(e, "llm_provider", None),
                "status_code": getattr(e, "status_code", None),
            }

            update_data["error_message"] = getattr(e, "message", str(e))
            update_data["error_details"] = error_dict

        run = await crud.run.update(obj_current=run, obj_new=update_data)
        return run

    else:
        return run
