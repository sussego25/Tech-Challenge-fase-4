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

module "lambda_iam" {
  source = "../lambda/terraform/iam"

  environment   = var.environment
  project_name  = var.project_name
  sqs_queue_arn = module.sqs.architecture_analysis_queue_arn
  common_tags   = var.common_tags
}

module "worker_iam" {
  count  = var.enable_worker_iam ? 1 : 0
  source = "../eks/terraform/iam"

  environment              = var.environment
  project_name             = var.project_name
  eks_oidc_provider_arn    = var.eks_oidc_provider_arn
  eks_oidc_provider_url    = replace(var.eks_oidc_provider_url, "https://", "")
  k8s_namespace            = var.k8s_namespace
  k8s_service_account_name = var.k8s_service_account_name
  sqs_queue_arn            = module.sqs.architecture_analysis_queue_arn
  sqs_dlq_arn              = module.sqs.architecture_analysis_dlq_arn
  common_tags              = var.common_tags
}
