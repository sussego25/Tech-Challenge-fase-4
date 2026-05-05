environment = "prod"

# ─────────────────────────────────────────────
# Feature flags — habilitar módulos condicionais
# ─────────────────────────────────────────────
enable_networking = true
enable_eks        = true
enable_kafka      = false
enable_worker_iam = true

# ─────────────────────────────────────────────
# Networking
# ─────────────────────────────────────────────
enable_ha_nat = false # false = 1 NAT Gateway (economia ~$32/mês)

# ─────────────────────────────────────────────
# EKS — mínimo para funcionar (economia)
# ─────────────────────────────────────────────
eks_node_instance_type = "t3.small"
eks_node_desired_size  = 1
eks_node_min_size      = 1
eks_node_max_size      = 2

# ─────────────────────────────────────────────
# Kafka/MSK removido do deploy atual
# ─────────────────────────────────────────────
# kafka_broker_instance_type   = "kafka.t3.small"
# kafka_number_of_broker_nodes = 2
# kafka_broker_volume_size     = 10

# ─────────────────────────────────────────────
# Worker IAM (IRSA)
# ─────────────────────────────────────────────
k8s_namespace            = "prod"
k8s_service_account_name = "worker-service"
