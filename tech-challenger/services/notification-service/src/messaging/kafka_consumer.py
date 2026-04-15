import logging
from typing import Callable

from application.notify_use_case import NotifyAnalysisCompletedUseCase
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent
from libs.messaging.kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)


class KafkaAnalysisConsumer:
    def __init__(
        self,
        kafka_consumer: KafkaConsumer,
        use_case: NotifyAnalysisCompletedUseCase,
    ) -> None:
        self._kafka = kafka_consumer
        self._use_case = use_case

    def run(self, topic: str) -> None:
        logger.info("Notification service consuming topic: %s", topic)
        self._kafka.consume(topic, self._handle_message)

    def _handle_message(self, payload: dict) -> None:
        try:
            event = ArchitectureAnalysisCompletedEvent(**payload)
            self._use_case.execute(event)
        except Exception as exc:
            logger.error("Failed to handle Kafka message: %s", exc)
