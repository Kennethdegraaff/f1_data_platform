resource "aws_iam_user" "grafana" {
  name = "${var.project_name}-grafana"

  tags = local.common_tags
}

resource "aws_iam_policy" "grafana" {
  name = "${var.project_name}-grafana"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      # Athena query execution and metadata
      {
        Effect = "Allow"

        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup",
          "athena:ListDataCatalogs",
          "athena:ListDatabases",
          "athena:ListWorkGroups",
          "athena:GetDataCatalog",
          "athena:GetDatabase",
          "athena:GetTableMetadata",
          "athena:ListTableMetadata",
        ]

        Resource = "*"
      },

      # AWS Glue Data Catalog metadata
      {
        Effect = "Allow"

        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartitions",
          "glue:GetPartition",
        ]

        Resource = "*"
      },

      # S3 bucket metadata
      {
        Effect = "Allow"

        Action = [
          "s3:GetBucketLocation",
          "s3:ListBucket",
        ]

        Resource = aws_s3_bucket.f1_data.arn
      },

      # Read collected F1 data
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
        ]

        Resource = "${aws_s3_bucket.f1_data.arn}/data_collected/*"
      },

      # Read and write Athena query results
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
        ]

        Resource = "${aws_s3_bucket.f1_data.arn}/athena-results/*"
      },
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_user_policy_attachment" "grafana" {
  user       = aws_iam_user.grafana.name
  policy_arn = aws_iam_policy.grafana.arn
}