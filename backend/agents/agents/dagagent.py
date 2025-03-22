# from autogen_agentchat.agents import AssistantAgent
# from autogen_agentchat.messages import ModelClientStreamingChunkEvent
# from autogen_agentchat.base import ChatCompletionContext, Memory
# from autogen_agentchat.agents._assistant_agent import AssistantAgentConfig
# from typing import Any, Dict, Optional, Type, List, Callable, Awaitable, Sequence, AsyncGenerator, Union
# from autogen_core.tools import BaseTool
# from autogen_core import CancellationToken
# from pydantic import BaseModel, Field, EmailStr, create_model
# from uuid import UUID
# from autogen_core.models import (
#     ChatCompletionClient,
#     CreateResult,
#     SystemMessage,
# )

# # 🔹 Type mappings from JSON Schema → Pydantic types
# TYPE_MAPPING = {
#     "string": str,
#     "integer": int,
#     "boolean": bool,
#     "number": float,
#     "object": dict,  # Will be handled separately for nested models
#     "array": list,   # Will be handled separately for list elements
# }

# FORMAT_MAPPING = {
#     "uuid": UUID,
#     "email": EmailStr,
# }


# def resolve_ref(ref: str, definitions: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Resolves a $ref path (e.g., `#/$defs/PreferencesModel`) into the actual JSON schema.
#     """
#     ref_key = ref.split("/")[-1]  # Extract "PreferencesModel" from "#/$defs/PreferencesModel"
#     return definitions.get(ref_key, {})


# def json_schema_to_pydantic(
#     schema: Dict[str, Any], definitions: Dict[str, Any], model_name: str = "GeneratedModel"
# ) -> Type[BaseModel]:
#     """
#     Converts a JSON Schema into a dynamically created Pydantic model with proper nested handling.

#     :param schema: The JSON Schema dictionary.
#     :param definitions: Extracted `$defs` containing referenced models.
#     :param model_name: The name of the generated Pydantic model.
#     :return: A dynamically generated Pydantic model class.
#     """
#     fields = {}
#     required_fields = set(schema.get("required", []))

#     for key, value in schema.get("properties", {}).items():
#         json_type = value.get("type", "string")
#         field_type = TYPE_MAPPING.get(json_type, str)  # Default to string

#         # Handle special formats (UUID, Email, etc.)
#         if json_type == "string" and "format" in value:
#             field_type = FORMAT_MAPPING.get(value["format"], str)

#         # Resolve `$ref` (nested objects defined in `$defs`)
#         if "$ref" in value:
#             ref_schema = resolve_ref(value["$ref"], definitions)
#             field_type = json_schema_to_pydantic(ref_schema, definitions, model_name=f"{model_name}_{key}")

#         # Handle nested objects (direct properties inside)
#         elif json_type == "object" and "properties" in value:
#             field_type = json_schema_to_pydantic(value, definitions, model_name=f"{model_name}_{key}")

#         # Handle lists/arrays (recursively process list elements)
#         if json_type == "array" and "items" in value:
#             item_schema = value["items"]

#             if "$ref" in item_schema:  # If array contains objects with `$ref`
#                 ref_schema = resolve_ref(item_schema["$ref"], definitions)
#                 item_type = json_schema_to_pydantic(ref_schema, definitions, model_name=f"{model_name}_{key}_Item")
#             elif "properties" in item_schema:  # If array contains inline objects
#                 item_type = json_schema_to_pydantic(item_schema, definitions, model_name=f"{model_name}_{key}_Item")
#             else:
#                 item_type = TYPE_MAPPING.get(item_schema.get("type", "string"), str)

#             field_type = List[item_type]  # List of the determined type

#         # Handle default values
#         default_value = value.get("default", None)
#         is_required = key in required_fields

#         # Use '...' if required, else provide default
#         fields[key] = (field_type, Field(default=... if is_required else default_value))

#     # Dynamically create the model
#     return create_model(model_name, **fields)


