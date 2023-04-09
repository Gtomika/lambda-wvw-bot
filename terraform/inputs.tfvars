app_name = "LambdaWvwBot"

commons_layer_deployment_path = "../common-layer-deployment-package/common_layer.zip"

discord_interaction_lambda_data = {
  handler = "bot/discord_interaction_lambda_function/lambda_function.lambda_handler"
  path_to_deployment_package = "../discord-interaction-lambda-package/discord_interaction_lambda.zip"
}

command_data = [
  {
    command_name = "Help"
    command_name_discord = "help"
    handler = "bot/help_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../help-lambda-package/help_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "ApiKeyAdd"
    command_name_discord = "api_key_add"
    handler = "bot/api_key_add_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../api-key-add-lambda-package/api_key_add_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "HomeWorld"
    command_name_discord = "home_world"
    handler = "bot/home_world_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../home-world-lambda-package/home_world_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "ManagerRole"
    command_name_discord = "manager_role"
    handler = "bot/manager_role_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../manager-role-lambda-package/manager_role_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwRole"
    command_name_discord = "wvw_role"
    handler = "bot/wvw_role_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../wvw-role-lambda-package/wvw_role_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwRank"
    command_name_discord = "wvw_rank"
    handler = "bot/wvw_rank_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../wvw-rank-lambda-package/wvw_rank_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "WvwMatchup"
    command_name_discord = "wvw_matchup"
    handler = "bot/wvw_matchup_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../wvw-matchup-lambda-package/wvw_matchup_lambda.zip"
    timeout_seconds = 30
  },
  {
    command_name = "NextWvwMatchup"
    command_name_discord = "next_wvw_matchup"
    handler = "bot/next_wvw_matchup_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../next-wvw-matchup-lambda-package/next_wvw_matchup_lambda.zip"
    timeout_seconds = 30
  },
  {
    command_name = "AnnouncementChannel"
    command_name_discord = "announcement_channel"
    handler = "bot/announcement_channel_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../announcement-channel-lambda-package/announcement_channel_lambda.zip"
    timeout_seconds = 3
  }
]

discord_interaction_path = "api/discord/interaction"
log_retention_days = 30