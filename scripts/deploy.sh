#!/bin/bash
# Deployment script for Coffee Bean application
# Usage: ./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh dev

set -e

ENVIRONMENT=${1:-dev}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|uat|prod)$ ]]; then
    echo "Error: Invalid environment '$ENVIRONMENT'"
    echo "Valid environments: dev, uat, prod"
    exit 1
fi

echo "Deploying to $ENVIRONMENT environment..."

# Set environment variable
export ENVIRONMENT=$ENVIRONMENT

# Synthesize CloudFormation template
echo "Synthesizing CDK stack..."
cdk synth -c environment=$ENVIRONMENT

# Deploy the stack
echo "Deploying CDK stack..."
cdk deploy -c environment=$ENVIRONMENT --require-approval never

echo "Deployment to $ENVIRONMENT completed successfully!"
