import logging

import boto3

from config.settings import Settings
from consumers.sqs_consumer import SQSConsumer
from domain.analysis_service import AnalysisService
from infrastructure.diagram_repository import DynamoDBDiagramRepository
from infrastructure.kafka_publisher import KafkaPublisher
from libs.aws.s3_client import S3Client
from libs.aws.sqs_client import SQSClient
from libs.llm.sagemaker_client import LLMClient
from libs.messaging.kafka_producer import KafkaProducer
from processors.diagram_processor import DiagramProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    s3_client = S3Client(bucket_name=settings.S3_BUCKET, region=settings.AWS_REGION)
    sqs_client = SQSClient(queue_url=settings.SQS_QUEUE_URL, region=settings.AWS_REGION)
    llm_client = LLMClient(endpoint_name=settings.SAGEMAKER_ENDPOINT, region=settings.AWS_REGION)
    kafka_producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    table = dynamodb.Table(settings.DYNAMODB_TABLE)
    repo = DynamoDBDiagramRepository(table=table)

    kafka_publisher = KafkaPublisher(
        producer=kafka_producer,
        topic=settings.KAFKA_TOPIC_ANALYSIS_COMPLETED,
    )
    analysis_service = AnalysisService(llm_client=llm_client)
    processor = DiagramProcessor(
        s3_client=s3_client,
        analysis_service=analysis_service,
        repository=repo,
        kafka_publisher=kafka_publisher,
    )
    consumer = SQSConsumer(sqs_client=sqs_client, processor=processor)

    logger.info("Worker service starting...")
    consumer.run()


if __name__ == "__main__":
    main()
