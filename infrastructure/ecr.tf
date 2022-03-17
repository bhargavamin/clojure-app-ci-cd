resource "aws_ecr_repository" "infra_problem_app_ecr_repo" {
  name                 = var.app_ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
