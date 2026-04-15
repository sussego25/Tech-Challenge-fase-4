import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from application.notify_use_case import NotifyAnalysisCompletedUseCase
from contracts.events.analysis_completed import ArchitectureAnalysisCompletedEvent, AnalysisStatus
from domain.notification import Notification, NotificationStatus


DIAGRAM_ID = uuid4()
USER_ID = "user-notif-2"


@pytest.fixture
def completed_event():
    return ArchitectureAnalysisCompletedEvent(
        diagram_id=DIAGRAM_ID,
        user_id=USER_ID,
        status=AnalysisStatus.COMPLETED,
        analysis_report="Detailed analysis.",
        elements_detected=["service", "database"],
        completed_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def failed_event():
    return ArchitectureAnalysisCompletedEvent(
        diagram_id=DIAGRAM_ID,
        user_id=USER_ID,
        status=AnalysisStatus.FAILED,
        completed_at=datetime.now(timezone.utc),
        error_message="LLM timed out",
    )


@pytest.fixture
def mock_sender():
    return MagicMock()


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def use_case(mock_sender, mock_repo):
    return NotifyAnalysisCompletedUseCase(sender=mock_sender, repository=mock_repo)


class TestNotifyUseCaseSuccess:
    def test_calls_sender_once(self, use_case, mock_sender, completed_event):
        use_case.execute(completed_event)
        mock_sender.send.assert_called_once()

    def test_saves_notification_to_repository(self, use_case, mock_repo, completed_event):
        use_case.execute(completed_event)
        mock_repo.save.assert_called_once()

    def test_notification_status_is_sent_after_success(self, use_case, mock_repo, completed_event):
        use_case.execute(completed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert saved.status == NotificationStatus.SENT

    def test_notification_message_contains_diagram_id(self, use_case, mock_repo, completed_event):
        use_case.execute(completed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert str(DIAGRAM_ID) in saved.message

    def test_completed_message_mentions_elements(self, use_case, mock_repo, completed_event):
        use_case.execute(completed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert "service" in saved.message or "database" in saved.message

    def test_failed_event_message_contains_error(self, use_case, mock_repo, failed_event):
        use_case.execute(failed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert "LLM timed out" in saved.message


class TestNotifyUseCaseFailure:
    def test_notification_marked_failed_when_sender_raises(
        self, use_case, mock_sender, mock_repo, completed_event
    ):
        mock_sender.send.side_effect = RuntimeError("connection refused")
        use_case.execute(completed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert saved.status == NotificationStatus.FAILED

    def test_repository_save_called_even_when_sender_fails(
        self, use_case, mock_sender, mock_repo, completed_event
    ):
        mock_sender.send.side_effect = RuntimeError("network error")
        use_case.execute(completed_event)
        mock_repo.save.assert_called_once()

    def test_notification_user_id_is_preserved(self, use_case, mock_repo, completed_event):
        use_case.execute(completed_event)
        saved: Notification = mock_repo.save.call_args[0][0]
        assert saved.user_id == USER_ID
