variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "f1-data-platform"
}

variable "aws_region" {
  description = "AWS region to deploy resources to"
  type        = string
  default     = "eu-central-1"
}

variable "athena_database_name" {
  description = "Name of the Athena database"
  type        = string
  default     = "f1_data"
}