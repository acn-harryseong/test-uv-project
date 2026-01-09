# AWS CDK Infrastructure Deployment

This project contains AWS CDK infrastructure to deploy the Coffee Bean application with DynamoDB tables and Lambda functions across multiple environments (dev, uat, prod).

## Project Structure

```
.
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── cdk/                            # CDK infrastructure code
│   ├── __init__.py
│   ├── config.py                  # Environment configurations
│   ├── coffee_bean_stack.py       # Main application stack
│   └── hello_world_stack.py       # Legacy Lambda stack (deprecated)
├── lambda_functions/               # Lambda function code
│   └── hello_world/
│       └── handler.py             # Lambda handler
├── scripts/                        # Deployment scripts
│   ├── deploy.sh                  # Bash deployment script
│   └── deploy.ps1                 # PowerShell deployment script
└── pyproject.toml                 # Python dependencies
```

## Prerequisites

- AWS CLI configured with valid credentials
- Python 3.13+
- uv package manager (already configured in this project)
- AWS CDK CLI installed globally
- Appropriate AWS permissions for CloudFormation, DynamoDB, Lambda, and IAM

## Setup

1. Install CDK CLI globally (if not already installed):
```bash
npm install -g aws-cdk
```

2. Ensure your virtual environment is activated:
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

3. Bootstrap CDK (one-time setup per AWS account/region):
```bash
cdk bootstrap
```

## Environment Configuration

The application supports three environments with different configurations:

### Development (dev)
- **Region**: ap-southeast-1
- **Read Capacity**: 1 unit
- **Write Capacity**: 1 unit
- **Removal Policy**: DESTROY (table will be deleted on stack deletion)
- **Point-in-Time Recovery**: Disabled
- **Table Name**: `coffee-bean-data-dev`

### UAT
- **Region**: ap-southeast-1
- **Read Capacity**: 5 units
- **Write Capacity**: 5 units
- **Removal Policy**: RETAIN (table protected from deletion)
- **Point-in-Time Recovery**: Enabled
- **Table Name**: `coffee-bean-data-uat`

### Production (prod)
- **Region**: ap-southeast-1
- **Read Capacity**: 10 units
- **Write Capacity**: 10 units
- **Removal Policy**: RETAIN (table protected from deletion)
- **Point-in-Time Recovery**: Enabled
- **Table Name**: `coffee-bean-data-prod`

## Deployment

### Quick Deployment (Using Scripts)

**Windows (PowerShell):**
```powershell
# Deploy to dev
.\scripts\deploy.ps1 dev

# Deploy to uat
.\scripts\deploy.ps1 uat

# Deploy to prod
.\scripts\deploy.ps1 prod
```

**Linux/macOS (Bash):**
```bash
# Make script executable (first time only)
chmod +x scripts/deploy.sh

# Deploy to dev
./scripts/deploy.sh dev

# Deploy to uat
./scripts/deploy.sh uat

# Deploy to prod
./scripts/deploy.sh prod
```

### Manual Deployment

#### Deploy to Development
```bash
cdk synth -c environment=dev
cdk deploy -c environment=dev
```

#### Deploy to UAT
```bash
cdk synth -c environment=uat
cdk deploy -c environment=uat
```

#### Deploy to Production
```bash
cdk synth -c environment=prod
cdk deploy -c environment=prod
```

## Stack Resources

Each environment stack creates:

### DynamoDB Table
- **Table Name**: `coffee-bean-data-{environment}`
- **Partition Key**: `coffee_roast_name` (String)
- **Encryption**: AWS managed encryption
- **Billing**: Provisioned capacity (environment-specific)
- **Backup**: Point-in-time recovery (UAT/Prod only)

### Lambda Function
- **Runtime**: Python 3.13
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **Environment Variables**:
  - `ENVIRONMENT`: Current environment (dev/uat/prod)
  - `TABLE_NAME`: DynamoDB table name
- **Permissions**: Read/write access to DynamoDB table
- **Logs**: CloudWatch Logs with 7-day retention

## Testing the Deployment

### View Stacks
```bash
cdk list
```

Expected output:
```
CoffeeBeanStack-dev
CoffeeBeanStack-uat
CoffeeBeanStack-prod
```

### Check Stack Differences
```bash
cdk diff -c environment=dev
```

### Test Lambda Function

**Via AWS Console:**
1. Go to AWS Lambda console
2. Find function: `CoffeeBeanStack-{env}-HelloWorldFunction...`
3. Create and run test event
4. Check CloudWatch Logs

**Via AWS CLI:**
```bash
aws lambda invoke \
  --function-name CoffeeBeanStack-dev-HelloWorldFunction... \
  --payload '{}' \
  response.json
```

### Verify DynamoDB Table

```bash
# List tables
aws dynamodb list-tables

# Describe table
aws dynamodb describe-table --table-name coffee-bean-data-dev
```

## Using the Application with CDK-Created Tables

Set the environment variable before running your application:

```bash
# For dev environment
export ENVIRONMENT=dev
python main.py

# For uat environment
export ENVIRONMENT=uat
python main.py

# For prod environment
export ENVIRONMENT=prod
python main.py
```

**Windows (PowerShell):**
```powershell
$env:ENVIRONMENT = "dev"
python main.py
```

## Cleanup

To remove all deployed resources for an environment:

```bash
# Development (will delete DynamoDB table)
cdk destroy -c environment=dev

# UAT (DynamoDB table will be retained)
cdk destroy -c environment=uat

# Production (DynamoDB table will be retained)
cdk destroy -c environment=prod
```

**Note**: UAT and Production tables have `RETAIN` removal policy and will not be deleted when the stack is destroyed. You must manually delete them from the AWS Console if needed.

## Configuration Customization

### Modify Environment Settings

Edit [cdk/config.py](cdk/config.py) to change:
- AWS region
- Read/write capacity units
- Removal policy
- Point-in-time recovery settings

### Change AWS Account

Set your AWS account ID in environment variables:
```bash
export CDK_DEFAULT_ACCOUNT=123456789012
```

Or modify [cdk/config.py](cdk/config.py) to set `account` value for each environment.

## CDK Commands Reference

- `cdk list` - List all stacks in the app
- `cdk synth -c environment=ENV` - Synthesize CloudFormation template
- `cdk diff -c environment=ENV` - Compare deployed stack with current state
- `cdk deploy -c environment=ENV` - Deploy the stack
- `cdk destroy -c environment=ENV` - Delete the stack
- `cdk watch -c environment=ENV` - Watch for changes and auto-deploy
- `cdk doctor` - Check CDK setup

## Troubleshooting

### Bootstrap Error
If you get a bootstrap error:
```bash
cdk bootstrap aws://ACCOUNT-ID/ap-southeast-1
```

### Permission Errors
Ensure your AWS credentials have permissions for:
- CloudFormation (full access)
- DynamoDB (create/delete tables)
- Lambda (create/update functions)
- IAM (create roles and policies)
- CloudWatch Logs (create log groups)

### Stack Already Exists
If deploying to an environment that already has a stack:
```bash
cdk deploy -c environment=ENV --force
```

## Best Practices

1. **Always deploy to dev first** to test infrastructure changes
2. **Review diffs** before deploying to uat/prod: `cdk diff -c environment=prod`
3. **Use CI/CD** for automated deployments to uat/prod
4. **Tag resources** appropriately (already configured in stacks)
5. **Monitor costs** per environment using AWS Cost Explorer with tags
6. **Backup production data** - Point-in-time recovery is enabled for prod
