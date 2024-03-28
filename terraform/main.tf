terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket = "mood-tracker-bucket"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

module "mood_tracker_repository" {
  source = "terraform-aws-modules/ecr/aws"

  repository_type = "public"
  repository_name                 = "mood-tracker"
  repository_image_tag_mutability = "MUTABLE"

  repository_read_write_access_arns = [
    data.aws_caller_identity.current.arn,
  ]

  public_repository_catalog_data = {
    description       = "Telegram-based mood tracking bot"
    about_text        = file("${path.module}/files/ABOUT.md")
    usage_text        = file("${path.module}/files/USAGE.md")
    operating_systems = ["Linux"]
    architectures     = ["x86"]
    logo_image_blob   = filebase64("${path.module}/files/mood_tracker_logo.jpg")
  }

  repository_lifecycle_policy = local.repository_lifecycle_policy
}

locals {
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep 3 images",
        selection = {
          tagStatus   = "any",
          countType   = "imageCountMoreThan",
          countNumber = 2
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

