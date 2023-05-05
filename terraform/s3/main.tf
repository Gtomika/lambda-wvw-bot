resource "aws_s3_bucket" "assets_bucket" {
  bucket = "assets-${lower(var.app_name)}-${var.environment}-${var.aws_region}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "asset_versioning" {
  bucket = aws_s3_bucket.assets_bucket.id
  versioning_configuration {
    status = "Disabled"
  }
}

data "aws_iam_policy_document" "assets_bucket_policy" {
  statement {
    sid = "AllowPublicGet"
    effect = "Allow"
    actions = ["s3:GetObject"]
    principals {
      identifiers = ["*"]
      type        = "*"
    }
    resources = ["${aws_s3_bucket.assets_bucket.arn}/*"]
  }
}

# only 1 lifecycle configuration is supported per bucket!
resource "aws_s3_bucket_lifecycle_configuration" "map_images_lifecycle" {
  bucket = aws_s3_bucket.assets_bucket.id
  rule {
    id     = "expire_map_images_lifecycle"
    filter = {
      prefix = var.map_images_prefix
    }
    expiration {
      days = var.map_images_expiration_days
    }
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "assets_policy_attachment" {
  bucket = aws_s3_bucket.assets_bucket.id
  policy = data.aws_iam_policy_document.assets_bucket_policy.json
}

resource "aws_s3_object" "app_icon_asset" {
  bucket = aws_s3_bucket.assets_bucket.bucket
  key    = var.key_of_app_icon
  source = var.path_to_app_icon
  etag = filemd5(var.path_to_app_icon)
  force_destroy = true
}