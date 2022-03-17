output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = local.cluster_name
}

output "ecr_repo_url" {
  description = "ECR repo Name"
  value       = aws_ecr_repository.infra_problem_app_ecr_repo.repository_url
}

output "ecr_repo_name" {
  description = "ECR repo Name"
  value       = var.app_ecr_repo_name
}

