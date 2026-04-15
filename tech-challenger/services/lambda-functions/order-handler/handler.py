import base64
import json
import logging
from typing import Any

import boto3

from config import Config
from repositories import DynamoDBDiagramRepository
from use_cases import ProcessDiagramUploadUseCase
from libs.aws.s3_client import S3Client
from libs.aws.sqs_client import SQSClient

logger = logging.getLogger(__name__)

_ACCEPTED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

_use_case: ProcessDiagramUploadUseCase | None = None


def _get_use_case() -> ProcessDiagramUploadUseCase:
    global _use_case
    if _use_case is None:
        config = Config()
        s3_client = S3Client(bucket_name=config.S3_BUCKET, region=config.AWS_REGION)
        sqs_client = SQSClient(queue_url=config.SQS_QUEUE_URL, region=config.AWS_REGION)
        dynamodb = boto3.resource("dynamodb", region_name=config.AWS_REGION)
        table = dynamodb.Table(config.DYNAMODB_TABLE)
        repo = DynamoDBDiagramRepository(table=table)
        _use_case = ProcessDiagramUploadUseCase(
            s3_client=s3_client,
            sqs_client=sqs_client,
            repository=repo,
            s3_bucket=config.S3_BUCKET,
        )
    return _use_case


def _json_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}

    user_id = headers.get("x-user-id", "").strip()
    if not user_id:
        return _json_response(400, {"error": "Missing required header: x-user-id"})

    content_type = headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type not in _ACCEPTED_CONTENT_TYPES:
        return _json_response(
            400,
            {"error": f"Unsupported content type. Accepted: {sorted(_ACCEPTED_CONTENT_TYPES)}"},
        )

    raw_body = event.get("body")
    if not raw_body:
        return _json_response(400, {"error": "Request body is required"})

    try:
        if event.get("isBase64Encoded"):
            image_data = base64.b64decode(raw_body)
        else:
            image_data = raw_body.encode() if isinstance(raw_body, str) else raw_body
    except Exception:
        return _json_response(400, {"error": "Failed to decode request body"})

    try:
        use_case = _get_use_case()
        diagram = use_case.execute(image_data, content_type, user_id)
    except Exception:
        logger.exception("Unexpected error processing diagram upload")
        return _json_response(500, {"error": "Internal server error"})

    return _json_response(
        202,
        {
            "diagram_id": str(diagram.diagram_id),
            "status": diagram.status.value,
            "message": "Diagram upload accepted. Analysis is in progress.",
        },
    )
