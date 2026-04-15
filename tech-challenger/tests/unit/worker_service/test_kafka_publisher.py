import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from infrastructure.kafka_publisher import KafkaPublisher
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus


@pytest.fixture
def mock_producer():
    return MagicMock()


@pytest.fixture
def completed_event():
    return ArchitectureAnalysisCompletedEvent(
        diagram_id=uuid4(),
        user_id="user-1",
        status=AnalysisStatus.COMPLETED,
        analysis_report="Architecture report",
        elements_detected=["service"],
        completed_at=datetime.now(timezone.utc),
    )


class TestKafkaPublisher:
    def test_publishes_to_correct_topic(self, mock_producer, completed_event):
        publisher = KafkaPublisher(producer=mock_producer, topic="analysis-completed")
        publisher.publish_analysis_completed(completed_event)
        mock_producer.publish.assert_called_once_with("analysis-completed", completed_event)

    def test_publishes_completed_event(self, mock_producer, completed_event):
        publisher = KafkaPublisher(producer=mock_producer, topic="events")
        publisher.publish_analysis_completed(completed_event)
        _, called_event = mock_producer.publish.call_args[0]
        assert called_event is completed_event

    def test_different_topics_are_respected(self, mock_producer, completed_event):
        publisher = KafkaPublisher(producer=mock_producer, topic="my-custom-topic")
        publisher.publish_analysis_completed(completed_event)
        topic, _ = mock_producer.publish.call_args[0]
        assert topic == "my-custom-topic"
