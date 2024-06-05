resource "aws_ssm_parameter" "world_functionality_enabled_parameter" {
  name = var.world_functionality_enabled_param_name
  type = "String"
  value = var.world_functionality_enabled_by_default
  allowed_pattern = "^(true|false)$"
  description = "Whether the world functionality of the bot is enabled or not. Typically disabled during beta events and restructurings."

  # This can be updated later, but we don't want to trigger a change in the resource
  lifecycle {
    ignore_changes = [value]
  }
}
