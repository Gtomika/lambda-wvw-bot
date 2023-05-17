output "error_topic_arn" {
  value = aws_sns_topic.app_errors_topic.arn
}