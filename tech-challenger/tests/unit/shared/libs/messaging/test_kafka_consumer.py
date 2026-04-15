import json
import pytest
from unittest.mock import MagicMock, patch

from libs.messaging.kafka_consumer import KafkaConsumer
from libs.messaging.exceptions import KafkaConsumeError


@pytest.fixture
def mock_consumer():
    return MagicMock()


@pytest.fixture
def consumer(mock_consumer):
    return KafkaConsumer(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        _consumer=mock_consumer,
    )


class TestKafkaConsumerInit:
    def test_raises_when_bootstrap_servers_empty(self):
        with pytest.raises(ValueError, match="bootstrap_servers"):
            KafkaConsumer(bootstrap_servers="", group_id="grp")

    def test_raises_when_group_id_empty(self):
        with pytest.raises(ValueError, match="group_id"):
            KafkaConsumer(bootstrap_servers="localhost:9092", group_id="")


class TestKafkaConsumerConsume:
    def test_consume_calls_handler_for_each_message(self, consumer, mock_consumer):
        msg1 = MagicMock()
        msg1.error.return_value = None
        msg1.value.return_value = b'{"diagram_id": "abc"}'

        msg2 = MagicMock()
        msg2.error.return_value = None
        msg2.value.return_value = b'{"diagram_id": "def"}'

        # Simulate: 2 messages then StopIteration to exit loop
        call_count = 0
        def poll_side_effect(timeout):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return msg1
            elif call_count == 2:
                return msg2
            else:
                raise StopIteration

        mock_consumer.poll.side_effect = poll_side_effect

        handler = MagicMock()
        with pytest.raises(StopIteration):
            consumer.consume("my-topic", handler)

        assert handler.call_count == 2
        handler.assert_any_call({"diagram_id": "abc"})
        handler.assert_any_call({"diagram_id": "def"})

    def test_consume_skips_none_messages(self, consumer, mock_consumer):
        call_count = 0
        def poll_side_effect(timeout):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return None
            raise StopIteration

        mock_consumer.poll.side_effect = poll_side_effect
        handler = MagicMock()
        with pytest.raises(StopIteration):
            consumer.consume("topic", handler)
        handler.assert_not_called()

    def test_consume_subscribes_to_topic(self, consumer, mock_consumer):
        mock_consumer.poll.side_effect = StopIteration
        with pytest.raises(StopIteration):
            consumer.consume("my-topic", MagicMock())
        mock_consumer.subscribe.assert_called_once_with(["my-topic"])
