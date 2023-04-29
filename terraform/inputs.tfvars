app_name = "LambdaWvwBot"

libraries_layer_deployment_path = "../libraries-layer-deployment-package/libraries_layer.zip"
commons_layer_deployment_path = "../commons-layer-deployment-package/commons_layer.zip"
image_layer_deployment_path = "../image-layer-deployment-package/image_layer.zip"

discord_interaction_lambda_data = {
  handler = "bot/discord_interaction_lambda_function/lambda_function.lambda_handler"
  path_to_deployment_package = "../discord-interaction-lambda-package/discord_interaction_lambda.zip"
}

scheduled_lambda_data = {
  handler = "bot/scheduled_lambda_function/lambda_function.lambda_handler"
  path_to_deployment_package = "../scheduled-lambda-package/scheduled_lambda.zip"
}

command_data = [
  {
    command_name = "Help"
    command_name_discord = "help"
    handler = "bot/help_command/lambda_function.lambda_handler"
    package_zip_name = "help_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "ApiKey"
    command_name_discord = "api_key"
    handler = "bot/api_key_command/lambda_function.lambda_handler"
    package_zip_name = "api_key_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "HomeWorld"
    command_name_discord = "home_world"
    handler = "bot/home_world_command/lambda_function.lambda_handler"
    package_zip_name = "home_world_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "ManagerRole"
    command_name_discord = "manager_role"
    handler = "bot/manager_role_command/lambda_function.lambda_handler"
    package_zip_name = "manager_role_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwRole"
    command_name_discord = "wvw_role"
    handler = "bot/wvw_role_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_role_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwRank"
    command_name_discord = "wvw_rank"
    handler = "bot/wvw_rank_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_rank_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "WvwMatchup"
    command_name_discord = "wvw_matchup"
    handler = "bot/wvw_matchup_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_matchup_lambda.zip"
    timeout_seconds = 30
  },
  {
    command_name = "NextWvwMatchup"
    command_name_discord = "next_wvw_matchup"
    handler = "bot/next_wvw_matchup_command/lambda_function.lambda_handler"
    package_zip_name = "next_wvw_matchup_lambda.zip"
    timeout_seconds = 30
  },
  {
    command_name = "AnnouncementChannel"
    command_name_discord = "announcement_channel"
    handler = "bot/announcement_channel_command/lambda_function.lambda_handler"
    package_zip_name = "announcement_channel_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwRaid"
    command_name_discord = "wvw_raid"
    handler = "bot/wvw_raid_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_raid_lambda.zip"
    timeout_seconds = 3
  },
  {
    command_name = "WvwDaily"
    command_name_discord = "wvw_daily"
    handler = "bot/wvw_daily_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_daily_lambda.zip"
    timeout_seconds = 8
  },
  {
    command_name = "WvwWeekly"
    command_name_discord = "wvw_weekly"
    handler = "bot/wvw_weekly_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_weekly_lambda.zip"
    timeout_seconds = 8
  },
  {
    command_name = "WvwCurrencies"
    command_name_discord = "wvw_currencies"
    handler = "bot/wvw_currencies_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_currencies_lambda.zip"
    timeout_seconds = 8
  },
  {
    command_name = "WvwItems"
    command_name_discord = "wvw_items"
    handler = "bot/wvw_items_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_items_lambda.zip"
    timeout_seconds = 180 # checking every character can take a long time
  },
  {
    command_name = "WvwLegendaries"
    command_name_discord = "wvw_legendaries"
    handler = "bot/wvw_legendaries_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_legendaries_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "GuildLanguage"
    command_name_discord = "guild_language"
    handler = "bot/guild_language_command/lambda_function.lambda_handler"
    package_zip_name = "guild_language_lambda.zip"
    timeout_seconds = 10
  },
  {
    command_name = "WvwMap"
    command_name_discord = "wvw_map"
    handler = "bot/wvw_map_command/lambda_function.lambda_handler"
    package_zip_name = "wvw_lambda_lambda.zip"
    timeout_seconds = 30
  }
]

discord_interaction_path = "api/discord/interaction"
log_retention_days = 30