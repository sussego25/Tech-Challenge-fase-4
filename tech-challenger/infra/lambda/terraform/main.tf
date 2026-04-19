locals {
  function_name    = "${var.project_name}-order-handler-${var.environment}"
  handler_src_path = "${path.module}/../../../services/lambda-functions/order-handler"
}

# -------------------------------------------------------------------
# Empacota o codigo-fonte da Lambda em um zip
# -------------------------------------------------------------------
data "archive_file" "order_handler" {
  type        = "zip"
  source_dir  = local.handler_src_path
  output_path = "${path.module}/lambda_order_handler.zip"

  excludes = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
  ]
}

# -------------------------------------------------------------------
# Lambda Function
# -------------------------------------------------------------------
resource "aws_lambda_function" "order_handler" {
  function_name = local.function_name
  description   = "Order handler para upload e processamento de diagramas de arquitetura"
  role          = var.lambda_role_arn

  filename         = data.archive_file.order_handler.output_path
  source_code_hash = data.archive_file.order_handler.output_base64sha256

  runtime     = "python3.11"
  handler     = "handler.lambda_handler"
  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      S3_BUCKET      = var.s3_bucket_name
      SQS_QUEUE_URL  = var.sqs_queue_url
      DYNAMODB_TABLE = var.dynamodb_table_name
    }
  }

  tags = merge(var.common_tags, {
    Name        = local.function_name
    Environment = var.environment
    Module      = "lambda"
  })
}
