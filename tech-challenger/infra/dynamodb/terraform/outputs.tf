output "diagrams_table_name" {
  description = "Nome da tabela DynamoDB de diagramas"
  value       = aws_dynamodb_table.diagrams.name
}

output "diagrams_table_arn" {
  description = "ARN da tabela DynamoDB de diagramas"
  value       = aws_dynamodb_table.diagrams.arn
}

output "notifications_table_name" {
  description = "Nome da tabela DynamoDB de notificações"
  value       = aws_dynamodb_table.notifications.name
}

output "notifications_table_arn" {
  description = "ARN da tabela DynamoDB de notificações"
  value       = aws_dynamodb_table.notifications.arn
}
