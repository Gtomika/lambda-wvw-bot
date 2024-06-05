locals {
  api_gateway_name = "API-${var.app_name}-${var.environment}-${var.aws_region}"
}

# Configure access logging for the API gateway
resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  name = "/aws/apigateway/${local.api_gateway_name}"
  retention_in_days = var.log_retention_days
}

# Configure the API gateway
resource "aws_apigatewayv2_api" "api_gateway" {
  name          = local.api_gateway_name
  protocol_type = "HTTP"
  description = "API Gateway for ${var.app_name} application, forwarding request to lambdas"
}

resource "aws_apigatewayv2_integration" "discord_interaction_integration" {
  api_id           = aws_apigatewayv2_api.api_gateway.id
  integration_type = "AWS_PROXY"
  description = "Forward to POST request to the Discord Interaction lambda ${var.discord_interaction_lambda_name}"

  integration_method        = "POST"
  integration_uri           = var.discord_interaction_lambda_invocation_arn
}

resource "aws_apigatewayv2_route" "discord_interaction_route" {
  api_id    = aws_apigatewayv2_api.api_gateway.id
  route_key = "POST /${var.discord_interaction_path}"
  target = "integrations/${aws_apigatewayv2_integration.discord_interaction_integration.id}"
}

resource "aws_apigatewayv2_integration" "parameter_update_integration" {
  api_id           = aws_apigatewayv2_api.api_gateway.id
  integration_type = "AWS_PROXY"
  description = "Forward to POST request to the ${var.scheduled_lambda_name} which will update SSM parameter."

  integration_method = "POST"
  integration_uri    = var.scheduled_lambda_invocation_arn
}

resource "aws_apigatewayv2_route" "parameter_update_route" {
  api_id    = aws_apigatewayv2_api.api_gateway.id
  route_key = "POST /${var.parameter_update_interaction_path}"
  target = "integrations/${aws_apigatewayv2_integration.parameter_update_integration.id}"
}

# API gateway stage
resource "aws_apigatewayv2_stage" "api_gateway_stage" {
  name          = "$default"
  api_id        = aws_apigatewayv2_api.api_gateway.id
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_deployment" "api_gateway_deployment" {
  api_id        = aws_apigatewayv2_api.api_gateway.id
  description = "Deployment for the ${local.api_gateway_name} HTTP API Gateway"

  # To avoid attempting deployment before route + integration are ready
  depends_on = [
    aws_apigatewayv2_integration.discord_interaction_integration,
    aws_apigatewayv2_route.discord_interaction_route,
    aws_apigatewayv2_integration.parameter_update_integration,
    aws_apigatewayv2_route.parameter_update_route,
  ]

  lifecycle { # to avoid downtime
    create_before_destroy = true
  }

  triggers = { # to avoid unnecessary re-deployments
    redeployment = sha1(join(",", tolist([
      jsonencode(aws_apigatewayv2_integration.discord_interaction_integration),
      jsonencode(aws_apigatewayv2_route.discord_interaction_route),
      jsonencode(aws_apigatewayv2_integration.parameter_update_integration),
      jsonencode(aws_apigatewayv2_route.parameter_update_route),
    ])))
  }
}

# Give permissions to API gateway to invoke interaction lambda
resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id = "AllowAPIGatewayToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = var.discord_interaction_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.api_gateway.execution_arn}/*"
}

# Give permissions to API gateway to invoke scheduled lambda
resource "aws_lambda_permission" "api_gateway_lambda_permission_scheduled" {
  statement_id = "AllowAPIGatewayToInvokeLambdaScheduled"
  action        = "lambda:InvokeFunction"
  function_name = var.scheduled_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.api_gateway.execution_arn}/*"
}
