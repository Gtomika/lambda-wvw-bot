output "command_handler_lambda_arn" {
  value = aws_lambda_function.command_lambda.arn
}

output "command_handler_lambda_name" {
  value = aws_lambda_function.command_lambda.function_name
}

output "command_name_discord" {
  value = var.command_name_discord
}