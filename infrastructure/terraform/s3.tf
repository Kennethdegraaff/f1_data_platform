resource "aws_s3_bucket" "f1_data" {
  bucket = "f1-data-platform"

  tags = {
    Project     = "f1-data-platform"
  }
}

resource "aws_s3_bucket_public_access_block" "f1_data" {
  bucket = aws_s3_bucket.f1_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "f1_data" {
  bucket = aws_s3_bucket.f1_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "f1_data" {
  bucket = aws_s3_bucket.f1_data.id

  versioning_configuration {
    status = "Enabled"
  }
}