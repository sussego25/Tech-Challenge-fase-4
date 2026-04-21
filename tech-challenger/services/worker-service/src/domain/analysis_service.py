# TODO: integrar YOLO (deteccao de componentes) + LLM (descricao textual) aqui
# Por enquanto retorna dados mockados para validar o fluxo completo

_MOCK_REPORT = (
    "[MOCK] Architecture diagram analyzed. "
    "Detected components: API Gateway, Lambda, SQS, DynamoDB, S3, Kafka, EKS."
)

_MOCK_ELEMENTS = ["api", "lambda", "queue", "database", "storage", "broker", "container"]


class AnalysisService:
    def analyze(self, image_data: bytes, diagram_id: str) -> tuple[str, list[str]]:
        return _MOCK_REPORT, _MOCK_ELEMENTS
