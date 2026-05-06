import base64
import json
import os
from typing import Any
import cv2
import numpy as np
from ultralytics import YOLO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class YoloDetector:
    def __init__(
        self,
        endpoint_name: str | None,
        region: str | None = None,
        boto_client: Any = None,
    ) -> None:
        if not endpoint_name:
            raise ValueError("endpoint_name must be a non-empty string")
        self._endpoint_name = endpoint_name
        self._client = boto_client or boto3.client(
            "sagemaker-runtime",
            region_name=region or os.getenv("AWS_REGION"),
            config=Config(
                connect_timeout=5,
                read_timeout=70,
                retries={"max_attempts": 1},
            ),
        )

    def detect_components(self, image_data: bytes) -> list[str]:
        
        try:

            model = YOLO('modelo_arquitetura_fiap3.pt')

            img_data = base64.b64encode(image_data).decode("utf-8")
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            results = model.predict(source=img)

            components: list[str] = []
            if isinstance(results, list):
                for prediction in results:
                    label = self._extract_label(prediction)
                    if label and label not in components:
                        components.append(label)
                return components
        except ClientError as exc:
            raise RuntimeError(
                f"Failed to invoke YOLO SageMaker endpoint '{self._endpoint_name}': {exc}"
            ) from exc

    def _extract_label(self, prediction: Any) -> str:
        if isinstance(prediction, dict):
            return str(prediction.get("label", "")).strip()
        return str(prediction).strip()
