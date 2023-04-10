output "discord_interaction_lambda_name" {
  value = module.discord_interaction_lambda.discord_interaction_lambda_name
}

output "discord_interaction_lambda_arn" {
  value = module.discord_interaction_lambda.discord_interaction_lambda_arn
}

output "command_handler_lambda_names" {
  value = [for command_handler_module in module.command_lambda_modules: {
    command_name_discord: command_handler_module.command_name_discord
    command_handler_lambda_arn: command_handler_module.command_handler_lambda_arn
    command_lambda_name: command_handler_module.command_handler_lambda_name
  }]
}

output "gw2_users_table_name" {
  value = module.dynamodb_tables.gw2_users_table_name
}

output "gw2_guilds_table_name" {
  value = module.dynamodb_tables.gw2_guilds_table_name
}

output "discord_interaction_webhook_url" {
  value = module.api_gateway.discord_interaction_webhook_url
}

output "assets_s3_bucket_arn" {
  value = module.s3.assets_bucket_arn
}

output "app_icon_url" {
  value = module.s3.app_icon_url
}