# class DagAgentConfig(AssistantAgentConfig):
#     metadata: Optional[Dict[str, Any]] = None # Additional metadata for the DAG agent configuration (e.g. Tenant ID, User ID etc)
#     output_json_schema: Optional[Dict[str, Any]] = None # JSON schema to validate the output of the DAG agent if it is not None then set it the JSON schema call response format
#     output_pydantic_model: Optional[Type[BaseModel]] = None # Pydantic model to validate the output of the DAG agent if it is not None then set it the Model call response format

# class DagAgent(AssistantAgent):
#     component_config_schema = DagAgentConfig
#     component_provider_override = "backend.agents.agents.dagagent.DagAgent"

#     def __init__(
#         self,
#         name: str,
#         model_client: ChatCompletionClient,
#         *,
#         tools: List[BaseTool[Any, Any] | Callable[..., Any] | Callable[..., Awaitable[Any]]] | None = None,
#         handoffs: List[HandoffBase | str] | None = None,
#         model_context: ChatCompletionContext | None = None,
#         description: str = "An agent that provides assistance with ability to use tools.",
#         system_message: (
#             str | None
#         ) = "You are a helpful AI assistant. Solve tasks using your tools. Reply with TERMINATE when the task has been completed.",
#         model_client_stream: bool = False,
#         reflect_on_tool_use: bool = False,
#         tool_call_summary_format: str = "{result}",
#         memory: Sequence[Memory] | None = None,
#         meta_data: Optional[Dict[str, Any]] = None,
#         output_pydantic_model: Optional[Type[BaseModel]] = None,
#         output_json_schema: Optional[Dict[str, Any]] = None,
#     ):
#         super().__init__(
#             name=name,
#             model_client=model_client,
#             tools=tools,
#             handoffs=handoffs,
#             model_context=model_context,
#             description=description,
#             system_message=system_message,
#             model_client_stream=model_client_stream,
#             reflect_on_tool_use=reflect_on_tool_use,
#             tool_call_summary_format=tool_call_summary_format,
#             memory=memory,
#         )
#         if meta_data:
#             self.meta_data = meta_data
#         if output_pydantic_model:
#             self.output_pydantic_model = output_pydantic_model
#             self.output_json_schema = output_pydantic_model.schema()
#         elif output_json_schema:
#             self.output_json_schema = output_json_schema
#             self.output_pydantic_model = json_schema_to_pydantic(output_json_schema, {})

#     @classmethod
#     async def _call_llm(
#         cls,
#         model_client: ChatCompletionClient,
#         model_client_stream: bool,
#         system_messages: List[SystemMessage],
#         model_context: ChatCompletionContext,
#         tools: List[BaseTool[Any, Any]],
#         handoff_tools: List[BaseTool[Any, Any]],
#         agent_name: str,
#         cancellation_token: CancellationToken,
#         metadata: Optional[Dict[str, Any]] = None,

#     ) -> AsyncGenerator[Union[CreateResult, ModelClientStreamingChunkEvent], None]:
#         all_messages = await model_context.get_messages()
#         llm_messages = cls._get_compatible_context(model_client=model_client, messages=system_messages + all_messages)

#         all_tools = tools + handoff_tools
#         extra_create_args = {}
#         if metadata is not None:
#             extra_create_args["metadata"] = metadata


#         if model_client_stream:
#             model_result: Optional[CreateResult] = None
#             async for chunk in model_client.create_stream(
#                 llm_messages, tools=all_tools, cancellation_token=cancellation_token
#             ):
#                 if isinstance(chunk, CreateResult):
#                     model_result = chunk
#                 elif isinstance(chunk, str):
#                     yield ModelClientStreamingChunkEvent(content=chunk, source=agent_name)
#                 else:
#                     raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
#             if model_result is None:
#                 raise RuntimeError("No final model result in streaming mode.")
#             yield model_result
#         else:
#             model_result = await model_client.create(
#                 llm_messages, tools=all_tools, cancellation_token=cancellation_token
#             )
#             yield model_result
