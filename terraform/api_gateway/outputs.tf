output "discord_interaction_webhook_url" {
  value = "${aws_apigatewayv2_stage.api_gateway_stage.invoke_url}${var.discord_interaction_path}"
}