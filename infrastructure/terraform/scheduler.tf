resource "aws_scheduler_schedule" "f1_data_platform" {
  name = "f1-data-platform-daily"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 day)"

  target {
    arn      = aws_lambda_function.f1_data_platform.arn
    role_arn = aws_iam_role.scheduler.arn
  }
}