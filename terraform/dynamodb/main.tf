resource "aws_dynamodb_table" "gw2_users_table" {
  name = "Gw2Users-${var.environment}-${var.aws_region}"
  stream_enabled = false

  billing_mode   = "PROVISIONED"
  read_capacity  = var.dynamodb_read_capacity
  write_capacity = var.dynamodb_write_capacity

  attribute {
    name = var.gw2_users_hash_key
    type = "S"
  }
  hash_key = var.gw2_users_hash_key
}

resource "aws_dynamodb_table" "gw2_guilds_table" {
  name = "Gw2Guilds-${var.environment}-${var.aws_region}"
  stream_enabled = false

  billing_mode   = "PROVISIONED"
  read_capacity  = var.dynamodb_read_capacity
  write_capacity = var.dynamodb_write_capacity

  attribute {
    name = var.gw2_guilds_hash_key
    type = "S"
  }
  hash_key = var.gw2_guilds_hash_key
}