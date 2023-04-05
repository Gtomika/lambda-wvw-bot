# Here are declared all the IAM policies for the command lambda functions
# at least logging permissions must be declared

data "aws_iam_policy_document" "help_lambda_policy" {
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

data "aws_iam_policy_document" "api_key_add_lambda_policy" {
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
    sid = "AllowLambdaToAccessUsersTable"
    effect = "Allow"
    actions = [
      "dynamodb:*Item"
    ]
    resources = [module.dynamodb_tables.gw2_users_table_arn]
  }
}

locals {

  # Here are declared the environmental variable configurations for the command lambda functions
  # The APPLICATION_ID and BOT_TOKEN are required by all

  help_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
  }

  api_key_add_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
    GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
  }

  # Build map objects from the command inputs: to be used later
  command_policies = tomap({
    Help = data.aws_iam_policy_document.help_lambda_policy
    ApiKeyAdd = data.aws_iam_policy_document.api_key_add_lambda_policy
  })

  environment_variables = tomap({
    Help = local.help_variables
    ApiKeyAdd = local.api_key_add_variables
  })
}