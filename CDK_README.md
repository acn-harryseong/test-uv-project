# AWS CDK Lambda Deployment

This project contains AWS CDK infrastructure to deploy a Python Lambda function that prints "Hello World" to CloudWatch logs.

## Project Structure

```
.
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── cdk/                            # CDK infrastructure code
│   ├── __init__.py
│   └── hello_world_stack.py       # Lambda stack definition
├── lambda_functions/               # Lambda function code
│   ├── __init__.py
│   └── hello_world/
│       └── handler.py             # Lambda handler
└── pyproject.toml                 # Python dependencies
```

## Prerequisites

- AWS CLI configured with valid credentials
- Python 3.13+
- uv package manager (already configured in this project)
- AWS CDK CLI installed globally

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

## Deployment

### Synthesize CloudFormation template
```bash
cdk synth
```

### Deploy the stack
```bash
cdk deploy
```

### View deployed resources
After deployment, the stack will output the Lambda function ARN and name.

## Testing the Lambda Function

### Option 1: AWS Console
1. Go to AWS Lambda console
2. Find the function named `HelloWorldStack-HelloWorldFunction...`
3. Click "Test" and create a test event
4. Run the test and check CloudWatch Logs

### Option 2: AWS CLI
```bash
aws lambda invoke \
  --function-name HelloWorldStack-HelloWorldFunction... \
  --payload '{}' \
  response.json
```

### View CloudWatch Logs
```bash
aws logs tail /aws/lambda/HelloWorldStack-HelloWorldFunction... --follow
```

## Stack Resources

The CDK stack creates:
- **Lambda Function**: Python 3.13 runtime with 128MB memory
- **IAM Role**: Execution role for the Lambda function
- **CloudWatch Log Group**: 7-day retention for function logs

## Cleanup

To remove all deployed resources:
```bash
cdk destroy
```

## Configuration

You can customize the stack by modifying:
- `cdk/hello_world_stack.py` - Stack resources and configuration
- `lambda_functions/hello_world/handler.py` - Lambda function logic
- `app.py` - Stack instantiation and environment settings

## CDK Commands

- `cdk ls` - List all stacks in the app
- `cdk synth` - Synthesize CloudFormation template
- `cdk diff` - Compare deployed stack with current state
- `cdk deploy` - Deploy the stack
- `cdk destroy` - Delete the stack
- `cdk watch` - Watch for changes and auto-deploy
