import logging

from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus
from domain.notification import Notification
from infrastructure.notification_repository import NotificationRepository
from infrastructure.notification_sender import NotificationSender

logger = logging.getLogger(__name__)


class NotifyAnalysisCompletedUseCase:
    def __init__(self, sender: NotificationSender, repository: NotificationRepository) -> None:
        self._sender = sender
        self._repo = repository

    def execute(self, event: ArchitectureAnalysisCompletedEvent) -> None:
        message = self._format_message(event)
        notification = Notification(
            diagram_id=event.diagram_id,
            user_id=event.user_id,
            message=message,
        )

        try:
            self._sender.send(notification)
            notification.mark_sent()
        except Exception:
            logger.exception("Failed to send notification for diagram %s", event.diagram_id)
            notification.mark_failed()

        self._repo.save(notification)

    def _format_message(self, event: ArchitectureAnalysisCompletedEvent) -> str:
        if event.status == AnalysisStatus.COMPLETED:
            elements_str = ", ".join(event.elements_detected) if event.elements_detected else "none"
            return (
                f"Your architecture diagram (ID: {event.diagram_id}) has been analyzed successfully. "
                f"Elements detected: {elements_str}."
            )
        return (
            f"Analysis of your architecture diagram (ID: {event.diagram_id}) failed. "
            f"Error: {event.error_message}"
        )
