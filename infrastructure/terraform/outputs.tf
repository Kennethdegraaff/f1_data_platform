output "ecr_repository_url" {
  value = aws_ecr_repository.f1_data_platform.repository_url
}

output "github_actions_role_arn" {
  description = "IAM role ARN used by GitHub Actions"
  value       = aws_iam_role.github_actions.arn
}