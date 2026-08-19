resource "aws_athena_workgroup" "f1_data_platform" {
  name = "f1-data-platform"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.f1_data.bucket}/athena-results/"
    }
  }

  tags = local.common_tags
}

resource "aws_athena_database" "f1_data" {
  name   = var.athena_database_name
  bucket = aws_s3_bucket.f1_data.id
}