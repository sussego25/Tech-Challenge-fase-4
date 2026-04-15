import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from contracts.events import ArchitectureAnalysisCompletedEvent, AnalysisStatus


class TestArchitectureAnalysisCompletedEvent:

    def test_create_completed_status(self):
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="user-123",
            status=AnalysisStatus.COMPLETED,
            analysis_report="# Report\n\nDiagram looks good.",
            elements_detected=["EC2", "RDS", "S3"],
            completed_at=datetime.now(timezone.utc),
        )
        assert event.status == AnalysisStatus.COMPLETED
        assert event.analysis_report == "# Report\n\nDiagram looks good."
        assert event.error_message is None

    def test_create_failed_status(self):
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="user-123",
            status=AnalysisStatus.FAILED,
            completed_at=datetime.now(timezone.utc),
            error_message="SageMaker endpoint timeout",
        )
        assert event.status == AnalysisStatus.FAILED
        assert event.error_message == "SageMaker endpoint timeout"
        assert event.analysis_report is None

    def test_completed_without_analysis_report_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            ArchitectureAnalysisCompletedEvent(
                diagram_id=uuid4(),
                user_id="user-123",
                status=AnalysisStatus.COMPLETED,
                completed_at=datetime.now(timezone.utc),
            )
        assert "analysis_report" in str(exc_info.value)

    def test_failed_without_error_message_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            ArchitectureAnalysisCompletedEvent(
                diagram_id=uuid4(),
                user_id="user-123",
                status=AnalysisStatus.FAILED,
                completed_at=datetime.now(timezone.utc),
            )
        assert "error_message" in str(exc_info.value)

    def test_elements_detected_empty_list_is_valid(self):
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="user-123",
            status=AnalysisStatus.COMPLETED,
            analysis_report="No elements found.",
            elements_detected=[],
            completed_at=datetime.now(timezone.utc),
        )
        assert event.elements_detected == []

    def test_elements_detected_defaults_to_empty_list(self):
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="user-123",
            status=AnalysisStatus.COMPLETED,
            analysis_report="Report text.",
            completed_at=datetime.now(timezone.utc),
        )
        assert event.elements_detected == []

    def test_missing_diagram_id_raises_error(self):
        with pytest.raises(ValidationError):
            ArchitectureAnalysisCompletedEvent(
                user_id="user-123",
                status=AnalysisStatus.COMPLETED,
                analysis_report="Report.",
                completed_at=datetime.now(timezone.utc),
            )

    def test_missing_user_id_raises_error(self):
        with pytest.raises(ValidationError):
            ArchitectureAnalysisCompletedEvent(
                diagram_id=uuid4(),
                status=AnalysisStatus.COMPLETED,
                analysis_report="Report.",
                completed_at=datetime.now(timezone.utc),
            )

    def test_invalid_status_raises_error(self):
        with pytest.raises(ValidationError):
            ArchitectureAnalysisCompletedEvent(
                diagram_id=uuid4(),
                user_id="user-123",
                status="in_progress",
                analysis_report="Report.",
                completed_at=datetime.now(timezone.utc),
            )

    def test_json_round_trip_completed(self):
        diagram_id = uuid4()
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=diagram_id,
            user_id="user-456",
            status=AnalysisStatus.COMPLETED,
            analysis_report="# Architecture Report",
            elements_detected=["Lambda", "SQS", "DynamoDB"],
            completed_at=datetime.now(timezone.utc),
        )
        json_str = event.model_dump_json()
        restored = ArchitectureAnalysisCompletedEvent.model_validate_json(json_str)
        assert restored.diagram_id == diagram_id
        assert restored.status == AnalysisStatus.COMPLETED
        assert restored.elements_detected == ["Lambda", "SQS", "DynamoDB"]

    def test_json_round_trip_failed(self):
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="user-789",
            status=AnalysisStatus.FAILED,
            completed_at=datetime.now(timezone.utc),
            error_message="Model inference failed",
        )
        json_str = event.model_dump_json()
        restored = ArchitectureAnalysisCompletedEvent.model_validate_json(json_str)
        assert restored.status == AnalysisStatus.FAILED
        assert restored.error_message == "Model inference failed"
