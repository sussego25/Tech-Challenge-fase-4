from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent
from libs.messaging.kafka_producer import KafkaProducer


class KafkaPublisher:
    def __init__(self, producer: KafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    def publish_analysis_completed(self, event: ArchitectureAnalysisCompletedEvent) -> None:
        self._producer.publish(self._topic, event)
