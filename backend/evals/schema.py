from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    namespace: str
    metric_name: str
    params: dict
