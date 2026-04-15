import os


class Settings:
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "")
    KAFKA_TOPIC_ANALYSIS_COMPLETED: str = os.environ.get(
        "KAFKA_TOPIC_ANALYSIS_COMPLETED", "analysis-completed"
    )
    KAFKA_GROUP_ID: str = os.environ.get("KAFKA_GROUP_ID", "notification-service")
    DYNAMODB_TABLE: str = os.environ.get("DYNAMODB_TABLE", "")
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")
