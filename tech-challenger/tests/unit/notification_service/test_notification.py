import pytest
from datetime import datetime, timezone
from uuid import uuid4

from domain.notification import Notification, NotificationStatus


@pytest.fixture
def notification():
    return Notification(
        diagram_id=uuid4(),
        user_id="user-notif-1",
        message="Your analysis is complete.",
    )


class TestNotificationCreation:
    def test_default_status_is_pending(self, notification):
        assert notification.status == NotificationStatus.PENDING

    def test_notification_id_auto_generated(self, notification):
        assert notification.notification_id is not None

    def test_notification_ids_are_unique(self):
        n1 = Notification(diagram_id=uuid4(), user_id="u", message="m")
        n2 = Notification(diagram_id=uuid4(), user_id="u", message="m")
        assert n1.notification_id != n2.notification_id

    def test_sent_at_is_none_on_creation(self, notification):
        assert notification.sent_at is None


class TestNotificationStatusTransitions:
    def test_mark_sent_sets_status_to_sent(self, notification):
        notification.mark_sent()
        assert notification.status == NotificationStatus.SENT

    def test_mark_sent_sets_sent_at_timestamp(self, notification):
        notification.mark_sent()
        assert notification.sent_at is not None

    def test_mark_sent_at_is_utc_datetime(self, notification):
        notification.mark_sent()
        assert notification.sent_at.tzinfo is not None

    def test_mark_failed_sets_status_to_failed(self, notification):
        notification.mark_failed()
        assert notification.status == NotificationStatus.FAILED
