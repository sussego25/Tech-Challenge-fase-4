import boto3

from domain.notification import Notification


class NotificationRepository:
    def __init__(self, table=None, table_name: str = "", region: str = "us-east-1") -> None:
        if table is not None:
            self._table = table
        else:
            if not table_name:
                raise ValueError("table_name cannot be empty when table is not provided")
            dynamodb = boto3.resource("dynamodb", region_name=region)
            self._table = dynamodb.Table(table_name)

    def save(self, notification: Notification) -> None:
        item: dict = {
            "notification_id": str(notification.notification_id),
            "diagram_id": str(notification.diagram_id),
            "message": notification.message,
            "status": notification.status.value,
            "created_at": notification.created_at.isoformat(),
        }
        if notification.sent_at:
            item["sent_at"] = notification.sent_at.isoformat()

        self._table.put_item(Item=item)
