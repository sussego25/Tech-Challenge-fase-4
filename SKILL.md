# SKILL.md - Competências Técnicas do Projeto Tech-Challenge-fase-4

Este documento define as principais skills e competências necessárias para contribuir no projeto Tech-Challenge-fase-4, um sistema de microserviços em nuvem baseado em AWS.

## Visão Geral do Projeto
O projeto implementa uma arquitetura de microserviços para processamento de pedidos, de analise de arquitetura de software, ou seja uma pipeline onde vamos receber um diagrama de desenho e temos que gerar um realtorio de analise de arquitetura, onde vamos avaliar a qualidade do desenho, e sugerir melhorias, utilizando LLM e modelo yolo para identificação dos elementos para análise e geração de relatórios. 

foi desenvolvido utilizando Python, FastAPI, Terraform para IaC, Kubernetes para orquestração, DynamoDB para banco de dados NoSQL, Kafka e SQS para mensageria, e integração com SageMaker para IA/LLM. O projeto segue as melhores práticas de desenvolvimento, testes e DevOps.

O fluxo se incia com uma requisição via API Gateway e grava em um bucket o diagrama de arquitetura, que é processado por uma lambda onde armazena os metadados em uma tabela dyanamo (as Keys), e publica um evento em um SQS para o worker-service processar o diagrama, onde o worker-service consome o evento do SQS, baixa o diagrama do bucket, processa utilizando um modelo yolo para identificar os elementos do diagrama, e depois utiliza um modelo LLM para gerar um relatório de análise de arquitetura, e publica o resultado em um tópico Kafka, onde a notification-service consome o evento do Kafka e notifica o usuário via email ou outro canal configurado.

## Skills Essenciais

### 1. Desenvolvimento de Microserviços
- **Linguagens**: Python (principal para todos os serviços: lambda-functions, worker-service e etc).
- **Frameworks**: FastAPI para APIs REST assíncronas, Pydantic para validação de dados.
- **Padrões**: Arquitetura hexagonal (domain, application, infrastructure), contratos compartilhados (shared/contracts/).

### 2. Infraestrutura como Código (IaC)
- **Ferramentas**: Terraform para provisionamento de recursos AWS (EKS, DynamoDB, S3, VPC, etc.).
- **Conceitos**: Módulos Terraform, state management, versionamento de infraestrutura.

### 3. Containers e Orquestração
- **Docker**: Criação de imagens (Dockerfile em serviços), multi-stage builds.
- **Kubernetes**: Deploy via Helm charts (infra/eks/helm-charts/), manifests YAML, ConfigMaps/Secrets.
- **Orquestração**: Gerenciamento de pods, services, ingress no EKS.

### 4. Mensageria e Integração
- **Kafka**: Tópicos, producers/consumers (messaging/kafka/).
- **AWS SQS**: Filas para notificações e processamento assíncrono.
- **Eventos**: Contratos de eventos (shared/contracts/events/) para comunicação entre serviços.

### 5. Banco de Dados e Armazenamento
- **DynamoDB**: Schemas NoSQL (infra/dynamodb/schemas/), queries otimizadas.
- **S3**: Buckets para armazenamento de dados (infra/s3/).

### 6. Integração com IA/LLM
- **SageMaker**: Modelos de machine learning (infra/sagemaker/models/), handlers Lambda (services/lambda-functions/sagemaker-handler/).
- **Prompts**: Configuração de prompts para LLM (infra/llm/prompts/).


### 8. DevOps e CI/CD
- **Pipelines**: GitHub Actions ou similares para builds, testes e deploys.
- **Monitoramento**: Logs, métricas em Kubernetes/AWS.
- **Segurança**: IAM roles, VPC, secrets management.

## Níveis de Proficiência
- **Iniciante**: Conhecimento básico de uma linguagem e AWS.
- **Intermediário**: Experiência com microserviços e IaC.
- **Avançado**: Especialista em Kubernetes, Terraform e otimização de performance.

## Treinamento Recomendado
- AWS Certified Solutions Architect/Developer.
- Kubernetes Certified Administrator.
- Cursos em Terraform e Docker.

Este documento deve ser atualizado conforme o projeto evolui.