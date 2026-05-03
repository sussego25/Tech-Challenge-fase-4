import os


class Settings:
    SQS_QUEUE_URL: str = os.environ.get("SQS_QUEUE_URL", "")
    S3_BUCKET: str = os.environ.get("S3_BUCKET", "")
    DYNAMODB_TABLE: str = os.environ.get("DYNAMODB_TABLE", "")
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "")
    KAFKA_TOPIC_ANALYSIS_COMPLETED: str = os.environ.get(
        "KAFKA_TOPIC_ANALYSIS_COMPLETED", "analysis-completed"
    )
    LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "sagemaker").lower()
    SAGEMAKER_ENDPOINT: str = os.environ.get("SAGEMAKER_ENDPOINT", "")
    BEDROCK_MODEL_ID: str = os.environ.get("BEDROCK_MODEL_ID", "")
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")
