from typing import Any, Sequence, Mapping, Optional, Dict
from pydantic import BaseModel
import json
import tempfile
from pathlib import Path

from autogen_core import Image
from autogen_core.models import LLMMessage, UserMessage, CreateResult, RequestUsage
from autogen_core.tools import Tool, ToolSchema
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai.config import OpenAIClientConfigurationConfigModel
from autogen_ext.models.openai._openai_client import to_oai_type
from openai.types.chat import completion_create_params
from autogen_ext.models._utils.normalize_stop_reason import normalize_stop_reason

create_kwargs = set(completion_create_params.CompletionCreateParamsBase.__annotations__.keys()) | set(
    ("timeout", "stream")
)

class BatchOpenAIClient(OpenAIChatCompletionClient):
    """
    A custom OpenAI client that supports batch API usage.
    """

    component_type = "model"
    component_config_schema = OpenAIClientConfigurationConfigModel
    component_provider_override = "backend.agents.components.BatchOpenAIClient"

    def __init__(self, **kwargs: Dict[Any, Any]): # type: ignore
        super().__init__(**kwargs)

    async def create_batch(
        self,
        message_batches: Sequence[tuple[str, Sequence[LLMMessage]]],
        *,
        tools: Sequence[Tool | ToolSchema] = [],
        json_output: Optional[bool | type[BaseModel]] = None,
        extra_create_args: Mapping[str, Any] = {},
    ) -> tuple[Path, str]:
        """
        Create a batch job with multiple sequences of LLM messages.

        Args:
            message_batches: List of (custom_id, messages) tuples.
            tools: Optional list of tools.
            json_output: Whether to return JSON output.
            extra_create_args: Extra OpenAI-compatible create arguments.

        Returns:
            A tuple containing the path to the JSONL file and the batch_id returned from OpenAI.
        """
        extra_create_args_keys = set(extra_create_args.keys())
        if not create_kwargs.issuperset(extra_create_args_keys):
            raise ValueError(f"Extra create args are invalid: {extra_create_args_keys - create_kwargs}")

        # Copy the create args and overwrite anything in extra_create_args
        create_args = self._create_args.copy()
        create_args.update(extra_create_args)

        batch_entries = []
        for custom_id, messages in message_batches:
            local_create_args = self._create_args.copy()
            local_create_args.update(extra_create_args)

            if json_output is not None:
                if self.model_info["json_output"] is False and json_output is not False:
                    raise ValueError("Model does not support JSON output.")
                if json_output is True:
                    local_create_args["response_format"] = {"type": "json_object"}
                elif json_output is False:
                    local_create_args["response_format"] = {"type": "text"}
                elif isinstance(json_output, type) and issubclass(json_output, BaseModel):
                    schema = json_output.model_json_schema()
                    local_create_args["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": json_output.__name__,
                            "description": json_output.__doc__ or "",
                            "schema": schema,
                            "strict": False,
                        },
                    }

            if self.model_info["vision"] is False:
                for message in messages:
                    if isinstance(message, UserMessage) and isinstance(message.content, list):
                        if any(isinstance(x, Image) for x in message.content):
                            raise ValueError("Model does not support vision and image was provided.")

            oai_messages_nested = [to_oai_type(m, prepend_name=self._add_name_prefixes) for m in messages]
            oai_messages = [item for sublist in oai_messages_nested for item in sublist]

            if tools:
                raise ValueError("Tool calls are not currently supported in batch mode.")

            body = {
                **local_create_args,
                "messages": oai_messages,
            }

            batch_entries.append(
                {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": body,
                }
            )

        jsonl_path = self._generate_batch_jsonl_file(batch_entries)
        batch_id = await self._submit_openai_batch(jsonl_path)
        return jsonl_path, batch_id

    def _generate_batch_jsonl_file(self, batch_entries: list[dict[str, Any]]) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmpfile:
            for entry in batch_entries:
                tmpfile.write(json.dumps(entry) + "\n")
            return Path(tmpfile.name)

    async def _submit_openai_batch(self, jsonl_path: Path) -> str:
        # This method uses self._client to submit the batch using the OpenAI Batch API.
        with open(jsonl_path, "rb") as f:
            file_upload = await self._client.files.create(file=f, purpose="batch")

        response = await self._client.batches.create(
            input_file_id=file_upload.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        return response.id

    async def check_batch_status(self, batch_id: str) -> dict[str, Any]:
        """
        Check the status of a submitted batch job.

        Args:
            batch_id: The batch job ID.

        Returns:
            A dictionary with batch status information.
        """
        response = await self._client.batches.retrieve(batch_id)
        return response.model_dump()

    async def get_batch_results(self, batch_id: str) -> list[tuple[str, CreateResult]]:
        """
        Retrieve the results of a completed batch job.

        Args:
            batch_id: The batch job ID.

        Returns:
            A list of (custom_id, CreateResult) tuples.
        """
        batch = await self._client.batches.retrieve(batch_id)
        if batch.output_file_id is None:
            raise ValueError("Batch job has not completed or has no output file.")

        result_file = await self._client.files.content(batch.output_file_id)
        content_bytes = await result_file.aread()
        lines = content_bytes.decode("utf-8").splitlines()

        results: list[tuple[str, CreateResult]] = []
        for line in lines:
            data = json.loads(line)
            custom_id = data["custom_id"]
            response = data["response"]
            choice = response["choices"][0]

            result = CreateResult(
                finish_reason=normalize_stop_reason(choice.get("finish_reason")),
                content=choice["message"]["content"],
                usage=RequestUsage(
                    prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
                    completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
                ),
                cached=False,
                thought=None,
                logprobs=None,
            )
            results.append((custom_id, result))

        return results
