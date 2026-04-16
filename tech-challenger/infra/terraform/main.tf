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

module "sqs" {
  source = "../sqs/terraform"

  aws_region   = var.aws_region
  environment  = var.environment
  project_name = var.project_name
  common_tags  = var.common_tags
}

module "dynamodb" {
  source = "../dynamodb/terraform"

  aws_region   = var.aws_region
  environment  = var.environment
  project_name = var.project_name
  common_tags  = var.common_tags
}

module "s3" {
  source = "../s3/terraform"

  aws_region                = var.aws_region
  environment               = var.environment
  project_name              = var.project_name
  common_tags               = var.common_tags
  lifecycle_expiration_days = var.s3_lifecycle_expiration_days
}

module "lambda_iam" {
  source = "../lambda/terraform/iam"

  environment                 = var.environment
  project_name                = var.project_name
  sqs_queue_arn               = module.sqs.architecture_analysis_queue_arn
  dynamodb_diagrams_table_arn = module.dynamodb.diagrams_table_arn
  s3_diagrams_bucket_arn      = module.s3.diagrams_bucket_arn
  common_tags                 = var.common_tags
}

module "worker_iam" {
  count  = var.enable_worker_iam ? 1 : 0
  source = "../eks/terraform/iam"

  environment                 = var.environment
  project_name                = var.project_name
  eks_oidc_provider_arn       = var.eks_oidc_provider_arn
  eks_oidc_provider_url       = replace(var.eks_oidc_provider_url, "https://", "")
  k8s_namespace               = var.k8s_namespace
  k8s_service_account_name    = var.k8s_service_account_name
  sqs_queue_arn               = module.sqs.architecture_analysis_queue_arn
  sqs_dlq_arn                 = module.sqs.architecture_analysis_dlq_arn
  dynamodb_diagrams_table_arn = module.dynamodb.diagrams_table_arn
  s3_diagrams_bucket_arn      = module.s3.diagrams_bucket_arn
  common_tags                 = var.common_tags
}
