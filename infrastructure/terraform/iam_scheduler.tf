resource "aws_iam_role" "scheduler" {
  name = "f1-data-platform-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project = "f1-data-platform"
  }
}

resource "aws_iam_role_policy" "scheduler_lambda" {
  name = "f1-data-platform-scheduler-lambda"
  role = aws_iam_role.scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = aws_lambda_function.f1_data_platform.arn
      }
    ]
  })
}