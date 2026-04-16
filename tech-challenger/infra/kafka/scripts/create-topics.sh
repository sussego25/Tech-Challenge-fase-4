#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# create-topics.sh
# Cria os topicos Kafka necessarios no cluster MSK apos o
# provisionamento Terraform.
#
# Pre-requisitos:
#   - kafka-topics.sh disponivel no PATH (Kafka binaries instalados)
#   - Conectividade com o cluster MSK (execute dentro da VPC ou via
#     bastion host / kubectl exec em um pod na mesma VPC)
#
# Uso:
#   BOOTSTRAP_SERVERS="<msk_bootstrap_brokers>" bash create-topics.sh
#   ou
#   export BOOTSTRAP_SERVERS=$(terraform -chdir=../terraform output -raw kafka_bootstrap_brokers)
#   bash create-topics.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

BOOTSTRAP_SERVERS="${BOOTSTRAP_SERVERS:?Variavel BOOTSTRAP_SERVERS nao definida. Ex: broker1:9092,broker2:9092}"

# ─────────────────────────────────────────────
# Funcao auxiliar
# ─────────────────────────────────────────────
create_topic() {
  local topic=$1
  local partitions=$2
  local replication=$3
  local retention_ms=$4

  echo "→ Criando topico: ${topic} (partitions=${partitions}, replication=${replication})"
  kafka-topics.sh \
    --bootstrap-server "${BOOTSTRAP_SERVERS}" \
    --create \
    --if-not-exists \
    --topic "${topic}" \
    --partitions "${partitions}" \
    --replication-factor "${replication}" \
    --config "retention.ms=${retention_ms}"

  echo "  ✓ ${topic} criado (ou ja existia)"
}

# ─────────────────────────────────────────────
# Topicos necessarios para o tech-challenger
# ─────────────────────────────────────────────

# Producao: worker-service publica resultado da analise LLM
# Consumo:  notification-service persiste notificacao no DynamoDB
create_topic "analysis-completed" 3 2 604800000   # 7 dias

# Topico interno: worker-service pode usar para deduplicacao / rastreamento
create_topic "architecture-analysis" 3 2 604800000  # 7 dias

# ─────────────────────────────────────────────
# Lista os topicos criados
# ─────────────────────────────────────────────
echo ""
echo "Topicos existentes no cluster:"
kafka-topics.sh \
  --bootstrap-server "${BOOTSTRAP_SERVERS}" \
  --list
