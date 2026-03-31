# Decisões de Design

## ADR (Architecture Decision Records)

### 1. Uso de Microsserviços
**Problema**: Necessidade de escalabilidade e independência de serviços
**Decisão**: Arquitetura de microsserviços
**Consequências**: Complexidade aumentada, mas maior flexibilidade

### 2. Duplo Canal de Mensageria (Kafka + SQS)
**Problema**: Diferentes requisitos de processamento
**Decisão**: Usar Kafka para streams e SQS para filas assíncronas
**Consequências**: Maior flexibilidade, mais infraestrutura

### 3. Deploy em Kubernetes
**Problema**: Necessidade de orquestração eficiente
**Decisão**: Usar EKS (Elastic Kubernetes Service)
**Consequências**: DevOps mais complexo, deployment mais robusto

[Adicione mais ADRs conforme necessário]
