import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from libs.llm.exceptions import LLMInvokeError


class BedrockClient:
    def __init__(
        self,
        model_id: str | None,
        region: str | None = None,
        boto_client: Any = None,
    ) -> None:
        if not model_id:
            raise ValueError("model_id must be a non-empty string")
        self._model_id = model_id
        self._client = boto_client or boto3.client(
            "bedrock",
            region_name=region or os.getenv("AWS_REGION"),
        )

    def invoke(self, prompt: str) -> str:
        body = json.dumps({"input": prompt}).encode()
        try:
            response = self._client.invoke_model(
                modelId=self._model_id,
                contentType="application/json",
                accept="application/json",
                body=body,
            )
        except ClientError as e:
            raise LLMInvokeError(f"Failed to invoke Bedrock model '{self._model_id}': {e}") from e

        raw_body = response["body"]
        raw = raw_body.read() if hasattr(raw_body, "read") else raw_body
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                if "generated_text" in parsed:
                    return parsed["generated_text"]
                if "output" in parsed:
                    return parsed["output"]
            return text
        except json.JSONDecodeError:
            return text
