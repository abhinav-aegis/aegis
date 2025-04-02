"""
Sklearn Evaluator Implementation.

Evaluates classification/regression metrics using scikit-learn. Supports batch CI computation and sample size
estimation.
"""

import importlib
import numpy as np
from scipy.stats import norm
from typing import Any, List
from backend.evals.evaluators._base_evaluator import (
    Evaluator,
    EvaluatorConfig,
    EvaluationResult,
    BatchEvaluationResult,
    ComparisonResult
)

class SklearnEvaluator(Evaluator):
    """
    Evaluator for scikit-learn metrics.
    """

    def __init__(self, config: EvaluatorConfig):
        super().__init__(config)
        module = importlib.import_module(config.metric.namespace)
        self.metric_fn = getattr(module, config.metric.name)

    def evaluate(self, y_true: Any, y_pred: Any) -> EvaluationResult:
        """
        Compute metric score for a single sample.
        """
        score = self.metric_fn([y_true], [y_pred], **self.config.metric.params)
        return EvaluationResult(score=score, metric_name=self.config.metric.name)

    def evaluate_batch(self, y_true_list: List[Any], y_pred_list: List[Any]) -> BatchEvaluationResult:
        """
        Compute batch mean, std dev, and confidence interval.
        """
        scores = [
            self.metric_fn([yt], [yp], **self.config.metric.params)
            for yt, yp in zip(y_true_list, y_pred_list)
        ]
        mean_score = np.mean(scores)
        std_dev = np.std(scores, ddof=1) if len(scores) > 1 else 0.0

        ci_method = self.config.metric.ci_method
        confidence = 0.95

        if ci_method == "batch_mean":
            ci = norm.interval(confidence, loc=mean_score, scale=std_dev / np.sqrt(len(scores))) if len(scores) > 1 else (mean_score, mean_score)
        elif ci_method == "bootstrap":
            bootstrap_scores = []
            for _ in range(self.config.metric.bootstrap_iterations):
                indices = np.random.choice(len(scores), len(scores), replace=True)
                sample_mean = np.mean(np.array(scores)[indices])
                bootstrap_scores.append(sample_mean)
            lower = np.percentile(bootstrap_scores, 2.5)
            upper = np.percentile(bootstrap_scores, 97.5)
            ci = (lower, upper)
        else:
            raise ValueError(f"Unsupported ci_method: {ci_method}")

        return BatchEvaluationResult(
            metric_name=self.config.metric.name,
            mean=mean_score,
            std_dev=std_dev,
            confidence_interval=ci,
            sample_size=len(scores)
        )

    def compare(self, y_true: List[Any], y_pred1: List[Any], y_pred2: List[Any]) -> ComparisonResult:
        """
        Compare two prediction sets using paired difference.
        """
        scores1 = [self.metric_fn([yt], [yp1], **self.config.metric.params) for yt, yp1 in zip(y_true, y_pred1)]
        scores2 = [self.metric_fn([yt], [yp2], **self.config.metric.params) for yt, yp2 in zip(y_true, y_pred2)]
        differences = np.array(scores1) - np.array(scores2)

        mean_diff = np.mean(differences)
        std_dev = np.std(differences, ddof=1) if len(differences) > 1 else 0.0
        confidence = 0.95
        ci = norm.interval(confidence, loc=mean_diff, scale=std_dev / np.sqrt(len(differences))) if len(differences) > 1 else (mean_diff, mean_diff)

        return ComparisonResult(
            metric_name=self.config.metric.name,
            difference=mean_diff,
            confidence_interval=ci,
            sample_size=len(differences)
        )

    def estimate_sample_size(self, y_true_list: List[Any], y_pred_list: List[Any], confidence: float, margin_of_error: float) -> int:
        """
        Empirically estimate sample size based on observed variance.
        """
        scores = [
            self.metric_fn([yt], [yp], **self.config.metric.params)
            for yt, yp in zip(y_true_list, y_pred_list)
        ]
        observed_std = np.std(scores, ddof=1) if len(scores) > 1 else 0.0
        z = norm.ppf(1 - (1 - confidence) / 2)
        if observed_std == 0.0:
            return len(scores)
        n = (z * observed_std / margin_of_error) ** 2
        return int(np.ceil(n))

    def check_cache(self, y_true: Any, y_pred: Any) -> None:
        """
        No caching required for sklearn metrics.
        """
        return None

    def store_cache(self, y_true: Any, y_pred: Any, result: EvaluationResult) -> None:
        """
        No caching required for sklearn metrics.
        """
        pass

    @classmethod
    def from_config(cls, config: EvaluatorConfig) -> "SklearnEvaluator":
        """
        Load evaluator from config.
        """
        return cls(config)
