resource "aws_sns_topic" "app_errors_topic" {
  name = "${var.app_name}-Errors-${var.environment}-${var.aws_region}"
}

# partially supported by terraform -> must be confirmed by email in the given time
resource "aws_sns_topic_subscription" "developer_email_subscription" {
  protocol  = "email"
  endpoint  = var.developer_email_address
  topic_arn = aws_sns_topic.app_errors_topic.arn
  confirmation_timeout_in_minutes = 60
}