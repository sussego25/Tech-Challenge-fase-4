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

    def analyze(self, image_data: bytes, diagram_id: str) -> tuple[str, list[str]]:
        prompt = self._build_prompt(diagram_id, len(image_data))
        report = self._llm.invoke(prompt)
        elements = self._extract_elements(report)
        return report, elements

    def _build_prompt(self, diagram_id: str, image_size: int) -> str:
        return (
            "Você é um assistente de arquitetura de software. "
            f"Analise o diagrama de arquitetura com ID {diagram_id}. "
            "Gere um relatório em português com os principais componentes, riscos, pontos fortes e sugestões de melhoria. "
            "Se você identificar componentes, mencione-os em formato simples como api_gateway, lambda, dynamodb, s3, kafka, eks, service, database, queue ou container. "
            f"O arquivo imagem tem {image_size} bytes. Use essa informação apenas como contexto técnico." 
        )

    def _extract_elements(self, report: str) -> list[str]:
        normalized = re.sub(r"[^a-z0-9\s]", " ", report.lower())
        found = []
        for keyword in _ELEMENT_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, normalized) and keyword not in found:
                found.append(keyword)
        return found
