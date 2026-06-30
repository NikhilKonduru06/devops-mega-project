terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: store state remotely in S3 once you have a bucket created.
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "devops-todo-app/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}
