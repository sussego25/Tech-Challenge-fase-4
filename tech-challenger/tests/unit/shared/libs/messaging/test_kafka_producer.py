import json
import pytest
from unittest.mock import MagicMock, patch, call

from libs.messaging.kafka_producer import KafkaProducer
from libs.messaging.exceptions import KafkaPublishError


@pytest.fixture
def mock_producer():
    return MagicMock()


@pytest.fixture
def producer(mock_producer):
    return KafkaProducer(bootstrap_servers="localhost:9092", _producer=mock_producer)


class TestKafkaProducerInit:
    def test_raises_when_bootstrap_servers_empty(self):
        with pytest.raises(ValueError, match="bootstrap_servers"):
            KafkaProducer(bootstrap_servers="")

    def test_raises_when_bootstrap_servers_none(self):
        with pytest.raises(ValueError, match="bootstrap_servers"):
            KafkaProducer(bootstrap_servers=None)


class TestKafkaProducerPublish:
    def test_publish_dict_sends_json(self, producer, mock_producer):
        payload = {"diagram_id": "abc", "status": "completed"}
        producer.publish("my-topic", payload)
        mock_producer.produce.assert_called_once()
        call_kwargs = mock_producer.produce.call_args.kwargs
        assert call_kwargs["topic"] == "my-topic"
        assert json.loads(call_kwargs["value"]) == payload

    def test_publish_pydantic_model_serializes_correctly(self, producer, mock_producer):
        from contracts.events import ArchitectureAnalysisCompletedEvent, AnalysisStatus
        from datetime import datetime, timezone
        from uuid import uuid4
        event = ArchitectureAnalysisCompletedEvent(
            diagram_id=uuid4(),
            user_id="u1",
            status=AnalysisStatus.COMPLETED,
            analysis_report="Report.",
            completed_at=datetime.now(timezone.utc),
        )
        producer.publish("results-topic", event, key=str(event.diagram_id))
        call_kwargs = mock_producer.produce.call_args.kwargs
        body = json.loads(call_kwargs["value"])
        assert body["status"] == "completed"
        assert call_kwargs["key"] == str(event.diagram_id)

    def test_publish_calls_flush(self, producer, mock_producer):
        producer.publish("topic", {"key": "val"})
        mock_producer.flush.assert_called_once()

    def test_publish_raises_kafka_publish_error_on_exception(self, producer, mock_producer):
        mock_producer.produce.side_effect = Exception("Broker unavailable")
        with pytest.raises(KafkaPublishError, match="Failed to publish"):
            producer.publish("topic", {"key": "val"})
