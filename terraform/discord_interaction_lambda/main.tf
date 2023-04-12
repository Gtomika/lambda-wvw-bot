data "aws_iam_policy_document" "discord_interaction_assume_role_policy" {
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

data aws_iam_policy_document "discord_interaction_log_policy" {
  statement {
    sid = "AllowLambdaToLog"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

# to be able to invoke the command handler lambdas
data "aws_iam_policy_document" "discord_interaction_invoke_policies" {
  count = length(var.command_handler_lambda_arns)
  statement {
    sid = "AllowInvokeCommandHandler${count.index}"
    effect = "Allow"
    actions = ["lambda:InvokeFunction"]
    resources = [var.command_handler_lambda_arns[count.index]]
  }
}

# merged from all invoke policies
data "aws_iam_policy_document" "discord_interaction_merged_invoke_policy" {
  source_policy_documents = [for invoke_policy in data.aws_iam_policy_document.discord_interaction_invoke_policies: invoke_policy.json]
}

# finally merge all policies to create final version of this lambda's policies
data "aws_iam_policy_document" "discord_interaction_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.discord_interaction_log_policy.json,
    data.aws_iam_policy_document.discord_interaction_merged_invoke_policy.json
  ]
}

resource "aws_iam_role" "discord_interaction_role" {
  name = "DiscordInteraction-${var.app_name}-${var.environment}-${var.aws_region}"
  assume_role_policy = data.aws_iam_policy_document.discord_interaction_assume_role_policy.json
  inline_policy {
    name = "AllowLambdaToLogAndInvoke"
    policy = data.aws_iam_policy_document.discord_interaction_policy.json
  }
}

locals {
  function_name = "${var.app_name}-DiscordInteraction-${var.environment}-${var.aws_region}"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "discord_interaction_lambda" {
  function_name = local.function_name
  description = "This Lambda is getting all interaction calls from Discord, and distributing it for command processing lambdas."
  role          = aws_iam_role.discord_interaction_role.arn

  # deployment package required to be already present when this runs
  filename = var.path_to_deployment_package
  source_code_hash = filebase64sha256(var.path_to_deployment_package)

  layers = [var.common_layer_arn]
  runtime = "python3.9"
  handler = var.handler_name
  environment {
    variables = var.environment_variables
  }

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]
}