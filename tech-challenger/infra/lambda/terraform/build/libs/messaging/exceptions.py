class KafkaPublishError(Exception):
    """Raised when a message cannot be published to Kafka."""


class KafkaConsumeError(Exception):
    """Raised when consuming messages from Kafka fails."""
