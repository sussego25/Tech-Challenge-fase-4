from libs.llm.sagemaker_client import LLMClient


_COMPONENT_KEYWORDS = [
    "service",
    "database",
    "queue",
    "api",
    "gateway",
    "cache",
    "storage",
    "lambda",
    "function",
    "container",
    "broker",
]


class AnalysisService:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def analyze(self, image_data: bytes, diagram_id: str) -> tuple[str, list[str]]:
        prompt = self._build_prompt(image_data, diagram_id)
        report = self._llm.invoke(prompt)
        elements = self._extract_elements(report)
        return report, elements

    def _build_prompt(self, image_data: bytes, diagram_id: str) -> str:
        return (
            f"Analyze the architecture diagram (ID: {diagram_id}, "
            f"image size: {len(image_data)} bytes). "
            "Identify all architectural components such as services, databases, queues, "
            "APIs, gateways, caches, and storage systems. "
            "Describe their relationships and data flows. "
            "Provide a detailed technical analysis report."
        )

    def _extract_elements(self, report: str) -> list[str]:
        report_lower = report.lower()
        found: list[str] = []
        for keyword in _COMPONENT_KEYWORDS:
            if keyword in report_lower and keyword not in found:
                found.append(keyword)
        return found
