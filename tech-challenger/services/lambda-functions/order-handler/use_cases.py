from datetime import datetime, timezone
from uuid import uuid4

from contracts.entities.architecture_diagram import ArchitectureDiagram
from contracts.events.analysis_requested import ArchitectureAnalysisRequestedEvent
from libs.aws.s3_client import S3Client
from libs.aws.sqs_client import SQSClient
from repositories import DynamoDBDiagramRepository


class ProcessDiagramUploadUseCase:
    def __init__(
        self,
        s3_client: S3Client,
        sqs_client: SQSClient,
        repository: DynamoDBDiagramRepository,
        s3_bucket: str,
    ) -> None:
        self._s3 = s3_client
        self._sqs = sqs_client
        self._repo = repository
        self._s3_bucket = s3_bucket

    def execute(self, image_data: bytes, content_type: str, user_id: str) -> ArchitectureDiagram:
        diagram_id = uuid4()
        s3_key = f"diagrams/{user_id}/{diagram_id}"

        diagram = ArchitectureDiagram(
            diagram_id=diagram_id,
            s3_key=s3_key,
            s3_bucket=self._s3_bucket,
            user_id=user_id,
        )

        self._s3.upload_file(image_data, s3_key, content_type=content_type)

        event = ArchitectureAnalysisRequestedEvent(
            diagram_id=diagram_id,
            s3_bucket=self._s3_bucket,
            s3_key=s3_key,
            user_id=user_id,
            requested_at=datetime.now(timezone.utc),
        )
        self._sqs.send_message(event)

        self._repo.save(diagram)

        return diagram
