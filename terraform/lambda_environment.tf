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

data "aws_iam_policy_document" "scheduler_manager_policy" {
  statement {
    sid = "AllowToManageSchedules"
    effect = "Allow"
    actions = [
      "scheduler:*Schedule",
      "scheduler:List*"
    ]
    resources = ["*"]
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

data "aws_iam_policy_document" "pass_role_to_scheduler_policy" {
  statement {
    sid = "AllowToPassRoleToScheduler"
    effect = "Allow"
    actions = [
      "iam:PassRole"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["scheduler.amazonaws.com"]
    }
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

data "aws_iam_policy_document" "wvw_raid_command_policy" {
  source_policy_documents = [
    data.aws_iam_policy_document.log_policy.json,
    data.aws_iam_policy_document.guilds_table_policy.json,
    data.aws_iam_policy_document.scheduler_manager_policy.json,
    data.aws_iam_policy_document.pass_role_to_scheduler_policy.json
  ]
}


locals {
  common_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
  }

  required_layers = [
    aws_lambda_layer_version.libraries_lambda_layer.arn,
    aws_lambda_layer_version.common_lambda_layer.arn
  ]

  # Build map objects from the lambda environments: to be used later
  lambda_environments = {

    Help = {
      policy    = data.aws_iam_policy_document.log_policy
      variables = local.common_variables
      layers = local.required_layers
    }

    ApiKey = {
      policy    = data.aws_iam_policy_document.user_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    HomeWorld = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

    ManagerRole = {
      policy = data.aws_iam_policy_document.guilds_table_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

    WvwRole = {
      policy = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

    WvwRank = {
      policy    = data.aws_iam_policy_document.user_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    WvwMatchup = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

    NextWvwMatchup = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

    AnnouncementChannel = {
      policy    = data.aws_iam_policy_document.guild_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
        APP_NAME = var.discord_application_name
        APP_ICON_URL = module.s3.app_icon_url
      })
      layers = local.required_layers
    }

    WvwRaid = {
      policy    = data.aws_iam_policy_document.wvw_raid_command_policy
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
        SCHEDULE_GROUP_NAME = module.scheduler.schedule_group_name
        SCHEDULE_ROLE_ARN = module.scheduler.scheduler_role_arn
        SCHEDULED_LAMBDA_ARN = module.scheduled_lambda.scheduled_lambda_arn
        APP_NAME = var.app_name
        ENVIRONMENT = var.environment
      })
      layers = local.required_layers
    }

    WvwDaily = {
      policy    = data.aws_iam_policy_document.user_table_manager_lambda_policy
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    WvwWeekly = {
      policy    = data.aws_iam_policy_document.log_policy
      variables = local.common_variables
      layers = local.required_layers
    }

    WvwCurrencies = {
      policy = data.aws_iam_policy_document.user_table_manager_lambda_policy,
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    WvwItems = {
      policy = data.aws_iam_policy_document.user_table_manager_lambda_policy,
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    WvwLegendaries = {
      policy = data.aws_iam_policy_document.user_table_manager_lambda_policy,
      variables = merge(local.common_variables, {
        GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
      })
      layers = local.required_layers
    }

    GuildLanguage = {
      policy = data.aws_iam_policy_document.guild_table_manager_lambda_policy,
      variables = merge(local.common_variables, {
        GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
      })
      layers = local.required_layers
    }

  }
}