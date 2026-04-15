import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from processors.diagram_processor import DiagramProcessor
from contracts.events.analysis_requested import ArchitectureAnalysisRequestedEvent
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus
from contracts.entities.architecture_diagram import ArchitectureDiagram, DiagramStatus


DIAGRAM_ID = uuid4()
USER_ID = "user-worker-1"
S3_BUCKET = "test-bucket"
S3_KEY = f"diagrams/{USER_ID}/{DIAGRAM_ID}"


@pytest.fixture
def event() -> ArchitectureAnalysisRequestedEvent:
    return ArchitectureAnalysisRequestedEvent(
        diagram_id=DIAGRAM_ID,
        s3_bucket=S3_BUCKET,
        s3_key=S3_KEY,
        user_id=USER_ID,
        requested_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def diagram() -> ArchitectureDiagram:
    return ArchitectureDiagram(
        diagram_id=DIAGRAM_ID,
        s3_key=S3_KEY,
        s3_bucket=S3_BUCKET,
        user_id=USER_ID,
    )


@pytest.fixture
def mock_s3():
    mock = MagicMock()
    mock.download_file.return_value = b"fake-image-bytes"
    return mock


@pytest.fixture
def mock_analysis():
    mock = MagicMock()
    mock.analyze.return_value = ("Architecture analysis report", ["service", "database"])
    return mock


@pytest.fixture
def mock_repo(diagram):
    mock = MagicMock()
    mock.get.return_value = diagram
    return mock


@pytest.fixture
def mock_kafka_publisher():
    return MagicMock()


@pytest.fixture
def processor(mock_s3, mock_analysis, mock_repo, mock_kafka_publisher):
    return DiagramProcessor(
        s3_client=mock_s3,
        analysis_service=mock_analysis,
        repository=mock_repo,
        kafka_publisher=mock_kafka_publisher,
    )


class TestDiagramProcessorSuccess:
    def test_fetches_diagram_from_repository(self, processor, mock_repo, event):
        processor.process(event)
        mock_repo.get.assert_called_once_with(str(DIAGRAM_ID))

    def test_downloads_image_from_s3(self, processor, mock_s3, event):
        processor.process(event)
        mock_s3.download_file.assert_called_once_with(S3_KEY)

    def test_invokes_analysis_service(self, processor, mock_analysis, event):
        processor.process(event)
        mock_analysis.analyze.assert_called_once()

    def test_saves_diagram_twice(self, processor, mock_repo, event):
        processor.process(event)
        assert mock_repo.save.call_count == 2

    def test_marks_diagram_as_completed(self, processor, diagram, event):
        processor.process(event)
        assert diagram.status == DiagramStatus.COMPLETED

    def test_publishes_completed_event_to_kafka(self, processor, mock_kafka_publisher, event):
        processor.process(event)
        mock_kafka_publisher.publish_analysis_completed.assert_called_once()
        published: ArchitectureAnalysisCompletedEvent = (
            mock_kafka_publisher.publish_analysis_completed.call_args[0][0]
        )
        assert published.status == AnalysisStatus.COMPLETED

    def test_completed_event_has_report(self, processor, mock_kafka_publisher, event):
        processor.process(event)
        published = mock_kafka_publisher.publish_analysis_completed.call_args[0][0]
        assert published.analysis_report == "Architecture analysis report"

    def test_completed_event_has_elements(self, processor, mock_kafka_publisher, event):
        processor.process(event)
        published = mock_kafka_publisher.publish_analysis_completed.call_args[0][0]
        assert published.elements_detected == ["service", "database"]


class TestDiagramProcessorFailure:
    def test_marks_diagram_as_failed_when_analysis_raises(
        self, processor, mock_analysis, diagram, event
    ):
        mock_analysis.analyze.side_effect = RuntimeError("LLM unavailable")
        processor.process(event)
        assert diagram.status == DiagramStatus.FAILED

    def test_publishes_failed_event_to_kafka(
        self, processor, mock_analysis, mock_kafka_publisher, event
    ):
        mock_analysis.analyze.side_effect = RuntimeError("LLM unavailable")
        processor.process(event)
        published = mock_kafka_publisher.publish_analysis_completed.call_args[0][0]
        assert published.status == AnalysisStatus.FAILED

    def test_failed_event_contains_error_message(
        self, processor, mock_analysis, mock_kafka_publisher, event
    ):
        mock_analysis.analyze.side_effect = RuntimeError("LLM unavailable")
        processor.process(event)
        published = mock_kafka_publisher.publish_analysis_completed.call_args[0][0]
        assert "LLM unavailable" in published.error_message

    def test_still_saves_diagram_on_failure(
        self, processor, mock_analysis, mock_repo, event
    ):
        mock_analysis.analyze.side_effect = RuntimeError("LLM unavailable")
        processor.process(event)
        assert mock_repo.save.call_count == 2

    def test_marks_failed_when_s3_download_raises(
        self, processor, mock_s3, diagram, event
    ):
        mock_s3.download_file.side_effect = RuntimeError("S3 unreachable")
        processor.process(event)
        assert diagram.status == DiagramStatus.FAILED
