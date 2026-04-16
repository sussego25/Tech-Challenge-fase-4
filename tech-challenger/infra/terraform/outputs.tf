output "architecture_analysis_queue_url" {
  description = "URL of the architecture analysis SQS queue"
  value       = module.sqs.architecture_analysis_queue_url
}

output "architecture_analysis_queue_arn" {
  description = "ARN of the architecture analysis SQS queue"
  value       = module.sqs.architecture_analysis_queue_arn
}

output "architecture_analysis_dlq_url" {
  description = "URL of the architecture analysis DLQ"
  value       = module.sqs.architecture_analysis_dlq_url
}

output "architecture_analysis_dlq_arn" {
  description = "ARN of the architecture analysis DLQ"
  value       = module.sqs.architecture_analysis_dlq_arn
}

output "lambda_documents_role_arn" {
  description = "ARN da role da Lambda de documentos"
  value       = module.lambda_iam.lambda_documents_role_arn
}

output "worker_service_role_arn" {
  description = "ARN da role IRSA do worker no EKS (null quando enable_worker_iam=false)"
  value       = try(module.worker_iam[0].worker_service_role_arn, null)
}

output "diagrams_table_name" {
  description = "Nome da tabela DynamoDB de diagramas"
  value       = module.dynamodb.diagrams_table_name
}

output "diagrams_table_arn" {
  description = "ARN da tabela DynamoDB de diagramas"
  value       = module.dynamodb.diagrams_table_arn
}

output "notifications_table_name" {
  description = "Nome da tabela DynamoDB de notificacoes"
  value       = module.dynamodb.notifications_table_name
}

output "notifications_table_arn" {
  description = "ARN da tabela DynamoDB de notificacoes"
  value       = module.dynamodb.notifications_table_arn
}

output "diagrams_bucket_name" {
  description = "Nome do bucket S3 de diagramas"
  value       = module.s3.diagrams_bucket_name
}

output "diagrams_bucket_arn" {
  description = "ARN do bucket S3 de diagramas"
  value       = module.s3.diagrams_bucket_arn
}
