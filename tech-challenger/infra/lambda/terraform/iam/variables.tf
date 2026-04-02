variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "tech-challenger"
}

variable "sqs_queue_arn" {
  description = "ARN da fila SQS principal de analise de arquitetura"
  type        = string
}

variable "common_tags" {
  description = "Common tags"
  type        = map(string)
  default = {
    Terraform = "true"
    Project   = "tech-challenger"
  }
}
