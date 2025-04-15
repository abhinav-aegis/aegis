"""
Base Evaluator Interface and Config Models.

Defines standard evaluator API and configuration model used in evaluation service.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Tuple, Optional
from enum import Enum
from pydantic import BaseModel


class CIComputationMethod(str, Enum):
    """
    Method used to compute confidence intervals.
    """
    batch_mean = "batch_mean"  # Mean of per-sample scores
    bootstrap = "bootstrap"    # Bootstrap estimation


class FieldExtractionConfig(BaseModel):
    """
    Configuration to extract ground truth and predicted values from input data.
    """
    ground_truth_field: str
    prediction_field: str

class DatasetInputConfig(BaseModel):
    """
    Configuration to specify how evaluation inputs are mapped to GroundTruth Dataset.
    """
    dataset_id: str  # ID of the GroundTruthDataset
    input_fields: Dict[str, str]  # Maps input names to GroundTruthItem.input_uri fields
    label_field: str  # Field path for the ground truth label

class MetricFunctionConfig(BaseModel):
    """
    Configuration to specify metric function used for evaluation.
    """
    namespace: str
    name: str
    params: Dict[str, Any] = {}
    ci_method: CIComputationMethod = CIComputationMethod.batch_mean
    bootstrap_iterations: int = 1000  # Used only if ci_method is bootstrap


class EvaluatorConfig(BaseModel):
    """
    Declarative config for Evaluator.

    Includes extraction logic and metric details.
    """
    name: str
    description: str
    provider: str
    extraction: FieldExtractionConfig
    metric: MetricFunctionConfig
    dataset_inputs: Optional[DatasetInputConfig] = None

class EvaluationResult(BaseModel):
    """
    Result of a single sample evaluation.
    """
    score: float
    metric_name: str
    additional_info: Optional[dict] = None


class BatchEvaluationResult(BaseModel):
    """
    Aggregated batch evaluation metrics.
    """
    metric_name: str
    mean: float
    std_dev: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    sample_size: int
    additional_info: Optional[dict] = None


class ComparisonResult(BaseModel):
    """
    Result of comparing two prediction sets.
    """
    metric_name: str
    difference: float
    confidence_interval: Optional[Tuple[float, float]] = None
    p_value: Optional[float] = None
    significant: Optional[bool] = None
    sample_size: Optional[int] = None
    additional_info: Optional[dict] = None


class FieldExtractionError(Exception):
    """
    Raised when field extraction fails.
    """
    def __init__(self, field_path: str):
        super().__init__(f"Failed to extract field at path: '{field_path}'")


class Evaluator(ABC):
    """
    Abstract Evaluator class.

    Each concrete Evaluator must implement this interface.
    """

    def __init__(self, config: EvaluatorConfig):
        self.config = config

    @abstractmethod
    def evaluate(self, y_true: Any, y_pred: Any) -> EvaluationResult:
        """
        Compute metric score for a single sample.
        """
        pass

    @abstractmethod
    def evaluate_batch(self, y_true_list: List[Any], y_pred_list: List[Any]) -> BatchEvaluationResult:
        """
        Compute batch metrics: mean, std dev, confidence interval.
        Implementation must respect self.config.metric.ci_method:
        - batch_mean: compute mean/std over per-sample scores
        - bootstrap: compute confidence intervals using bootstrap sampling
        """
        pass

    @abstractmethod
    def compare(self, y_true: List[Any], y_pred1: List[Any], y_pred2: List[Any]) -> ComparisonResult:
        """
        Compare two prediction sets and return structured comparison result.
        """
        pass

    @abstractmethod
    def estimate_sample_size(self, y_true_list: List[Any], y_pred_list: List[Any], confidence: float, margin_of_error: float) -> int:
        """
        Estimate required sample size empirically.
        """
        pass

    def check_cache(self, y_true: Any, y_pred: Any) -> Optional[EvaluationResult]:
        """
        Optional cache lookup for expensive evaluations (e.g., LLM judges).

        Concrete evaluators may override this to check DB or Redis cache.
        """
        return None

    def store_cache(self, y_true: Any, y_pred: Any, result: EvaluationResult) -> None:
        """
        Optional cache storage for expensive evaluations.

        Concrete evaluators may override this to persist evaluation results.
        """
        pass

    def to_config(self) -> EvaluatorConfig:
        """
        Serialize Evaluator to config.
        """
        return self.config

    @classmethod
    @abstractmethod
    def from_config(cls, config: EvaluatorConfig) -> "Evaluator":
        """
        Load Evaluator from config.
        """
        pass

    def extract_values(self, ground_truth_label: Any, chat_response: List[Any]) -> Tuple[Any, Any]:
        """
        Extract y_true and y_pred from input objects using extraction config.
        """
        y_true = extract_field(ground_truth_label, self.config.extraction.ground_truth_field)
        if y_true is None:
            raise FieldExtractionError(self.config.extraction.ground_truth_field)

        last_msg = chat_response[-1]
        content = getattr(last_msg, "content", None)
        if isinstance(content, str):
            y_pred = content
        else:
            y_pred = extract_field(chat_response, self.config.extraction.prediction_field)
            if y_pred is None:
                raise FieldExtractionError(self.config.extraction.prediction_field)

        return y_true, y_pred


def extract_field(obj: Any, field_path: str) -> Any:
    """
    Dotted path extractor to retrieve nested fields from dict, Pydantic model or list.
    """
    parts = field_path.split(".")
    for part in parts:
        if isinstance(obj, list) and (part.isdigit() or (part.startswith("-") and part[1:].isdigit())):
            obj = obj[int(part)]
        elif isinstance(obj, BaseModel):
            obj = getattr(obj, part, None)
        elif isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
        if obj is None:
            break
    return obj
