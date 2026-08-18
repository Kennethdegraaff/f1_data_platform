resource "aws_lambda_function" "f1_data_platform" {
  function_name = "f1-data-platform"

  role = aws_iam_role.lambda.arn

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.f1_data_platform.repository_url}:latest"

  timeout     = 900
  memory_size = 3008

  environment {
    variables = {
      F1_DATA_BUCKET = aws_s3_bucket.f1_data.bucket
    }
  }

  tags = {
    Project = "f1-data-platform"
  }
}