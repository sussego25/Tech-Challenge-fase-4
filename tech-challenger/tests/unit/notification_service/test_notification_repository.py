import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from infrastructure.notification_repository import NotificationRepository
from domain.notification import Notification, NotificationStatus


def _make_notification(**kwargs) -> Notification:
    defaults = {
        "diagram_id": uuid4(),
        "user_id": "user-1",
        "message": "Analysis complete.",
    }
    return Notification(**{**defaults, **kwargs})


def _to_item(n: Notification) -> dict:
    return {
        "notification_id": str(n.notification_id),
        "diagram_id": str(n.diagram_id),
        "user_id": n.user_id,
        "message": n.message,
        "status": n.status.value,
        "created_at": n.created_at.isoformat(),
    }


class TestNotificationRepositorySave:
    def test_save_calls_put_item(self):
        mock_table = MagicMock()
        repo = NotificationRepository(table=mock_table)
        repo.save(_make_notification())
        mock_table.put_item.assert_called_once()

    def test_save_includes_notification_id(self):
        mock_table = MagicMock()
        repo = NotificationRepository(table=mock_table)
        n = _make_notification()
        repo.save(n)
        item = mock_table.put_item.call_args.kwargs["Item"]
        assert item["notification_id"] == str(n.notification_id)

    def test_save_includes_all_required_fields(self):
        mock_table = MagicMock()
        repo = NotificationRepository(table=mock_table)
        repo.save(_make_notification())
        item = mock_table.put_item.call_args.kwargs["Item"]
        for field in ("notification_id", "diagram_id", "user_id", "message", "status", "created_at"):
            assert field in item

    def test_save_includes_sent_at_when_present(self):
        mock_table = MagicMock()
        repo = NotificationRepository(table=mock_table)
        n = _make_notification()
        n.mark_sent()
        repo.save(n)
        item = mock_table.put_item.call_args.kwargs["Item"]
        assert "sent_at" in item
