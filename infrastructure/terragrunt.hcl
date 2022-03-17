# Configure Terragrunt to automatically store tfstate files in an S3 bucket

locals {
  region  = "aws_region"
  profile = "aws_profile" # Optional - set default if not using any profile
}

remote_state {
  backend = "s3"
  config = {
    encrypt        = true
    bucket         = "clojure-app-test1-terragrunt-state-bucket"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "${local.region}"
    dynamodb_table = "clojure-app-test1-infra-terraform-lock"
    profile        = "${local.profile}"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    provider "aws" {
      region = "${local.region}"
      profile = "${local.profile}"
    }
    EOF
}
