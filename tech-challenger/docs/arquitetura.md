# Arquitetura do Sistema

## Visão Geral

Este documento descreve a arquitetura de microsserviços do Tech Challenger.

## Componentes Principais

### Serviços

1. **Order Service**: Gerenciamento de pedidos
2. **Payment Service**: Processamento de pagamentos
3. **Notification Service**: Envio de notificações

### Mensageria

- **Kafka**: Para processamento em stream
- **SQS**: Para fila de mensagens da AWS

## Fluxo de Dados

[Adicione diagramas e descrições do fluxo]

## Infraestrutura

- **EKS**: Kubernetes gerenciado
- **RDS**: Banco de dados
- **SNS/SQS**: Serviços de fila

