from datetime import datetime, timezone

from contracts.entities.architecture_diagram import ArchitectureDiagram
from contracts.events.analysis_requested import ArchitectureAnalysisRequestedEvent
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus
from domain.analysis_service import AnalysisService
from infrastructure.diagram_repository import DynamoDBDiagramRepository
from infrastructure.kafka_publisher import KafkaPublisher
from libs.aws.s3_client import S3Client


class DiagramProcessor:
    def __init__(
        self,
        s3_client: S3Client,
        analysis_service: AnalysisService,
        repository: DynamoDBDiagramRepository,
        kafka_publisher: KafkaPublisher,
    ) -> None:
        self._s3 = s3_client
        self._analysis = analysis_service
        self._repo = repository
        self._kafka = kafka_publisher

    def process(self, event: ArchitectureAnalysisRequestedEvent) -> None:
        diagram: ArchitectureDiagram = self._repo.get(str(event.diagram_id))

        diagram.mark_processing()
        self._repo.save(diagram)

        try:
            image_data = self._s3.download_file(event.s3_key, bucket=event.s3_bucket)
            report, elements = self._analysis.analyze(image_data, str(event.diagram_id))
            diagram.mark_completed(report, elements)
            completed_event = ArchitectureAnalysisCompletedEvent(
                diagram_id=event.diagram_id,
                status=AnalysisStatus.COMPLETED,
                analysis_report=report,
                elements_detected=elements,
                completed_at=datetime.now(timezone.utc),
            )
        except Exception as exc:
            error_msg = str(exc)
            diagram.mark_failed(error_msg)
            completed_event = ArchitectureAnalysisCompletedEvent(
                diagram_id=event.diagram_id,
                status=AnalysisStatus.FAILED,
                completed_at=datetime.now(timezone.utc),
                error_message=error_msg,
            )

        self._repo.save(diagram)
        self._kafka.publish_analysis_completed(completed_event)
