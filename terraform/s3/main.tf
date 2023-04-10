resource "aws_s3_bucket" "assets_bucket" {
  bucket = "Assets-${var.app_name}-${var.environment}-${var.aws_region}"
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
    actions = ["s3:GetItem"]
    principals {
      identifiers = ["*"]
      type        = "*"
    }
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