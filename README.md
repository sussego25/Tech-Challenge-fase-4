# Tech-Challenge-fase-4

![alt text](image.png)

## Visão Geral

O projeto é um **analisador de diagramas de arquitetura** baseado em microsserviços. O usuário envia uma imagem de diagrama via API, e o sistema analisa automaticamente os componentes usando um modelo de linguagem (LLM via SageMaker), retornando os resultados ao usuário.


---

## Fluxo Completo de Dados
```
[Usuário]
    │  POST /upload (imagem + x-user-id header)
    ▼
[order-handler] ← Lambda AWS (API Gateway trigger)
    │  1. Valida content-type e user-id
    │  2. Faz upload da imagem → S3 (key: diagrams/{user_id}/{diagram_id})
    │  3. Salva ArchitectureDiagram no DynamoDB (status=PENDING)
    │  4. Publica ArchitectureAnalysisRequestedEvent → SQS
    │  5. Retorna 202 com diagram_id
    ▼
[SQS Queue]
    ▼
[worker-service] ← Serviço long-running (container/EKS)
    │  1. Consome evento do SQS
    │  2. Atualiza DynamoDB: PENDING → PROCESSING
    │  3. Baixa imagem do S3
    │  4. Invoca LLM via SageMaker → recebe relatório + elementos
    │  5. Atualiza DynamoDB: PROCESSING → COMPLETED (ou FAILED)
    │  6. Publica ArchitectureAnalysisCompletedEvent → Kafka
    │  7. Deleta mensagem do SQS
    ▼
[Kafka Topic: analysis-completed]
    ▼
[notification-service] ← Serviço long-running (container/EKS)
    │  1. Consome evento do Kafka
    │  2. Formata mensagem de notificação
    │  3. Envia notificação (via NotificationSender — logging atualmente)
    │  4. Salva Notification no DynamoDB (status=sent ou failed)
```

---

## Interações entre Recursos AWS

```
API Gateway → order-handler (Lambda)
                 │
                 ├── S3          (armazena imagens dos diagramas)
                 ├── DynamoDB    (cria registro PENDING)
                 └── SQS         (enfileira evento de análise)

SQS → worker-service (EKS container)
          │
          ├── S3          (baixa imagem)
          ├── SageMaker   (analisa via LLM)
          ├── DynamoDB    (atualiza status)
          ├── Kafka        (publica resultado)
          └── SQS          (deleta mensagem processada)

Kafka → notification-service (EKS container)
            │
            └── DynamoDB    (salva registro de notificação)
```

---

## Módulos Implementados

### `shared/contracts` — Contratos compartilhados

| Arquivo | Descrição |
|---|---|
| `entities/architecture_diagram.py` | Entidade `ArchitectureDiagram` com máquina de estados (`PENDING → PROCESSING → COMPLETED/FAILED`) |
| `events/analysis_requested.py` | Evento `ArchitectureAnalysisRequestedEvent` — publicado pelo order-handler no SQS |
| `events/analysis_completed.py` | Evento `ArchitectureAnalysisCompletedEvent` — publicado pelo worker no Kafka |
| `dto/diagram_upload.py` | DTO `DiagramUploadRequest` — valida content-types aceitos (png, jpeg, jpg, webp) |
| `dto/analysis_status.py` | DTO `AnalysisStatusResponse` — resposta de consulta de status |

### `shared/libs` — Clientes reutilizáveis

| Arquivo | Descrição |
|---|---|
| `aws/s3_client.py` | `S3Client` — upload e download de arquivos no S3 via boto3 |
| `aws/sqs_client.py` | `SQSClient` — send, receive (long polling 20s) e delete de mensagens SQS |
| `llm/sagemaker_client.py` | `LLMClient` — invoca endpoint SageMaker com prompt, retorna `generated_text` |
| `messaging/kafka_producer.py` | `KafkaProducer` — publica mensagens Kafka via `confluent_kafka` |
| `messaging/kafka_consumer.py` | `KafkaConsumer` — consome Kafka em loop infinito com handler callback |

### `services/lambda-functions/order-handler` — Ponto de entrada

Arquitetura: **Lambda AWS acionado pelo API Gateway**

| Arquivo | Descrição |
|---|---|
| `handler.py` | Entry point Lambda. Valida headers (`x-user-id`, `content-type`), decodifica body (suporta base64), retorna 202 |
| `use_cases.py` | `ProcessDiagramUploadUseCase` — orquestra upload S3 + publicação SQS + salvamento DynamoDB |
| `repositories.py` | `DynamoDBDiagramRepository` — persiste e recupera `ArchitectureDiagram` do DynamoDB |
| `config.py` | Lê `S3_BUCKET`, `SQS_QUEUE_URL`, `DYNAMODB_TABLE`, `AWS_REGION` de variáveis de ambiente |

