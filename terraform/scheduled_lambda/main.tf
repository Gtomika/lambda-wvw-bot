data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "scheduled_lambda_assume_role_policy" {
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

data aws_iam_policy_document "scheduled_lambda_policy" {
  statement {
    sid = "AllowLambdaToLog"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    sid = "AllowLambdaToAccessGuildsUsers"
    effect = "Allow"
    actions = [
      "dynamodb:BatchGet*",
      "dynamodb:DescribeStream",
      "dynamodb:DescribeTable",
      "dynamodb:Get*",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWrite*",
      "dynamodb:CreateTable",
      "dynamodb:Delete*",
      "dynamodb:Update*",
      "dynamodb:PutItem"
    ]
    resources = [
      var.gw2_guilds_table_arn,
      var.gw2_users_table_arn
    ]
  }
  statement {
    sid = "AllowLambdaToSendErrorNotification"
    effect = "Allow"
    actions = [
      "sns:Publish"
    ]
    resources = [
      var.dead_letter_error_topic_arn
    ]
  }
  statement {
    sid = "AllowLambdaToManageSSMParameters"
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:PutParameter",
    ]
    resources = [
      # variable 'bot_ssm_parameters_prefix' already includes / at start and end
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.bot_ssm_parameters_prefix}*"
    ]
  }
}

resource "aws_iam_role" "scheduled_lambda_role" {
  name = "ScheduledLambda-${var.app_name}-${var.environment}-${var.aws_region}"
  assume_role_policy = data.aws_iam_policy_document.scheduled_lambda_assume_role_policy.json
  inline_policy {
    name = "AllowScheduledLamdaActions"
    policy = data.aws_iam_policy_document.scheduled_lambda_policy.json
  }
}

locals {
  function_name = "${var.app_name}-Scheduled-${var.environment}-${var.aws_region}"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "scheduled_lambda" {
  function_name = local.function_name
  description = "This Lambda is invoked by AWS Scheduler to perform various tasks in ${var.app_name} (${var.environment})."
  role          = aws_iam_role.scheduled_lambda_role.arn

  # deployment package required to be already present when this runs
  filename = var.path_to_deployment_package
  source_code_hash = filebase64sha256(var.path_to_deployment_package)

  layers = [var.common_layer_arn, var.libraries_layer_arn]
  runtime = "python3.13"
  handler = var.handler_name
  memory_size = var.memory
  timeout = var.timeout_seconds
  environment {
    variables = var.environment_variables
  }

  dead_letter_config {
    target_arn = var.dead_letter_error_topic_arn
  }

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]
}