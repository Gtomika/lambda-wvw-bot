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
  },
  {
    command_name = "ApiKeyAdd"
    command_name_discord = "api_key_add"
    handler = "bot/api_key_add_command/lambda_function.lambda_handler"
    path_to_deployment_package = "../api-key-add-lambda-package/api_key_add_lambda.zip"
  }
]

discord_interaction_path = "api/discord/interaction"
discord_developer_id = 416289572289249280

documentation_url = "https://gtomika.github.io/mod-wvw-bot/" # TODO update this
gw2_required_permissions = "account, inventories, characters, wallet, unlocks, progression" # for the GW2 API

log_retention_days = 30