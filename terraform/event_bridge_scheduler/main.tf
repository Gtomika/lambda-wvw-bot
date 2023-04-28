# https://docs.aws.amazon.com/scheduler/latest/UserGuide/managing-targets-universal.html
# https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html

locals {
  name_suffix = "${var.app_name}-${var.environment}-${var.aws_region}"
}

resource "aws_scheduler_schedule_group" "schedule_group" {
  name = "Schedules-${local.name_suffix}"
}

data "aws_iam_policy_document" "scheduler_policy" {
  statement {
    sid = "AllowToInvokeScheduledLambda"
    effect = "Allow"
    actions = ["lambda:InvokeFunction"]
    resources = [var.scheduled_lambda_arn]
  }
}

data "aws_iam_policy_document" "scheduler_assume_policy" {
  statement {
    sid = "AllowToBeAssumedByScheduler"
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_role" {
  name = "Scheduler-${local.name_suffix}"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_policy.json
  inline_policy {
    name = "AllowSchedulerToInvokeLambda"
    policy = data.aws_iam_policy_document.scheduler_policy.json
  }
}

# Declare all schedules here that are not dynamic

resource "aws_scheduler_schedule" "wvw_reset_schedule" {
  name = "ResetSchedule-${local.name_suffix}"
  group_name = aws_scheduler_schedule_group.schedule_group.id
  description = "Scheduled before the WvW reset to trigger reminders."

  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "cron(${var.wvw_reset_cron})"
  schedule_expression_timezone = var.time_zone

  target {
    arn = var.scheduled_lambda_arn
    role_arn = aws_iam_role.scheduler_role.arn
    input = jsonencode({
      FunctionName = var.scheduled_lambda_arn
      InvocationType = "Event"
      Payload = "{\"lambda_wvw_event_type\":\"wvw_reset\"}" # also responsible for the re-link
    })
  }

  retry_policy {
    maximum_retry_attempts = 0
  }
}

resource "aws_scheduler_schedule" "population_recheck_schedule" {
  name = "PopulationRecheck-${local.name_suffix}"
  group_name = aws_scheduler_schedule_group.schedule_group.id
  description = "Scheduled to check if a selected GW2 world has changed in population."

  flexible_time_window {
    mode = "FLEXIBLE"
    maximum_window_in_minutes = 30
  }
  schedule_expression = "cron(${var.population_recheck_cron})"
  schedule_expression_timezone = var.time_zone

  target {
    arn = var.scheduled_lambda_arn
    role_arn = aws_iam_role.scheduler_role.arn
    input = jsonencode({
      FunctionName = var.scheduled_lambda_arn
      InvocationType = "Event"
      Payload = "{\"lambda_wvw_event_type\":\"home_world_population_recheck\"}"
    })
  }

  retry_policy {
    maximum_retry_attempts = 0
  }
}
