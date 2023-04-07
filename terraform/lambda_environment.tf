# Some common policies for all lambdas to use

data "aws_iam_policy_document" "log_policy" {
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

data aws_iam_policy_document "users_table_policy" {
  statement {
    sid = "AllowLambdaToAccessUsersTable"
    effect = "Allow"
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:*Item"
    ]
    resources = [module.dynamodb_tables.gw2_users_table_arn]
  }
}

data aws_iam_policy_document "guilds_table_policy" {
  statement {
    sid = "AllowLambdaToAccessGuildsTable"
    effect = "Allow"
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:*Item"
    ]
    resources = [module.dynamodb_tables.gw2_guilds_table_arn]
  }
}

# Here are declared all the IAM policies for the command lambda functions
# In case the lambda has no complex policy (one of the policies from above is enough) it is not declared here

data "aws_iam_policy_document" "api_key_add_lambda_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.log_policy,
    data.aws_iam_policy_document.users_table_policy
  ]
}

data "aws_iam_policy_document" "home_world_lambda_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.log_policy,
    data.aws_iam_policy_document.guilds_table_policy
  ]
}

locals {
  common_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
  }

  # Build map objects from the lambda environments: to be used later
  lambda_environments = tomap({

    Help = tomap({
      policy = data.aws_iam_policy_document.log_policy
      variables = local.common_variables
    })

    ApiKeyAdd = tomap({
      policy = data.aws_iam_policy_document.api_key_add_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
    })

    HomeWorld = tomap({
      policy = data.aws_iam_policy_document.home_world_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    })

  })
}