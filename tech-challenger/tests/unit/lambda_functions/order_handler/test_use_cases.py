import pytest
from unittest.mock import MagicMock, ANY

from use_cases import ProcessDiagramUploadUseCase
from contracts.entities.architecture_diagram import ArchitectureDiagram


IMAGE_DATA = b"fake-image-bytes"
CONTENT_TYPE = "image/png"
USER_ID = "user-456"


@pytest.fixture
def mock_s3():
    return MagicMock()


@pytest.fixture
def mock_sqs():
    return MagicMock()


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def use_case(mock_s3, mock_sqs, mock_repo):
    return ProcessDiagramUploadUseCase(
        s3_client=mock_s3,
        sqs_client=mock_sqs,
        repository=mock_repo,
        s3_bucket="test-bucket",
    )


class TestProcessDiagramUploadUseCaseOutput:
    def test_returns_architecture_diagram(self, use_case):
        result = use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        assert isinstance(result, ArchitectureDiagram)

    def test_returned_diagram_has_correct_user_id(self, use_case):
        result = use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        assert result.user_id == USER_ID

    def test_returned_diagram_s3_key_contains_diagram_id(self, use_case):
        result = use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        assert str(result.diagram_id) in result.s3_key

    def test_returned_diagram_s3_bucket_matches_config(self, use_case):
        result = use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        assert result.s3_bucket == "test-bucket"


class TestProcessDiagramUploadUseCaseSideEffects:
    def test_uploads_image_to_s3(self, use_case, mock_s3):
        use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        mock_s3.upload_file.assert_called_once_with(IMAGE_DATA, ANY, content_type=CONTENT_TYPE)

    def test_publishes_event_to_sqs(self, use_case, mock_sqs):
        use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        mock_sqs.send_message.assert_called_once()

    def test_saves_diagram_to_repository(self, use_case, mock_repo):
        use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        mock_repo.save.assert_called_once()

    def test_repository_save_receives_architecture_diagram(self, use_case, mock_repo):
        use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        saved = mock_repo.save.call_args[0][0]
        assert isinstance(saved, ArchitectureDiagram)

    def test_s3_key_includes_user_id(self, use_case, mock_s3):
        use_case.execute(IMAGE_DATA, CONTENT_TYPE, USER_ID)
        _, s3_key = mock_s3.upload_file.call_args[0][:2]
        assert USER_ID in s3_key
