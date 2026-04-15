import logging

from domain.notification import Notification

logger = logging.getLogger(__name__)


class NotificationSender:
    def send(self, notification: Notification) -> None:
        logger.info(
            "Notification → user=%s diagram=%s status=%s message=%s",
            notification.user_id,
            notification.diagram_id,
            notification.status.value,
            notification.message,
        )
