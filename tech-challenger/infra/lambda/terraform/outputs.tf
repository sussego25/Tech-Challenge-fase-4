output "lambda_function_name" {
  description = "Nome da funcao Lambda order-handler"
  value       = aws_lambda_function.order_handler.function_name
}

output "lambda_function_arn" {
  description = "ARN da funcao Lambda order-handler"
  value       = aws_lambda_function.order_handler.arn
}

output "lambda_invoke_arn" {
  description = "ARN de invocacao da Lambda (usado pelo API Gateway)"
  value       = aws_lambda_function.order_handler.invoke_arn
}
