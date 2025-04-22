from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey
from sqlmodel import Field, Relationship, JSON, SQLModel
from enum import Enum

from backend.common.models.base_uuid_model import BaseUUIDModel


# ---------- Enums ----------

class EvaluationJobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FeedbackType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    RATING = "rating"


# ---------- Ground Truth Dataset ----------

class GroundTruthDatasetBase(SQLModel):
    """
    Metadata about a Ground Truth Dataset.

    Contains labeled examples for evaluating agent performance.
    """
    task_id: UUID = Field(nullable=False, index=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    label_uri: Optional[str] = Field(default=None)


class GroundTruthDataset(GroundTruthDatasetBase, BaseUUIDModel, table=True):
    items: List["GroundTruthItem"] = Relationship(
        back_populates="dataset", sa_relationship_kwargs={"lazy": "selectin"}
    )


class GroundTruthItemBase(SQLModel):
    """
    Stores a single labeled data pair.

    Contains composite input keys and expected evaluation label.
    """
    dataset_id: UUID = Field(ForeignKey("groundtruthdataset.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Optional[UUID] = Field(nullable=True, index=True)
    input_data: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))  # Key-value pairs for input data. Allows reconstruction of StructuredData from Autogen
    ground_truth_label: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))


class GroundTruthItem(GroundTruthItemBase, BaseUUIDModel, table=True):
    dataset: Optional[GroundTruthDataset] = Relationship(
        back_populates="items", sa_relationship_kwargs={"lazy": "selectin"}
    )


# ---------- Evaluation Job ----------

class EvaluationJobBase(SQLModel):
    """
    Represents an evaluation batch job.
    """
    tenant_id: Optional[UUID] = Field(nullable=True, index=True)
    task_id: UUID = Field(nullable=False, index=True)
    dataset_id: Optional[UUID] = Field(ForeignKey("groundtruthdataset.id", ondelete="SET NULL"), nullable=True, index=True)
    team_ids: List[UUID] = Field(sa_column=Column(JSON, nullable=False))
    metrics: List[str] = Field(sa_column=Column(JSON, nullable=False))
    status: EvaluationJobStatus = Field(default=EvaluationJobStatus.PENDING, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    evaluation_component: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))


class EvaluationJob(EvaluationJobBase, BaseUUIDModel, table=True):
    results: List["EvaluationResult"] = Relationship(
        back_populates="job", sa_relationship_kwargs={"lazy": "selectin"}
    )


# ---------- Evaluation Result ----------

class EvaluationResultBase(SQLModel):
    """
    Stores evaluation score per session/team.

    Links to Evaluation Job and Dataset.
    """
    job_id: UUID = Field(ForeignKey("evaluationjob.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: UUID = Field(nullable=False, index=True)
    team_id: UUID = Field(nullable=False, index=True)
    metric_name: str = Field(nullable=False, index=True)
    score: float = Field(nullable=False)
    std_dev: Optional[float] = Field(default=None)
    confidence_interval: Optional[Tuple[float, float]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    dataset_id: Optional[UUID] = Field(ForeignKey("groundtruthdataset.id", ondelete="SET NULL"), nullable=True, index=True)


class EvaluationResult(EvaluationResultBase, BaseUUIDModel, table=True):
    job: Optional[EvaluationJob] = Relationship(
        back_populates="results", sa_relationship_kwargs={"lazy": "selectin"}
    )


# ---------- Evaluation Cache ----------

class EvaluationCacheBase(SQLModel):
    """
    Caches expensive evaluation results.
    """
    evaluator_config_hash: str = Field(nullable=False, index=True)
    input_hash: str = Field(nullable=False, index=True)
    result: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))


class EvaluationCache(EvaluationCacheBase, BaseUUIDModel, table=True):
    pass


# ---------- User Feedback ----------

class UserFeedbackBase(SQLModel):
    """
    Captures human feedback on evaluations.

    Can later be used to filter or improve Golden Datasets.
    """
    tenant_id: Optional[UUID] = Field(nullable=True, index=True)
    session_id: Optional[UUID] = Field(nullable=True, index=True)
    team_id: Optional[UUID] = Field(nullable=True, index=True)
    feedback_type: FeedbackType = Field(nullable=False)
    rating: Optional[float] = Field(default=None)
    comments: Optional[str] = Field(default=None)


class UserFeedback(UserFeedbackBase, BaseUUIDModel, table=True):
    pass
