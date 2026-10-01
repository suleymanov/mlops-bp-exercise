terraform {
  backend "s3" {
    bucket       = "mlops-zoomcamp-my-code-1790549480"
    key          = "terraform/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
  
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "model" {
  bucket = "mlops-zoomcamp-my-code-1790549480"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_ecr_repository" "lambda" {
  name = "stream-model-duration"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role" "lambda" {
  name = "stream-model-duration-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "model" {
  function_name = "stream-model-duration"
  role          = aws_iam_role.lambda.arn

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.image_digest}"

  architectures = ["arm64"]

  timeout     = 30
  memory_size = 512

  environment {
    variables = {
      MODEL_BUCKET      = aws_s3_bucket.model.bucket
      MODEL_KEY         = "lin_reg.bin"
      PREDS_STREAM_NAME = aws_kinesis_stream.output.name
    }
  }
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "lambda-model-read"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject"
      ]
      Resource = "${aws_s3_bucket.model.arn}/lin_reg.bin"
    }]
  })
}

resource "aws_kinesis_stream" "input" {
  name             = "input-stream"
  shard_count      = 1
  retention_period = 24
}

resource "aws_kinesis_stream" "output" {
  name             = "output-stream"
  shard_count      = 1
  retention_period = 24
}

resource "aws_iam_role_policy" "lambda_kinesis" {
  name = "lambda-kinesis"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListStreams"
        ]
        Resource = aws_kinesis_stream.input.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:PutRecord",
          "kinesis:PutRecords"
        ]
        Resource = aws_kinesis_stream.output.arn
      }
    ]
  })
}

resource "aws_lambda_event_source_mapping" "kinesis" {
  event_source_arn       = aws_kinesis_stream.input.arn
  function_name          = aws_lambda_function.model.arn
  starting_position      = "LATEST"
  batch_size             = 1
  maximum_retry_attempts = 0
}

data "aws_ecr_image" "lambda" {
  repository_name = aws_ecr_repository.lambda.name
  image_tag       = "latest"
}
