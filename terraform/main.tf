terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket = "telegram-mood-tracker-state"
    key    = "mood-tracker/terraform.tfstate"
    region = "eu-central-1"
  }
}

data "aws_caller_identity" "current" {}

module "mood_tracker_repository" {
  source = "terraform-aws-modules/ecr/aws"

  repository_name                 = "mood-tracker"
  repository_image_tag_mutability = "MUTABLE"

  repository_read_write_access_arns = [
    data.aws_caller_identity.current.arn,
  ]

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

