import json
import os
from typing import Any, Callable

from libs.messaging.exceptions import KafkaConsumeError


class KafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str | None,
        group_id: str | None,
        _consumer: Any = None,
    ) -> None:
        if not bootstrap_servers:
            raise ValueError("bootstrap_servers must be a non-empty string")
        if not group_id:
            raise ValueError("group_id must be a non-empty string")
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        if _consumer is not None:
            self._consumer = _consumer
        else:
            from confluent_kafka import Consumer
            self._consumer = Consumer({
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
            })

    def consume(self, topic: str, handler: Callable[[dict], None], poll_timeout: float = 1.0) -> None:
        self._consumer.subscribe([topic])
        while True:
            msg = self._consumer.poll(timeout=poll_timeout)
            if msg is None:
                continue
            if msg.error():
                raise KafkaConsumeError(f"Kafka consumer error: {msg.error()}")
            payload = json.loads(msg.value())
            handler(payload)
