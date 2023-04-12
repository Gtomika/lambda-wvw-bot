output "schedule_group_arn" {
  value = aws_scheduler_schedule_group.schedule_group.arn
}

output "scheduler_role_arn" {
  value = aws_iam_role.scheduler_role.arn
}