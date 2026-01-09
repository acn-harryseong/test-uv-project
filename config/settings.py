"""
Application configuration settings.
"""
import os

# Environment (dev, uat, prod)
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")

# DynamoDB Table Names (environment-aware)
TABLE_NAME_COFFEE_BEAN = os.getenv(
    "TABLE_NAME_COFFEE_BEAN",
    f"coffee-bean-data-{ENVIRONMENT}"
)

# DynamoDB Capacity Settings (for local table creation only)
# In production, capacity is managed by CDK
READ_CAPACITY_UNITS = int(os.getenv("READ_CAPACITY_UNITS", "5"))
WRITE_CAPACITY_UNITS = int(os.getenv("WRITE_CAPACITY_UNITS", "5"))
