variable "stack_name" {
  description = "Name of stack"
  type        = string
  default     = "clojure-app"
}

variable "cluster_name" {
  description = "Name of EKS cluster"
  type        = string
  default     = "test-cluster"
}

variable "app_ecr_repo_name" {
  description = "Name of ECR repo"
  type        = string
  default     = "clojure-app-repo"
}

