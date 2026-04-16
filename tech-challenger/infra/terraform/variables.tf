variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "tech-challenger"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Terraform = "true"
    Project   = "tech-challenger"
  }
}

variable "enable_worker_iam" {
  description = "Habilita criacao da role IRSA do worker no EKS"
  type        = bool
  default     = false
}

variable "eks_oidc_provider_arn" {
  description = "ARN do provider OIDC do EKS (obrigatorio quando enable_worker_iam=true)"
  type        = string
  default     = ""
}

variable "eks_oidc_provider_url" {
  description = "URL do provider OIDC do EKS (obrigatorio quando enable_worker_iam=true)"
  type        = string
  default     = ""
}

variable "k8s_namespace" {
  description = "Namespace Kubernetes do worker"
  type        = string
  default     = "default"
}

variable "k8s_service_account_name" {
  description = "ServiceAccount Kubernetes usada pelo worker"
  type        = string
  default     = "worker-service"
}

variable "s3_lifecycle_expiration_days" {
  description = "Dias para expirar objetos no bucket S3 de diagramas"
  type        = number
  default     = 90
}

variable "lambda_log_retention_days" {
  description = "Dias de retencao dos logs da Lambda no CloudWatch"
  type        = number
  default     = 14
}
