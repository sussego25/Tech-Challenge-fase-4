from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AnalysisStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class ArchitectureAnalysisCompletedEvent(BaseModel):
    diagram_id: UUID
    user_id: str
    status: AnalysisStatus
    analysis_report: str | None = None
    elements_detected: list[str] = Field(default_factory=list)
    completed_at: datetime
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_status_fields(self) -> "ArchitectureAnalysisCompletedEvent":
        if self.status == AnalysisStatus.COMPLETED and not self.analysis_report:
            raise ValueError("analysis_report is required when status=completed")
        if self.status == AnalysisStatus.FAILED and not self.error_message:
            raise ValueError("error_message is required when status=failed")
        return self
