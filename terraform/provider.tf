provider "aws" {
  # these credentials do not allow access: for that role must be assumed
  access_key = var.aws_key_id
  secret_key = var.aws_secret_key
  region = var.aws_region

  assume_role {
    role_arn = var.aws_terraform_role_arn
    external_id = var.aws_assume_role_external_id
    duration = "1h"
    session_name = "TerraformSession"
  }

  default_tags {
    tags = {
      application = "LambdaWvvBot"
      managed_by = "Terraform"
      repository = "https://github.com/Gtomika/lambda-wvw-bot"
      owner = "Tamas Gaspar"
    }
  }
}

terraform {
  backend "s3" {} # set dynamically
}