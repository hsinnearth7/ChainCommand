terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "chaincommand-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "chaincommand-terraform-locks"
    encrypt        = true
  }
}

module "chaincommand" {
  source = "../../"

  aws_region  = "us-east-1"
  environment = "prod"

  vpc_cidr = "10.1.0.0/16"

  # EKS — production sizing
  eks_cluster_version    = "1.31"
  eks_node_instance_type = "t3.xlarge"
  eks_node_min_size      = 3
  eks_node_max_size      = 20
  eks_node_desired_size  = 3

  # RDS — production sizing with Multi-AZ
  rds_instance_class    = "db.r6g.large"
  rds_allocated_storage = 100
  rds_db_name           = "chaincommand"
  rds_db_username       = "chaincommand"

  # Redis — production sizing with failover
  redis_node_type = "cache.r6g.large"
}

output "eks_cluster_endpoint" {
  value = module.chaincommand.eks_cluster_endpoint
}

output "rds_endpoint" {
  value = module.chaincommand.rds_endpoint
}

output "redis_endpoint" {
  value = module.chaincommand.redis_endpoint
}

output "s3_bucket_name" {
  value = module.chaincommand.s3_bucket_name
}
