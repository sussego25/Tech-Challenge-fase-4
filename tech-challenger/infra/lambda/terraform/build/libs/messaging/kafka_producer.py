import json
import os
from typing import Any, Callable

from libs.messaging.exceptions import KafkaPublishError


class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str | None,
        _producer: Any = None,
    ) -> None:
        if not bootstrap_servers:
            raise ValueError("bootstrap_servers must be a non-empty string")
        self._bootstrap_servers = bootstrap_servers
        if _producer is not None:
            self._producer = _producer
        else:
            from confluent_kafka import Producer
            self._producer = Producer({"bootstrap.servers": bootstrap_servers})

    def publish(self, topic: str, payload: Any, key: str | None = None) -> None:
        if hasattr(payload, "model_dump_json"):
            value = payload.model_dump_json()
        elif isinstance(payload, dict):
            value = json.dumps(payload)
        else:
            value = str(payload)

        try:
            self._producer.produce(
                topic=topic,
                value=value,
                key=key,
            )
            self._producer.flush()
        except Exception as e:
            raise KafkaPublishError(f"Failed to publish message to Kafka topic '{topic}': {e}") from e
