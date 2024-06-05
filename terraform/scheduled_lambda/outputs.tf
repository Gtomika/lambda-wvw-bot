output "scheduled_lambda_arn" {
  value = aws_lambda_function.scheduled_lambda.arn
}

output "scheduled_lambda_invoke_arn" {
  value = aws_lambda_function.scheduled_lambda.invoke_arn
}

output "scheduled_lambda_name" {
  value = aws_lambda_function.scheduled_lambda.function_name
}