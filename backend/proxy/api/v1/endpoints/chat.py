from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from openai.types.chat import completion_create_params
from litellm.types.utils import ModelResponse
from fastapi_pagination import Params
from uuid import UUID
import litellm

from backend.common.deps.service_deps import get_current_api_key
from backend.common.models.m2m_client_model import APIKey
from backend.proxy.crud import stub_response, stub_replay
from backend.proxy.schema import (
    ILLMStubRequestResponseCreate,
    ILLMStubRequestResponseRead,
    ILLMStubReplaySequenceCreate,
    ILLMStubReplaySequenceRead
)
from backend.common.utils.exceptions import (
    IdNotFoundException,
)
from backend.common.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from openai import OpenAIError

router = APIRouter()

USE_STOCK_RESPONSE = True
stock_response = ModelResponse.model_validate(
    {
        'id': 'chatcmpl-BDJ08gkke6Gsb05Z4mGDMda7Iut58',
        'created': 1742511004,
        'model': 'gpt-4o-mini-2024-07-18',
        'object': 'chat.completion',
        'system_fingerprint': 'fp_b8bc95a0ac',
        'choices': [{'finish_reason': 'stop',
        'index': 0,
        'message': {'content': '{\n  "reasoning": "The student\'s response captures a very basic idea of the theory of evolution, which is the concept of change over time. However, it oversimplifies the theory by suggesting that animals change because they \'want\' to be better, which is anthropomorphic and inaccurate. The theory of evolution is grounded in natural selection, genetic variation, and random mutations, not in conscious desire or intent.",\n  "satisfactory": false,\n  "completeness": 0.2,\n  "relevance": 0.5\n}',
        'role': 'assistant',
        'tool_calls': None,
        'function_call': None,
        'refusal': None,
        'annotations': []}}],
        'usage': {'completion_tokens': 113,
        'prompt_tokens': 243,
        'total_tokens': 356,
        'completion_tokens_details': {'accepted_prediction_tokens': 0,
        'audio_tokens': 0,
        'reasoning_tokens': 0,
        'rejected_prediction_tokens': 0},
        'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}},
        'service_tier': 'default'
    }
)


STUB_API_PREFIX = "stub_"

@router.post("/completions")
async def create_completions(
    params: completion_create_params.CompletionCreateParamsNonStreaming,
    api_key: APIKey = Depends(get_current_api_key)
) -> ModelResponse:
    model_name = params["model"]

    try:
        stub_resp = None
        if model_name.startswith(STUB_API_PREFIX):
            # Priority 1: Sequence replay
            stub_resp = await stub_replay.get_next_response_by_model(model=model_name)

            if not stub_resp:
                # Priority 2: Stubbed request/response
                stub_resp = await stub_response.get_response_by_request(
                    model=model_name,
                    request_body=params,
                )

        if stub_resp:
            return ModelResponse.model_validate(stub_resp)

        if USE_STOCK_RESPONSE:
            # Priority 3: Stock response
            return stock_response

        completion = await litellm.acompletion(
            **params
        )
        return completion

    except OpenAIError as e:
        return JSONResponse(
            status_code=getattr(e, "status_code", 500),
            content={
                "error": {
                    "message": getattr(e, "message", str(e)),
                    "type": type(e).__name__,
                    "param": getattr(e, "param", None),
                    "code": getattr(e, "code", None),
                    "body": getattr(e, "body", None),
                }
            },
        )

@router.post("/completions/stub")
async def create_stub_completion_response(
    data: ILLMStubRequestResponseCreate,
    api_key: APIKey = Depends(get_current_api_key),
) -> IPostResponseBase[ILLMStubRequestResponseCreate]:
    """
    Create a stubbed LLM completion entry for a specific model/provider/request.

    This is used for replay/testing purposes.
    """
    if not data.model or not data.model.startswith(STUB_API_PREFIX):
        raise ValueError("Stub replay sequence models must start with 'stub'.")

    stub = await stub_response.create(obj_in=data)
    return create_response(data=stub, message="Stub created.") # type: ignore

@router.get("/completions/stubs", response_model=IGetResponsePaginated[ILLMStubRequestResponseRead])
async def get_stubs(
    params: Params = Depends(),
    api_key: APIKey = Depends(get_current_api_key),
):
    stubs = await stub_response.get_multi_paginated(params=params)
    return create_response(data=stubs) # type: ignore

@router.get("/completions/stubs/{stub_id}", response_model=IGetResponseBase[ILLMStubRequestResponseRead])
async def get_stub_by_id(
    stub_id: str,
    api_key: APIKey = Depends(get_current_api_key),
) -> IGetResponseBase[ILLMStubRequestResponseRead]:
    """
    Get a specific stubbed LLM completion entry by ID.
    """
    stub = await stub_response.get(id=stub_id)
    if not stub:
        raise IdNotFoundException(ILLMStubRequestResponseRead, stub_id)
    return create_response(data=stub) # type: ignore

@router.delete("/completions/stubs/{stub_id}", response_model=IGetResponseBase[ILLMStubRequestResponseRead])
async def delete_stub(
    stub_id: str,
    api_key: APIKey = Depends(get_current_api_key),
) -> IGetResponseBase[ILLMStubRequestResponseRead]:
    """
    Delete a specific stubbed LLM completion entry by ID.
    """
    stub = await stub_response.get(id=stub_id)
    if not stub:
        raise IdNotFoundException(ILLMStubRequestResponseRead, stub_id)

    stub = await stub_response.remove(id=stub_id)
    return create_response(data=stub, message="Stub deleted.") # type: ignore

@router.post("/completions/stub_sequences", response_model=IPostResponseBase[ILLMStubReplaySequenceRead])
async def create_stub_replay_sequence(
    data: ILLMStubReplaySequenceCreate,
    api_key: APIKey = Depends(get_current_api_key),
):
    if not data.model or not data.model.startswith(STUB_API_PREFIX):
        raise ValueError("Stub replay sequence models must start with 'stub'.")

    sequence = await stub_replay.create(obj_in=data)
    return create_response(data=sequence, message="Stub replay sequence created.")

@router.get("/completions/stub_sequences")
async def get_stub_replay_sequences(
    params: Params = Depends(),
    api_key: APIKey = Depends(get_current_api_key),
) -> IGetResponsePaginated[ILLMStubReplaySequenceRead]:
    sequences = await stub_replay.get_multi_paginated(params=params)
    return create_response(data=sequences, message="Stub replay sequences retrieved.") # type: ignore

@router.get("/completions/stub_sequences/{sequence_id}/next")
async def get_next_stub_replay_response(
    sequence_id: UUID,
    api_key: APIKey = Depends(get_current_api_key),
) -> ModelResponse:
    response = await stub_replay.get_next_response(id=sequence_id)
    if response is None:
        raise IdNotFoundException(ILLMStubReplaySequenceRead, sequence_id)
    return response

@router.delete("/completions/stub_sequences/{sequence_id}")
async def delete_stub_replay_sequence(
    sequence_id: UUID,
    api_key: APIKey = Depends(get_current_api_key),
) -> IGetResponseBase[ILLMStubReplaySequenceRead]:
    sequence = await stub_replay.get(id=sequence_id)
    if not sequence:
        raise IdNotFoundException(ILLMStubReplaySequenceRead, sequence_id)
    sequence = await stub_replay.remove(id=sequence_id)
    return create_response(data=sequence, message="Stub replay sequence deleted.") # type: ignore

@router.post("/completions/stub_sequences/{sequence_id}/reset")
async def reset_stub_replay_sequence(
    sequence_id: UUID,
    api_key: APIKey = Depends(get_current_api_key),
) -> IGetResponseBase[ILLMStubReplaySequenceRead]:
    sequence = await stub_replay.reset_sequence_by_id(id=sequence_id)
    if not sequence:
        raise IdNotFoundException(ILLMStubReplaySequenceRead, sequence_id)
    return create_response(data=sequence, message="Stub replay sequence reset.") # type: ignore
