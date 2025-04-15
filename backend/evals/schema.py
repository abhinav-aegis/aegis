from typing import Optional, List
from uuid import UUID
from pydantic import types as pydantic_types
from backend.common.utils.partial import optional
from .models import (
    GroundTruthDatasetBase,
    GroundTruthItemBase,
    EvaluationJobBase,
    EvaluationResultBase,
    EvaluationCacheBase,
    UserFeedbackBase,
    EvaluationJobStatus
)

# ---- Dataset Schemas ----

class IGroundTruthDatasetCreate(GroundTruthDatasetBase):
    pass

class IGroundTruthDatasetCreateWithItems(GroundTruthDatasetBase):
    items: List["IGroundTruthItemCreate"]

@optional()
class IGroundTruthDatasetUpdate(GroundTruthDatasetBase):
    pass

class IGroundTruthDatasetRead(GroundTruthDatasetBase):
    id: UUID

class IGroundTruthDatasetList(GroundTruthDatasetBase):
    id: UUID

class IGroundTruthItemCreate(GroundTruthItemBase):
    pass

@optional()
class IGroundTruthItemUpdate(GroundTruthItemBase):
    pass

class IGroundTruthItemRead(GroundTruthItemBase):
    id: UUID

class IGroundTruthDatasetReadDetailed(GroundTruthDatasetBase):
    id: UUID
    items: List[IGroundTruthItemRead]


# ---- Evaluation Job Schemas ----

class IEvaluationJobCreate(EvaluationJobBase):
    pass

@optional()
class IEvaluationJobUpdate(EvaluationJobBase):
    pass

class IEvaluationResultRead(EvaluationResultBase):
    id: UUID

class IEvaluationJobRead(EvaluationJobBase):
    id: UUID
    status: EvaluationJobStatus
    completed_at: Optional[pydantic_types.AwareDatetime]

class IEvaluationJobReadDetailed(EvaluationJobBase):
    id: UUID
    status: EvaluationJobStatus
    completed_at: Optional[pydantic_types.AwareDatetime]
    results: List[IEvaluationResultRead]


# ---- Evaluation Result Schemas ----

class IEvaluationResultCreate(EvaluationResultBase):
    pass


# ---- Evaluation Cache (read only) ----

class IEvaluationCacheRead(EvaluationCacheBase):
    id: UUID
    created_at: pydantic_types.AwareDatetime


# ---- User Feedback ----

class IUserFeedbackCreate(UserFeedbackBase):
    pass

class IUserFeedbackRead(UserFeedbackBase):
    id: UUID
    created_at: pydantic_types.AwareDatetime

@optional()
class IUserFeedbackUpdate(UserFeedbackBase):
    pass
