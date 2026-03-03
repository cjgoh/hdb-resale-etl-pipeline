HDB Data Platform - AI Deployment Agent
=======================================

Overview
--------
This project provides an AI-assisted deployment agent (AIDeployment.py) that automates
the provisioning of AWS infrastructure, ETL pipeline setup, validation, monitoring,
and documentation for the HDB resale flat data platform.

Prerequisites
-------------
- Python 3.9 or higher
- Virtual environment (venv) recommended
- AWS CLI installed and configured (aws configure)
- Terraform installed
- Required Python packages:
  pip install boto3

Quick Start
-----------
1. Clone the repository:
   git clone https://github.com/your-org/HDB-V1.git
   cd HDB-V1

2. Activate virtual environment:
   Windows: .venv\Scripts\activate
   Linux/Mac: source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure AWS CLI:
   aws configure
   (Provide AWS Access Key, Secret Key, region e.g. ap-southeast-1, and output format)

5. Run the AI Deployment Agent:
   python AIDeployment.py

What the Agent Does
-------------------
1. Provision Infrastructure:
   - VPC, subnets, Internet/NAT Gateway
   - S3 buckets (Raw, Cleaned, Transformed, Failed, Hashed)
   - IAM roles and policies

2. Deploy ETL Pipeline:
   - Package and deploy Lambda ingestion function
   - Upload Glue ETL script to S3
   - Create Glue job and Data Catalog tables

3. Validation:
   - Run sample ingestion from data.gov.sg
   - Execute Glue ETL job
   - Run Athena queries to confirm transformed data

4. Monitoring and Alerts:
   - Configure CloudWatch dashboards
   - Set SNS/email alerts for job failures

5. Security and Compliance:
   - Scan IAM policies for least privilege
   - Verify S3 encryption and access restrictions
   - Generate CloudTrail audit report

6. Documentation:
   - Auto-generate README and Quick Start guide
   - Save architecture diagram

Validation Steps
----------------
After deployment, confirm:
- Raw, Cleaned, Transformed, and Hashed datasets exist in S3
- Failed dataset contains duplicates/anomalies
- Athena queries return expected results
- Tableau connects via Athena driver and loads dashboards

Cleanup
-------
To tear down resources and avoid costs:
   terraform destroy


