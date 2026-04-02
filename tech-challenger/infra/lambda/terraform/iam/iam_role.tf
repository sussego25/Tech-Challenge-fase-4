resource "aws_iam_role" "lambda_documents_role" {
  name = "${var.project_name}-lambda-documents-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowLambdaServiceAssumeRole"
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy" "lambda_sqs_send_policy" {
  name = "${var.project_name}-lambda-sqs-send-policy-${var.environment}"
  role = aws_iam_role.lambda_documents_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowSendMessageToArchitectureQueue"
      Effect = "Allow"
      Action = [
        "sqs:SendMessage"
      ]
      Resource = var.sqs_queue_arn
    }]
  })
}

output "lambda_documents_role_arn" {
  description = "ARN da role da Lambda de documentos"
  value       = aws_iam_role.lambda_documents_role.arn
}
