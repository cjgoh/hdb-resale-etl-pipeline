provider "aws" {
  region = "ap-southeast-1" # Singapore
}

# =====================================================
# Networking
# =====================================================
resource "aws_vpc" "hdb_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.hdb_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.hdb_vpc.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.hdb_vpc.id
}

resource "aws_nat_gateway" "nat" {
  subnet_id     = aws_subnet.public.id
  allocation_id = aws_eip.nat.id
}

resource "aws_eip" "nat" {
  vpc = true
}
# =====================================================
# S3 Buckets
# =====================================================
resource "aws_s3_bucket" "raw" {
  bucket = "hdb-raw-zone"
}

resource "aws_s3_bucket" "cleaned" {
  bucket = "hdb-cleaned-zone"
}

resource "aws_s3_bucket" "transformed" {
  bucket = "hdb-transformed-zone"
}
# =====================================================
# IAM Roles
# =====================================================
resource "aws_iam_role" "lambda_role" {
  name               = "lambda-ingestion-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Attach policies for S3, Glue, Athena
resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# =====================================================
# Lambda Ingestion
# =====================================================
resource "aws_lambda_function" "ingest" {
  function_name = "hdb-ingest"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  # zip file with your ingestion code
  filename      = "lambda.zip"
}

# =====================================================
# Glue ETL
# =====================================================
resource "aws_glue_job" "etl" {
  name     = "hdb-etl-job"
  role_arn = aws_iam_role.lambda_role.arn
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.raw.bucket}/scripts/etl.py"
  }
}

# =====================================================
# Glue Data Catalog
# =====================================================
resource "aws_glue_catalog_database" "hdb" {
  name = "hdb_resale"
}

resource "aws_glue_catalog_table" "resale" {
  name          = "resale_table"
  database_name = aws_glue_catalog_database.hdb.name
  table_type    = "EXTERNAL_TABLE"
}

# =====================================================
# Athena
# =====================================================
resource "aws_athena_workgroup" "default" {
  name = "hdb-workgroup"
}

# =====================================================
# VPC Endpoint / PrivateLink
# =====================================================
resource "aws_vpc_endpoint" "athena" {
  vpc_id            = aws_vpc.hdb_vpc.id
  service_name      = "com.amazonaws.ap-southeast-1.athena"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private.id]
  security_group_ids = []
}

# =====================================================
# CloudTrail
# =====================================================
resource "aws_cloudtrail" "main" {
  name                          = "hdb-trail"
  s3_bucket_name                = aws_s3_bucket.raw.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
}
