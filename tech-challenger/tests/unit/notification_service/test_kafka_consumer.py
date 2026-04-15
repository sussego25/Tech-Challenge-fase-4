import json
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from messaging.kafka_consumer import KafkaAnalysisConsumer
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus


DIAGRAM_ID = uuid4()
USER_ID = "user-kafka-1"


def _make_completed_payload() -> dict:
    event = ArchitectureAnalysisCompletedEvent(
        diagram_id=DIAGRAM_ID,
        user_id=USER_ID,
        status=AnalysisStatus.COMPLETED,
        analysis_report="Report content.",
        elements_detected=["service"],
        completed_at=datetime.now(timezone.utc),
    )
    return json.loads(event.model_dump_json())


@pytest.fixture
def mock_kafka():
    return MagicMock()


@pytest.fixture
def mock_use_case():
    return MagicMock()


@pytest.fixture
def consumer(mock_kafka, mock_use_case):
    return KafkaAnalysisConsumer(kafka_consumer=mock_kafka, use_case=mock_use_case)


class TestKafkaAnalysisConsumerRun:
    def test_run_calls_consume_with_topic(self, consumer, mock_kafka):
        consumer.run("my-topic")
        mock_kafka.consume.assert_called_once()
        topic = mock_kafka.consume.call_args[0][0]
        assert topic == "my-topic"

    def test_run_passes_handler_callable(self, consumer, mock_kafka):
        consumer.run("test-topic")
        _, handler = mock_kafka.consume.call_args[0]
        assert callable(handler)


class TestKafkaAnalysisConsumerHandleMessage:
    def test_handle_message_calls_use_case(self, consumer, mock_use_case):
        consumer._handle_message(_make_completed_payload())
        mock_use_case.execute.assert_called_once()

    def test_handle_message_passes_correct_event_type(self, consumer, mock_use_case):
        consumer._handle_message(_make_completed_payload())
        passed_event = mock_use_case.execute.call_args[0][0]
        assert isinstance(passed_event, ArchitectureAnalysisCompletedEvent)

    def test_handle_message_preserves_diagram_id(self, consumer, mock_use_case):
        consumer._handle_message(_make_completed_payload())
        passed_event = mock_use_case.execute.call_args[0][0]
        assert passed_event.diagram_id == DIAGRAM_ID

    def test_handle_message_with_invalid_payload_does_not_crash(self, consumer, mock_use_case):
        consumer._handle_message({"invalid": "data"})
        mock_use_case.execute.assert_not_called()
