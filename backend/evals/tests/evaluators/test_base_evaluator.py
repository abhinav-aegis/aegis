import pytest
from pydantic import BaseModel
from backend.evals.evaluators._base_evaluator import (
    EvaluatorConfig,
    FieldExtractionConfig,
    MetricFunctionConfig,
    extract_field,
    FieldExtractionError,
    CIComputationMethod,
    Evaluator
)


class DummyLabel(BaseModel):
    value: int
    meta: dict

class DummyMessage(BaseModel):
    content: str
    extra: dict

class DummyContentStructure(BaseModel):
    value: int

class DummyStructuredMessage(BaseModel):
    content: DummyContentStructure
    extra: dict

@pytest.fixture
def evaluator_config():
    return EvaluatorConfig(
        name="dummy",
        description="Dummy evaluator",
        provider="sklearn",
        extraction=FieldExtractionConfig(
            ground_truth_field="value",
            prediction_field="-1.content"
        ),
        metric=MetricFunctionConfig(
            namespace="sklearn.metrics",
            name="accuracy_score",
            params={},
            ci_method=CIComputationMethod.batch_mean
        )
    )

@pytest.fixture
def structured_evaluator_config():
    return EvaluatorConfig(
        name="dummy",
        description="Dummy evaluator",
        provider="sklearn",
        extraction=FieldExtractionConfig(
            ground_truth_field="value",
            prediction_field="-1.content.value"
        ),
        metric=MetricFunctionConfig(
            namespace="sklearn.metrics",
            name="accuracy_score",
            params={},
            ci_method=CIComputationMethod.batch_mean
        )
    )

class DummyEvaluator(Evaluator):
    def evaluate(self, y_true, y_pred):
        pass
    def evaluate_batch(self, y_true_list, y_pred_list):
        pass
    def compare(self, y_true, y_pred1, y_pred2):
        pass
    def estimate_sample_size(self, y_true_list, y_pred_list, confidence, margin_of_error):
        pass
    @classmethod
    def from_config(cls, config):
        return cls(config)

def test_extract_field_simple():
    data = {"a": {"b": 5}}
    assert extract_field(data, "a.b") == 5


def test_extract_field_list():
    data = [{"value": 1}, {"value": 2}]
    assert extract_field(data, "1.value") == 2


def test_extract_field_pydantic():
    label = DummyLabel(value=10, meta={"x": 1})
    assert extract_field(label, "meta.x") == 1


def test_extract_field_invalid():
    data = {"a": {"b": 5}}
    assert extract_field(data, "a.c") is None


def test_field_extraction_error(evaluator_config):
    evaluator = DummyEvaluator(evaluator_config)

    label = DummyLabel(value=10, meta={"x": 1})
    messages = [
        DummyMessage(content="output", extra={}),
        DummyMessage(content="wrong", extra={})
    ]

    y_true, y_pred = evaluator.extract_values(label, messages)
    assert y_true == 10
    assert y_pred == "wrong"

    messages = [
        DummyMessage(content="output", extra={}),
        DummyMessage(content={"value", "wrong"}, extra={})
    ]

    evaluator.config.extraction.prediction_field = "-1.content.value"
    y_true, y_pred = evaluator.extract_values(label, messages)
    assert y_true == 10
    assert y_pred == "wrong"

    evaluator.config.extraction.prediction_field = "-1.content.nonexistent"
    with pytest.raises(FieldExtractionError):
        evaluator.extract_values(label, messages)

def test_field_extraction_error_structured(structured_evaluator_config):
    evaluator = DummyEvaluator(structured_evaluator_config)

    label = DummyLabel(value=10, meta={"x": 1})

    structured_messages = [
        DummyStructuredMessage(content=DummyContentStructure(value=5), extra={}),
        DummyStructuredMessage(content=DummyContentStructure(value=15), extra={})
    ]
    y_true, y_pred = evaluator.extract_values(label, structured_messages)
    assert y_true == 10
    assert y_pred == 15

    evaluator.config.extraction.prediction_field = "-1.nonexistent"
    with pytest.raises(FieldExtractionError):
        evaluator.extract_values(label, structured_messages)

def test_to_from_config(evaluator_config):
    from backend.evals.evaluators._base_evaluator import Evaluator

    class DummyEvaluator(Evaluator):
        def evaluate(self, y_true, y_pred):
            pass
        def evaluate_batch(self, y_true_list, y_pred_list):
            pass
        def compare(self, y_true, y_pred1, y_pred2):
            pass
        def estimate_sample_size(self, y_true_list, y_pred_list, confidence, margin_of_error):
            pass
        @classmethod
        def from_config(cls, config):
            return cls(config)

    evaluator = DummyEvaluator(evaluator_config)
    config = evaluator.to_config()
    assert config == evaluator_config
