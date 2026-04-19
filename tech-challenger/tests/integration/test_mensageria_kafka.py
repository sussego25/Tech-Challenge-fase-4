"""
===========================================================================
Testes de Integração — Mensageria Kafka (ArchitectureAnalysisCompletedEvent)
===========================================================================

Cenários Gherkin:
---------------------------------------------------------------------------
Feature: Consistência do ArchitectureAnalysisCompletedEvent no Kafka

  Scenario: Evento COMPLETED contém relatório e elementos obrigatórios
    Given um diagrama processado com sucesso pelo SageMaker
    When o worker-service publica o evento no tópico Kafka "analysis-completed"
    Then o payload JSON contém diagram_id, user_id, status="completed"
      And analysis_report não é nulo
      And elements_detected é uma lista não vazia
      And completed_at é um timestamp ISO 8601 válido

  Scenario: Evento FAILED contém error_message obrigatório
    Given um diagrama cujo processamento falhou
    When o worker-service publica o evento no tópico Kafka
    Then o payload contém status="failed" e error_message não nulo
      And analysis_report é nulo

  Scenario: notification-service consome evento Kafka corretamente
    Given um ArchitectureAnalysisCompletedEvent válido no tópico Kafka
    When o notification-service consome a mensagem
    Then uma notificação é criada com a mensagem correta
      And a notificação é salva no DynamoDB com status SENT

  Scenario: KafkaProducer serializa Pydantic model via model_dump_json
    Given um ArchitectureAnalysisCompletedEvent com todos os campos
    When o KafkaProducer.publish() é chamado
    Then o valor enviado ao broker é JSON válido com todos os campos do evento
---------------------------------------------------------------------------
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from uuid import uuid4

import pytest

_WORKER_SRC = str(
    Path(__file__).resolve().parents[2] / "services" / "worker-service" / "src"
)
if _WORKER_SRC not in sys.path:
    sys.path.insert(0, _WORKER_SRC)

_NOTIFICATION_SRC = str(
    Path(__file__).resolve().parents[2] / "services" / "notification-service" / "src"
)
if _NOTIFICATION_SRC not in sys.path:
    sys.path.insert(0, _NOTIFICATION_SRC)

_SHARED_DIR = str(Path(__file__).resolve().parents[2] / "shared")
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from contracts.events.analysis_completed import (
    ArchitectureAnalysisCompletedEvent,
    AnalysisStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def completed_event(diagram_id):
    return ArchitectureAnalysisCompletedEvent(
        diagram_id=diagram_id,
        user_id="user-abc-123",
        status=AnalysisStatus.COMPLETED,
        analysis_report="Arquitetura com API Gateway, Lambda e DynamoDB detectada.",
        elements_detected=["api_gateway", "lambda", "dynamodb"],
        completed_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def failed_event(diagram_id):
    return ArchitectureAnalysisCompletedEvent(
        diagram_id=diagram_id,
        user_id="user-abc-123",
        status=AnalysisStatus.FAILED,
        error_message="InferenceError: Model endpoint unavailable",
        completed_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Testes — Consistência do evento COMPLETED no Kafka
# ---------------------------------------------------------------------------
class TestKafkaEventoCompleted:
    """
    Given: diagrama processado com sucesso
    When:  KafkaPublisher publica o evento
    Then:  payload JSON válido com report + elements
    """

    def test_evento_completed_possui_campos_obrigatorios(
        self, completed_event, mock_kafka_producer
    ):
        from infrastructure.kafka_publisher import KafkaPublisher
        from libs.messaging.kafka_producer import KafkaProducer

        mock_kp = MagicMock(spec=KafkaProducer)
        publisher = KafkaPublisher(producer=mock_kp, topic="analysis-completed")

        # --- Act ---
        publisher.publish_analysis_completed(completed_event)

        # --- Assert ---
        mock_kp.publish.assert_called_once()
        published_payload = mock_kp.publish.call_args[0][1]

        # Verifica que o payload é um Pydantic model serializável
        payload_json = json.loads(published_payload.model_dump_json())
        assert payload_json["status"] == "completed"
        assert payload_json["analysis_report"] is not None
        assert len(payload_json["elements_detected"]) > 0
        assert payload_json["user_id"] == "user-abc-123"
        # completed_at deve ser ISO 8601 parseable
        datetime.fromisoformat(payload_json["completed_at"])

    def test_kafka_producer_serializa_pydantic_corretamente(
        self, completed_event
    ):
        """KafkaProducer.publish envia model_dump_json ao broker."""
        mock_confluent_producer = MagicMock()

        from libs.messaging.kafka_producer import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            _producer=mock_confluent_producer,
        )

        # --- Act ---
        producer.publish("analysis-completed", completed_event, key=str(completed_event.diagram_id))

        # --- Assert ---
        mock_confluent_producer.produce.assert_called_once()
        call_kwargs = mock_confluent_producer.produce.call_args[1]
        assert call_kwargs["topic"] == "analysis-completed"

        # O valor deve ser JSON válido
        sent_value = call_kwargs["value"]
        parsed = json.loads(sent_value)
        assert parsed["status"] == "completed"
        assert parsed["analysis_report"] is not None

        mock_confluent_producer.flush.assert_called_once()


# ---------------------------------------------------------------------------
# Testes — Consistência do evento FAILED no Kafka
# ---------------------------------------------------------------------------
class TestKafkaEventoFailed:
    """
    Given: processamento falhou
    When:  evento FAILED publicado
    Then:  error_message presente + analysis_report nulo
    """

    def test_evento_failed_contem_error_message(self, failed_event):
        payload = json.loads(failed_event.model_dump_json())
        assert payload["status"] == "failed"
        assert payload["error_message"] is not None
        assert "InferenceError" in payload["error_message"]
        assert payload["analysis_report"] is None

    def test_evento_failed_sem_error_message_invalido(self, diagram_id):
        """Pydantic deve rejeitar FAILED sem error_message."""
        with pytest.raises(ValueError, match="error_message is required"):
            ArchitectureAnalysisCompletedEvent(
                diagram_id=diagram_id,
                user_id="user-abc-123",
                status=AnalysisStatus.FAILED,
                completed_at=datetime.now(timezone.utc),
                # error_message omitido propositalmente
            )


# ---------------------------------------------------------------------------
# Testes — notification-service consome evento Kafka
# ---------------------------------------------------------------------------

def _load_notification_modules():
    """Carrega módulos do notification-service via importlib para evitar
    conflito de namespace com worker-service (ambos têm domain/ e infrastructure/)."""
    import importlib.util

    _ns_src = Path(__file__).resolve().parents[2] / "services" / "notification-service" / "src"

    def _load(name: str, filepath: Path):
        spec = importlib.util.spec_from_file_location(name, filepath)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    # Carrega domain.notification primeiro (dependência)
    ns_domain_notification = _load(
        "ns_domain.notification", _ns_src / "domain" / "notification.py"
    )

    # Monkey-patch para que notify_use_case.py consiga resolver seus imports
    sys.modules["domain.notification"] = ns_domain_notification
    sys.modules["infrastructure.notification_sender"] = _load(
        "ns_infra.notification_sender", _ns_src / "infrastructure" / "notification_sender.py"
    )
    sys.modules["infrastructure.notification_repository"] = _load(
        "ns_infra.notification_repository", _ns_src / "infrastructure" / "notification_repository.py"
    )

    ns_use_case = _load(
        "ns_app.notify_use_case", _ns_src / "application" / "notify_use_case.py"
    )

    # Limpa os monkey-patches para não poluir outros testes
    for k in [
        "domain.notification",
        "infrastructure.notification_sender",
        "infrastructure.notification_repository",
    ]:
        sys.modules.pop(k, None)

    return (
        ns_use_case.NotifyAnalysisCompletedUseCase,
        ns_domain_notification.NotificationStatus,
    )


class TestNotificationServiceConsumoKafka:
    """
    Given: evento COMPLETED válido no Kafka
    When:  notification-service consome
    Then:  notificação criada, salva como SENT
    """

    def test_notificacao_criada_para_evento_completed(self, completed_event):
        NotifyAnalysisCompletedUseCase, NotificationStatus = _load_notification_modules()

        mock_sender = MagicMock()
        mock_repo = MagicMock()

        use_case = NotifyAnalysisCompletedUseCase(
            sender=mock_sender, repository=mock_repo
        )

        # --- Act ---
        use_case.execute(completed_event)

        # --- Assert ---
        mock_sender.send.assert_called_once()
        notification = mock_sender.send.call_args[0][0]
        assert notification.user_id == "user-abc-123"
        assert notification.diagram_id == completed_event.diagram_id
        assert "analyzed successfully" in notification.message or "concluída" in notification.message

        # Salva com status SENT
        mock_repo.save.assert_called_once()
        saved_notification = mock_repo.save.call_args[0][0]
        assert saved_notification.status == NotificationStatus.SENT

    def test_notificacao_failed_quando_sender_falha(self, completed_event):
        NotifyAnalysisCompletedUseCase, NotificationStatus = _load_notification_modules()

        mock_sender = MagicMock()
        mock_sender.send.side_effect = RuntimeError("SMTP connection failed")
        mock_repo = MagicMock()

        use_case = NotifyAnalysisCompletedUseCase(
            sender=mock_sender, repository=mock_repo
        )

        # --- Act ---
        use_case.execute(completed_event)

        # --- Assert ---  salva mesmo com falha
        mock_repo.save.assert_called_once()
        saved_notification = mock_repo.save.call_args[0][0]
        assert saved_notification.status == NotificationStatus.FAILED