### `services/worker-service` — Processador assíncrono

Arquitetura: **Hexagonal**, serviço long-running em container

| Arquivo | Descrição |
|---|---|
| `consumers/sqs_consumer.py` | `SQSConsumer` — loop infinito, busca batches de 10 msgs, deleta após sucesso |
| `processors/diagram_processor.py` | `DiagramProcessor` — orquestra: get repo → mark_processing → download S3 → LLM → mark_completed/failed → save → publicar Kafka |
| `domain/analysis_service.py` | `AnalysisService` — constrói prompt, invoca `LLMClient`, extrai elementos detectados via keywords |
| `infrastructure/diagram_repository.py` | DynamoDB para `ArchitectureDiagram` |
| `infrastructure/kafka_publisher.py` | `KafkaPublisher` — publica `ArchitectureAnalysisCompletedEvent` no tópico Kafka |
| `jobs/worker.py` | `main()` — instancia dependências e inicia o `SQSConsumer` |

### `services/notification-service` — Notificador

Arquitetura: **Hexagonal**, serviço long-running em container

| Arquivo | Descrição |
|---|---|
| `messaging/kafka_consumer.py` | `KafkaAnalysisConsumer` — consome tópico `analysis-completed`, valida payload, delega ao use case |
| `application/notify_use_case.py` | `NotifyAnalysisCompletedUseCase` — formata mensagem para `completed` vs `failed`, chama sender, salva no DynamoDB |
| `domain/notification.py` | Entidade `Notification` com estados `PENDING → SENT/FAILED` |
| `infrastructure/notification_repository.py` | DynamoDB para `Notification` |
| `infrastructure/notification_sender.py` | Sender atual baseado em logging (SES/email a integrar) |
| `main.py` | Entry point do serviço |

---

## Cobertura de Testes

Testes unitários cobrindo:

- `shared/contracts` — entidades, eventos e DTOs
- `shared/libs` — S3, SQS, Kafka e SageMaker clients
- `order-handler` — handler, use cases e repositório
- `worker-service` — SQS consumer, diagram processor, analysis service, Kafka publisher e repositório
- `notification-service` — Kafka consumer, use case, entidade Notification e repositório

### Comandos para rodar os testes

```powershell
# Shared contracts e libs
cd tech-challenger
$env:PYTHONPATH = ".\shared"
python -m pytest tests\unit\shared\ -v

# Order Handler (Lambda)
$env:PYTHONPATH = ".\shared;.\services\lambda-functions\order-handler"
python -m pytest tests\unit\lambda_functions\ -v

# Worker Service
$env:PYTHONPATH = ".\shared;.\services\worker-service\src"
python -m pytest tests\unit\worker_service\ -v

# Notification Service
$env:PYTHONPATH = ".\shared;.\services\notification-service\src"
python -m pytest tests\unit\notification_service\ -v
```

---

## Variáveis de Ambiente

### order-handler (Lambda)

| Variável | Descrição |
|---|---|
| `S3_BUCKET` | Nome do bucket S3 para armazenar imagens |
| `SQS_QUEUE_URL` | URL da fila SQS de análise |
| `DYNAMODB_TABLE` | Nome da tabela DynamoDB de diagramas |
| `AWS_REGION` | Região AWS (padrão: `us-east-1`) |

### worker-service

| Variável | Descrição |
|---|---|
| `S3_BUCKET` | Nome do bucket S3 |
| `SQS_QUEUE_URL` | URL da fila SQS |
| `DYNAMODB_TABLE` | Nome da tabela DynamoDB de diagramas |
| `KAFKA_BOOTSTRAP_SERVERS` | Endereço dos brokers Kafka |
| `KAFKA_TOPIC_ANALYSIS_COMPLETED` | Tópico Kafka de resultados (padrão: `analysis-completed`) |
| `SAGEMAKER_ENDPOINT` | Nome do endpoint SageMaker (LLM) |
| `AWS_REGION` | Região AWS (padrão: `us-east-1`) |

### notification-service

| Variável | Descrição |
|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | Endereço dos brokers Kafka |
| `KAFKA_TOPIC_ANALYSIS_COMPLETED` | Tópico Kafka consumido (padrão: `analysis-completed`) |
| `KAFKA_GROUP_ID` | Consumer group ID (padrão: `notification-service`) |
| `DYNAMODB_TABLE` | Nome da tabela DynamoDB de notificações |
| `AWS_REGION` | Região AWS (padrão: `us-east-1`) |

---

## Pendências

- `lambda-functions/notification-handler/` e `sagemaker-handler/` — não implementados
- `NotificationSender` — atualmente só faz logging; integração com SES/e-mail pendente
- `infra/` (Terraform) — estrutura criada, código de provisionamento pendente
