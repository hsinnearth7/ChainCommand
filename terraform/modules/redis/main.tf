variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "node_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "eks_security_group" {
  type = string
}

variable "auth_token" {
  type      = string
  sensitive = true
}

# --- Subnet Group ---

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet"
  subnet_ids = var.subnet_ids
}

# --- Security Group ---

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-${var.environment}-redis-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.eks_security_group]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# --- ElastiCache Redis ---

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "${var.project_name}-${var.environment}"
  description          = "Redis cluster for ${var.project_name} ${var.environment}"

  node_type            = var.node_type
  num_cache_clusters   = var.environment == "prod" ? 2 : 1
  port                 = 6379
  parameter_group_name = "default.redis7"
  engine_version       = "7.1"

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  auth_token                 = var.auth_token
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  automatic_failover_enabled = var.environment == "prod"
  multi_az_enabled           = var.environment == "prod"

  snapshot_retention_limit = var.environment == "prod" ? 7 : 1
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "mon:05:00-mon:06:00"

  apply_immediately = var.environment != "prod"

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}

# --- Outputs ---

output "endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "redis_url" {
  value     = aws_elasticache_replication_group.main.transit_encryption_enabled ? "rediss://:${aws_elasticache_replication_group.main.auth_token}@${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0" : "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
  sensitive = true
}

output "security_group_id" {
  value = aws_security_group.redis.id
}
