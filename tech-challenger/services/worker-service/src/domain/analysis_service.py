import json
import re

from libs.llm import LLMClient

_ELEMENT_KEYWORDS = [
    "api gateway",
    "api_gateway",
    "api",
    "lambda",
    "sqs",
    "dynamodb",
    "s3",
    "kafka",
    "eks",
    "database",
    "storage",
    "queue",
    "container",
    "service",
]


class AnalysisService:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def analyze(
        self,
        image_data: bytes,
        diagram_id: str,
        yolo_components: list[str] | None = None,
    ) -> tuple[str, list[str]]:
        prompt = self._build_prompt(diagram_id, len(image_data), yolo_components)
        report = self._llm.invoke(prompt)
        elements = self._extract_elements(report)
        return report, elements

    def _build_prompt(
        self,
        diagram_id: str,
        image_size: int,
        yolo_components: list[str] | None = None,
    ) -> str:
        yolo_components = yolo_components or []
        yolo_components_text = json.dumps(yolo_components, ensure_ascii=False)

        return (
            "Seu nome é ArchitectGen, um especialista em arquitetura de software e análise de diagramas. "
            "Você tem amplo conhecimento em AWS, Kafka, SQS, EKS, ECS, Lambdas, DynamoDB, S3, API Gateway, SNS, SES, RDS, EC2 e padrões de integração. "
            "Responda apenas em Português. "
            "Você é orientado a entregar apenas um JSON válido, sem explicações extras ou texto adicional fora do JSON. "
            "Gere sua resposta usando a seguinte estrutura JSON exata: "
            "{\n"
            "  \"summary\": \"\",\n"
            "  \"components_detected\": [],\n"
            "  \"risks\": [],\n"
            "  \"recommendations\": [],\n"
            "  \"infra_layers\": [],\n"
            "  \"service_boundary\": \"\"\n"
            "}\n"
            f"Inclua os componentes presentes no campo COMPONENTES_YOLO: {yolo_components_text} no array components_detected e também qualquer componente adicional inferido pelo diagrama. "
            f"Analise o diagrama de arquitetura com ID {diagram_id}. "
            "Considere o arquivo de imagem apenas como contexto técnico. "
            f"O arquivo imagem tem {image_size} bytes. "
        )

    def _extract_elements(self, report: str) -> list[str]:
        normalized = re.sub(r"[^a-z0-9\s]", " ", report.lower())
        found = []
        for keyword in _ELEMENT_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, normalized) and keyword not in found:
                found.append(keyword)
        return found
