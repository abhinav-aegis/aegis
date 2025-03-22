from fastapi import APIRouter, Depends
from openai.types.chat import completion_create_params
from litellm.types.utils import ModelResponse

from backend.common.deps.service_deps import get_current_api_key
from backend.common.models.m2m_client_model import APIKey

router = APIRouter()


# @router.post("/process-job")
# async def process_job(data: dict, api_key: APIKey = Depends(get_current_api_key)):
#     """
#     Process a job.
#     """
#     return data

# router = APIRouter()

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

@router.post("/completions")
async def create_completions(
    params: completion_create_params.CompletionCreateParamsNonStreaming,
    api_key: APIKey = Depends(get_current_api_key)
) -> ModelResponse:
    return stock_response
