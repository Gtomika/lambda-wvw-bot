output "gw2_users_table_arn" {
  value = aws_dynamodb_table.gw2_users_table.arn
}

output "gw2_users_table_name" {
  value = aws_dynamodb_table.gw2_users_table.name
}

output "gw2_guilds_table_arn" {
  value = aws_dynamodb_table.gw2_guilds_table.arn
}

output "gw2_guilds_table_name" {
  value = aws_dynamodb_table.gw2_guilds_table.name
}