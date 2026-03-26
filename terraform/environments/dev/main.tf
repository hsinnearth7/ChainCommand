terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "chaincommand-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "chaincommand-terraform-locks"
    encrypt        = true
  }
}

module "chaincommand" {
  source = "../../"

  aws_region  = "us-east-1"
  environment = "dev"

  vpc_cidr = "10.0.0.0/16"

  # EKS — smaller for dev
  eks_cluster_version    = "1.31"
  eks_node_instance_type = "t3.medium"
  eks_node_min_size      = 1
  eks_node_max_size      = 3
  eks_node_desired_size  = 1

  # RDS — smaller for dev
  rds_instance_class    = "db.t3.micro"
  rds_allocated_storage = 10
  rds_db_name           = "chaincommand"
  rds_db_username       = "chaincommand"

  # Redis — smallest for dev
  redis_node_type = "cache.t3.micro"
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
