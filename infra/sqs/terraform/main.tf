terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# SQS Queue - Análise de Arquitetura
resource "aws_sqs_queue" "architecture_analysis_queue" {
  name                       = "${var.project_name}-architecture-analysis-queue-${var.environment}"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600  # 14 dias
  visibility_timeout_seconds = 300     # 5 minutos

  tags = var.common_tags
}

# Dead Letter Queue para análise de arquitetura
resource "aws_sqs_queue" "architecture_analysis_dlq" {
  name = "${var.project_name}-architecture-analysis-dlq-${var.environment}"

  tags = var.common_tags
}

# Redrive Policy para enviar mensagens com falha para DLQ
resource "aws_sqs_queue_redrive_policy" "architecture_analysis" {
  queue_url = aws_sqs_queue.architecture_analysis_queue.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.architecture_analysis_dlq.arn
    maxReceiveCount     = 3
  })
}

# SQS Queue - Notificações
resource "aws_sqs_queue" "notification_queue" {
  name                       = "${var.project_name}-notification-queue-${var.environment}"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600  # 14 dias
  visibility_timeout_seconds = 300     # 5 minutos

  tags = var.common_tags
}

# Dead Letter Queue para notificações
resource "aws_sqs_queue" "notification_dlq" {
  name = "${var.project_name}-notification-dlq-${var.environment}"

  tags = var.common_tags
}

# Redrive Policy para notificações
resource "aws_sqs_queue_redrive_policy" "notification" {
  queue_url = aws_sqs_queue.notification_queue.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notification_dlq.arn
    maxReceiveCount     = 3
  })
}
