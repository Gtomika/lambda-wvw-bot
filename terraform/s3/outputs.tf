output "assets_bucket_arn" {
  value = aws_s3_bucket.assets_bucket.arn
}

output "assets_bucket_name" {
  value = aws_s3_bucket.assets_bucket.bucket
}

output "app_icon_url" {
  value = "https://${aws_s3_bucket.assets_bucket.bucket_regional_domain_name}/${var.key_of_app_icon}"
}

output "assets_bucket_url" {
  value = "https://${aws_s3_bucket.assets_bucket.bucket_regional_domain_name}"
}

output "map_images_prefix" {
  value = var.map_images_prefix
}