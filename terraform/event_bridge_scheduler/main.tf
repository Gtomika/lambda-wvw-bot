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
      Payload = {
        lambda_wvw_event_type: "wvw_reset" # It's also responsible for the wvw relink
      }
    })
  }
}

resource "aws_scheduler_schedule" "population_recheck_schedule" {
  name = "PopulationRecheck-${local.name_suffix}"
  group_name = aws_scheduler_schedule_group.schedule_group.id

  flexible_time_window {
    mode = "FLEXIBLE"
  }
  schedule_expression = "cron(${var.population_recheck_cron})"
  schedule_expression_timezone = var.time_zone

  target {
    arn = var.scheduled_lambda_arn
    role_arn = aws_iam_role.scheduler_role.arn
    input = jsonencode({
      FunctionName = var.scheduled_lambda_arn
      InvocationType = "Event"
      Payload = {
        lambda_wvw_event_type: "home_world_population_recheck"
      }
    })
  }
}
