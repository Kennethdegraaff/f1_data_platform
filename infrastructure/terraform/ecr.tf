resource "aws_ecr_repository" "f1_data_platform" {
  name                 = "f1-data-platform"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}