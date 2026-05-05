# variable "aws_region" {
#   description = "AWS Region"
#   type        = string
# }

# variable "environment" {
#   description = "Environment name (dev, staging, prod)"
#   type        = string
# }

# variable "project_name" {
#   description = "Project name for resource naming"
#   type        = string
# }

# variable "common_tags" {
#   description = "Common tags for all resources"
#   type        = map(string)
#   default     = {}
# }

# variable "vpc_id" {
#   description = "ID da VPC onde o cluster MSK sera criado"
#   type        = string
# }

# variable "subnet_ids" {
#   description = "Lista de IDs de subnets privadas (minimo 2 AZs) para os brokers MSK"
#   type        = list(string)
# }

# variable "kafka_version" {
#   description = "Versao do Apache Kafka para o cluster MSK"
#   type        = string
#   default     = "3.5.1"
# }

# variable "broker_instance_type" {
#   description = "Tipo de instancia para os brokers MSK (kafka.t3.small para dev)"
#   type        = string
#   default     = "kafka.t3.small"
# }

# variable "number_of_broker_nodes" {
#   description = "Numero de broker nodes MSK (deve ser multiplo das AZs)"
#   type        = number
#   default     = 2
# }

# variable "broker_volume_size" {
#   description = "Tamanho do volume EBS de cada broker em GB"
#   type        = number
#   default     = 10
# }

# variable "allowed_cidr_blocks" {
#   description = "Lista de CIDR blocks autorizados a conectar no MSK (subnets do EKS)"
#   type        = list(string)
#   default     = []
# }

# variable "topics" {
#   description = "Mapa de topicos Kafka a serem documentados (criados via script de init)"
#   type = map(object({
#     partitions         = number
#     replication_factor = number
#   }))
#   default = {
#     "architecture-analysis" = {
#       partitions         = 3
#       replication_factor = 2
#     }
#     "analysis-completed" = {
#       partitions         = 3
#       replication_factor = 2
#     }
#   }
# }
