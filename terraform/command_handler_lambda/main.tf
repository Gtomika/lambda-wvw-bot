data "aws_iam_policy_document" "command_assume_role_policy" {
  statement {
    sid = "AllowLambdaToAssume"
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "command_execution_role" {
  name = "${var.app_name}-${var.command_name}-${var.environment}-${var.aws_region}"
  assume_role_policy = data.aws_iam_policy_document.command_assume_role_policy.json
  inline_policy {
    name = "${var.command_name}CommandPolicy"
    policy = var.command_policy.json
  }
}

locals {
  lambda_name = "${var.app_name}-${var.command_name}-${var.environment}-${var.aws_region}"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${local.lambda_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "command_lambda" {
  function_name = local.lambda_name
  description = "This lambda processes and responds to the command ${var.command_name}"
  role          = aws_iam_role.command_execution_role.arn

  # deployment package required to be already present when this runs
  filename = var.path_to_deployment_package
  source_code_hash = filebase64sha256(var.path_to_deployment_package)

  layers = var.layer_arns
  runtime = "python3.9"
  handler = var.handler_name
  memory_size = var.memory
  environment {
    variables = var.environment_variables
  }

  timeout = var.timeout_seconds

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]
}




