import logging

import boto3

from application.notify_use_case import NotifyAnalysisCompletedUseCase
from config.settings import Settings
from infrastructure.notification_repository import NotificationRepository
from infrastructure.notification_sender import NotificationSender
from libs.messaging.kafka_consumer import KafkaConsumer
from messaging.kafka_consumer import KafkaAnalysisConsumer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    table = dynamodb.Table(settings.DYNAMODB_TABLE)
    repo = NotificationRepository(table=table)

    sender = NotificationSender()
    use_case = NotifyAnalysisCompletedUseCase(sender=sender, repository=repo)

    kafka_consumer = KafkaConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
    )
    consumer = KafkaAnalysisConsumer(kafka_consumer=kafka_consumer, use_case=use_case)

    logger.info("Notification service starting...")
    consumer.run(settings.KAFKA_TOPIC_ANALYSIS_COMPLETED)


if __name__ == "__main__":
    main()
