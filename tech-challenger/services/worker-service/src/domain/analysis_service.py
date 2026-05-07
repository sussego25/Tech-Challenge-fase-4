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
        yolo_components = yolo_components or []
        prompt = self._build_prompt(diagram_id, len(image_data), yolo_components)
        report = self._llm.invoke(prompt)
        report = self._normalize_report(report, yolo_components)
        elements = self._extract_elements(report)
        for component in yolo_components:
            if component not in elements:
                elements.append(component)
        return report, elements

    def _build_prompt(
        self,
        diagram_id: str,
        image_size: int,
        yolo_components: list[str] | None = None,
    ) -> str:
        yolo_components = yolo_components or []
        yolo_components_text = json.dumps(yolo_components, ensure_ascii=False)

        return f"""Persona (Concise/Logical): Você é um Arquiteto de Software Especialista em Cloud, certificado como AWS Solutions Architect Professional. Sua tarefa é realizar uma análise técnica de uma lista de componentes extraídos de um diagrama de arquitetura para a empresa FIAP Secure Systems.

Contexto do Diagrama: ID {diagram_id}. O arquivo de imagem possui {image_size} bytes e deve ser usado apenas como contexto técnico auxiliar.

Dados de Entrada (Explicit):
> Componentes Identificados: {yolo_components_text}

Instruções de Análise (Logical/Reflective):
> Para cada componente na lista, execute as seguintes etapas baseadas nos princípios do AWS Well-Architected Framework:

Caso de Uso e Justificativa: Explique por que este serviço foi incluído e sua função na arquitetura.

Limitações Técnicas: Identifique gargalos, limites de cota ou cenários onde o serviço pode falhar (Ex: Cold starts em Lambda, IOPS em EBS).

Comparação Competitiva: Compare o serviço com uma alternativa AWS (ex: RDS vs DynamoDB, EC2 vs Fargate), destacando trade-offs de custo e performance.

Análise de Riscos (Segurança e Confiabilidade): Identifique falhas de segurança (ex: falta de WAF) ou pontos únicos de falha (SPOF).

Guardrails e Restrições (Explicit/Adaptive):
Proibição de Alucinação: Não mencione serviços que não foram fornecidos na lista de entrada, a menos que seja para sugerir uma recomendação de segurança obrigatória.
Fidelidade Técnica: Use terminologia técnica precisa da AWS.
Formato de Saída: Responda estritamente em formato JSON para integração com o back-end do sistema. Não inclua Markdown, comentários, texto explicativo ou blocos de código fora do JSON.

Esquema JSON Esperado (Explicit):
{{
  "analise_componentes": {yolo_components_text},
  "riscos_identificados": [],
  "recomendacoes_melhoria": []
}}

Reflexão Final (Reflective): Antes de finalizar o JSON, revise se as recomendações atendem ao pilar de Otimização de Custos e Sustentabilidade."""

    def _extract_elements(self, report: str) -> list[str]:
        normalized = re.sub(r"[^a-z0-9\s]", " ", report.lower())
        found = []
        for keyword in _ELEMENT_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, normalized) and keyword not in found:
                found.append(keyword)
        return found

    def _normalize_report(self, report: str, yolo_components: list[str]) -> str:
        report_json = self._extract_json_report(report)
        try:
            parsed = json.loads(report_json)
        except json.JSONDecodeError:
            return report

        if not isinstance(parsed, dict):
            return report

        parsed["analise_componentes"] = yolo_components
        parsed.setdefault("riscos_identificados", [])
        parsed.setdefault("recomendacoes_melhoria", [])
        return json.dumps(parsed, ensure_ascii=False)

    def _extract_json_report(self, report: str) -> str:
        cleaned = report.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return cleaned[start : end + 1]

        return cleaned
