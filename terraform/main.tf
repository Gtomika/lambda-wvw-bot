module "dynamodb_tables" {
  source = "./dynamodb"
  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment
}

locals {
  common_layer_package_path = "${path.module}/${var.commons_layer_deployment_path}"
  discord_interaction_lambda_package_path = "${path.module}/${var.discord_interaction_lambda_data.path_to_deployment_package}"
}

# The lambda layer that contains the libraries
resource "aws_lambda_layer_version" "common_lambda_layer" {
  layer_name = "Commons-${var.app_name}-${var.environment}-${var.aws_region}"
  filename = local.common_layer_package_path
  source_code_hash = filebase64sha256(local.common_layer_package_path)
  compatible_runtimes = ["python3.9"]
}

# Build a lambda function for each command
module "command_lambda_modules" {
  count = length(var.command_data)
  source = "./command_handler_lambda"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  command_name = var.command_data[count.index].command_name
  command_name_discord = var.command_data[count.index].command_name_discord
  handler_name = var.command_data[count.index].handler
  path_to_deployment_package = "${path.module}/${var.command_data[count.index].path_to_deployment_package}"
  common_layer_arn = aws_lambda_layer_version.common_lambda_layer.arn

  command_policy = lookup(local.command_policies, var.command_data[count.index].command_name)
  environment_variables = lookup(local.environment_variables, var.command_data[count.index].command_name)
  log_retention_days = var.log_retention_days
}

# This object will be encoded into JSON and put into the Discord Interaction lambda
# contains the data about all commands and the lambda functions related to them
locals {
  command_lambda_functions_data = [
    for command_lambda_module in module.command_lambda_modules: {
      command_name_discord = command_lambda_module.command_name_discord
      command_lambda_arn = command_lambda_module.command_handler_lambda_arn
    }
  ]
}

# Build the lambda function that will distribute calls to command functions ("Discord Interaction" lambda)
module "discord_interaction_lambda" {
  source = "./discord_interaction_lambda"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  handler_name = var.discord_interaction_lambda_data.handler
  path_to_deployment_package = local.discord_interaction_lambda_package_path
  common_layer_arn = aws_lambda_layer_version.common_lambda_layer.arn

  command_handler_lambda_arns = [for command_handler in module.command_lambda_modules: command_handler.command_handler_lambda_arn]
  environment_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
    APPLICATION_PUBLIC_KEY = var.discord_application_public_key
    COMMANDS = jsonencode(local.command_lambda_functions_data)
  }
  log_retention_days = var.log_retention_days
}

module "api_gateway" {
  source = "./api_gateway"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  discord_interaction_lambda_name = module.discord_interaction_lambda.discord_interaction_lambda_name
  discord_interaction_lambda_invocation_arn = module.discord_interaction_lambda.discord_interaction_lambda_invoke_arn
  discord_interaction_path = var.discord_interaction_path
  log_retention_days = var.log_retention_days
}