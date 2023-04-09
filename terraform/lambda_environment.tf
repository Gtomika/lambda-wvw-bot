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

data "aws_iam_policy_document" "dynamodb_describe_policy" {
  statement {
    sid = "AllowLambdaToDescribeDynamoDb"
    effect = "Allow"
    actions = [
      "dynamodb:List*",
      "dynamodb:DescribeReservedCapacity*",
      "dynamodb:DescribeLimits",
      "dynamodb:DescribeTimeToLive"
    ]
    resources = ["*"]
  }
}

data aws_iam_policy_document "users_table_policy" {
  statement {
    sid = "AllowLambdaToAccessUsersTable"
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
    resources = [module.dynamodb_tables.gw2_users_table_arn]
  }
}

data aws_iam_policy_document "guilds_table_policy" {
  statement {
    sid = "AllowLambdaToAccessGuildsTable"
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
    resources = [module.dynamodb_tables.gw2_guilds_table_arn]
  }
}

# Here are declared all the IAM policies for the command lambda functions
# In case the lambda has no complex policy (one of the policies from above is enough) it is not declared here

data "aws_iam_policy_document" "user_table_manager_lambda_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.log_policy.json,
    data.aws_iam_policy_document.dynamodb_describe_policy.json,
    data.aws_iam_policy_document.users_table_policy.json
  ]
}

data "aws_iam_policy_document" "guild_table_manager_lambda_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.log_policy.json,
    data.aws_iam_policy_document.dynamodb_describe_policy.json,
    data.aws_iam_policy_document.guilds_table_policy.json
  ]
}

locals {
  common_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
  }

  # Build map objects from the lambda environments: to be used later
  lambda_environments = {

    Help = {
      policy    = data.aws_iam_policy_document.log_policy
      variables = local.common_variables
    }

    ApiKey = {
      policy    = data.aws_iam_policy_document.user_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
    }

    HomeWorld = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    ManagerRole = {
      policy = data.aws_iam_policy_document.guilds_table_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    WvwRole = {
      policy = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    WvwRank = {
      policy    = data.aws_iam_policy_document.user_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
    }

    WvwMatchup = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    NextWvwMatchup = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    AnnouncementChannel = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

    WvwRaid = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
    }

  }
}