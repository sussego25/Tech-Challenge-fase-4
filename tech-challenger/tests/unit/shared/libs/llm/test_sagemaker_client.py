import json
import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from libs.llm.sagemaker_client import LLMClient
from libs.llm.exceptions import LLMInvokeError, LLMResponseParseError


@pytest.fixture
def mock_boto_client():
    return MagicMock()


@pytest.fixture
def llm(mock_boto_client):
    return LLMClient(endpoint_name="my-endpoint", boto_client=mock_boto_client)


class TestLLMClientInit:
    def test_raises_when_endpoint_name_empty(self):
        with pytest.raises(ValueError, match="endpoint_name"):
            LLMClient(endpoint_name="")

    def test_raises_when_endpoint_name_none(self):
        with pytest.raises(ValueError, match="endpoint_name"):
            LLMClient(endpoint_name=None)


class TestLLMClientInvoke:
    def test_invoke_returns_generated_text(self, llm, mock_boto_client):
        response_body = json.dumps({"generated_text": "# Architecture Report\n\nLooks great."})
        mock_boto_client.invoke_endpoint.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=response_body.encode()))
        }
        result = llm.invoke("Analyze this diagram with elements: EC2, RDS")
        assert result == "# Architecture Report\n\nLooks great."

    def test_invoke_accepts_plain_text_response(self, llm, mock_boto_client):
        mock_boto_client.invoke_endpoint.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"Plain report text."))
        }
        result = llm.invoke("prompt")
        assert result == "Plain report text."

    def test_invoke_calls_endpoint_with_correct_params(self, llm, mock_boto_client):
        mock_boto_client.invoke_endpoint.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"report"))
        }
        llm.invoke("my prompt")
        mock_boto_client.invoke_endpoint.assert_called_once_with(
            EndpointName="my-endpoint",
            ContentType="application/json",
            Body=json.dumps({"inputs": "my prompt"}).encode(),
        )

    def test_invoke_raises_llm_invoke_error_on_client_error(self, llm, mock_boto_client):
        mock_boto_client.invoke_endpoint.side_effect = ClientError(
            {"Error": {"Code": "ModelError", "Message": "Model failed"}}, "InvokeEndpoint"
        )
        with pytest.raises(LLMInvokeError, match="Failed to invoke"):
            llm.invoke("prompt")

    def test_invoke_raises_llm_response_parse_error_on_bad_response(self, llm, mock_boto_client):
        mock_boto_client.invoke_endpoint.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"{invalid json}"))
        }
        # Should not raise — falls back to plain text
        result = llm.invoke("prompt")
        assert result == "{invalid json}"
