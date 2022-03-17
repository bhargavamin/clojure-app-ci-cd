provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  token                  = data.aws_eks_cluster_auth.cluster.token
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
}

locals {
  cluster_name = "${var.cluster_name}-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}
