variable "aws_region" {
  description = "AWS Region"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

variable "s3_diagrams_bucket_arn" {
  description = "ARN do bucket S3 de diagramas (permissao de leitura para o SageMaker)"
  type        = string
}

variable "model_container_image" {
  description = "URI da imagem de container do modelo LLM (HuggingFace TGI ou similar)"
  type        = string
  # Exemplo: 763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-tgi-inference:2.1.1-tgi1.4.0-gpu-py310-cu121-ubuntu22.04
}

variable "hf_model_id" {
  description = "HuggingFace model ID a ser carregado no endpoint"
  type        = string
  default     = "mistralai/Mistral-7B-Instruct-v0.2"
}

variable "instance_type" {
  description = "Tipo de instancia SageMaker para o endpoint (ml.m5.large para dev, GPU para prod)"
  type        = string
  default     = "ml.m5.large"
}

variable "instance_count" {
  description = "Numero de instancias no endpoint"
  type        = number
  default     = 1
}
