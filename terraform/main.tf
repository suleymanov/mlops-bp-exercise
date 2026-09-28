terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "model" {
  bucket = "mlops-zoomcamp-my-code-1790549480"
}
