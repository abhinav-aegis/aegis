import pytest
import numpy as np
from backend.evals.evaluators._base_evaluator import (
    EvaluatorConfig,
    FieldExtractionConfig,
    MetricFunctionConfig,
    CIComputationMethod
)
from backend.evals.evaluators.sklearn import SklearnEvaluator


@pytest.fixture
def evaluator_config():
    return EvaluatorConfig(
        name="accuracy_eval",
        description="Accuracy evaluator",
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
def bootstrap_evaluator_config():
    return EvaluatorConfig(
        name="accuracy_eval_bootstrap",
        description="Accuracy evaluator with bootstrap",
        provider="sklearn",
        extraction=FieldExtractionConfig(
            ground_truth_field="value",
            prediction_field="-1.content"
        ),
        metric=MetricFunctionConfig(
            namespace="sklearn.metrics",
            name="accuracy_score",
            params={},
            ci_method=CIComputationMethod.bootstrap,
            bootstrap_iterations=100
        )
    )


def test_single_evaluate(evaluator_config):
    evaluator = SklearnEvaluator(evaluator_config)
    result = evaluator.evaluate(1, 1)
    assert result.metric_name == "accuracy_score"
    assert result.score == 1.0


def test_batch_evaluate_batch_mean(evaluator_config):
    evaluator = SklearnEvaluator(evaluator_config)
    y_true = [1, 0, 1, 1]
    y_pred = [1, 0, 0, 1]
    result = evaluator.evaluate_batch(y_true, y_pred)
    assert result.metric_name == "accuracy_score"
    assert np.isclose(result.mean, 0.75)
    assert result.sample_size == 4


def test_batch_evaluate_bootstrap(bootstrap_evaluator_config):
    evaluator = SklearnEvaluator(bootstrap_evaluator_config)
    y_true = [1, 0, 1, 1]
    y_pred = [1, 0, 0, 1]
    result = evaluator.evaluate_batch(y_true, y_pred)
    assert result.metric_name == "accuracy_score"
    assert np.isclose(result.mean, 0.75)
    assert result.confidence_interval is not None


def test_compare(evaluator_config):
    evaluator = SklearnEvaluator(evaluator_config)
    y_true = [1, 0, 1, 1]
    y_pred1 = [1, 0, 0, 1]
    y_pred2 = [1, 1, 0, 1]
    result = evaluator.compare(y_true, y_pred1, y_pred2)
    assert result.metric_name == "accuracy_score"
    assert result.difference != 0
    assert result.confidence_interval is not None


def test_sample_size_estimation(evaluator_config):
    evaluator = SklearnEvaluator(evaluator_config)
    y_true = [1, 0, 1, 1, 0, 0, 1, 1, 0, 0]
    y_pred = [1, 0, 1, 0, 0, 0, 1, 1, 1, 0]
    n = evaluator.estimate_sample_size(y_true, y_pred, confidence=0.95, margin_of_error=0.1)
    assert n > 0
