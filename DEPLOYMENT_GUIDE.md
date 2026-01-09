# Quick Deployment Guide

This is a quick reference for deploying the Coffee Bean application to different environments.

## Prerequisites Checklist

- [ ] AWS CLI configured (`aws configure`)
- [ ] CDK CLI installed (`npm install -g aws-cdk`)
- [ ] Virtual environment activated
- [ ] CDK bootstrapped (`cdk bootstrap`)

## Quick Commands

### Deploy to Development
```powershell
# Windows
.\scripts\deploy.ps1 dev

# Linux/macOS
./scripts/deploy.sh dev
```

### Deploy to UAT
```powershell
# Windows
.\scripts\deploy.ps1 uat

# Linux/macOS
./scripts/deploy.sh uat
```

### Deploy to Production
```powershell
# Windows
.\scripts\deploy.ps1 prod

# Linux/macOS
./scripts/deploy.sh prod
```

## Environment Variables

Set before running the application:

```powershell
# Windows
$env:ENVIRONMENT = "dev"

# Linux/macOS
export ENVIRONMENT=dev
```

## What Gets Created

| Resource | Dev | UAT | Prod |
|----------|-----|-----|------|
| DynamoDB Table | `coffee-bean-data-dev` | `coffee-bean-data-uat` | `coffee-bean-data-prod` |
| Read Capacity | 1 | 5 | 10 |
| Write Capacity | 1 | 5 | 10 |
| Point-in-Time Recovery | ❌ | ✅ | ✅ |
| Deletion Protection | ❌ | ✅ | ✅ |
| Lambda Function | ✅ | ✅ | ✅ |

## Key Files

- [cdk/config.py](cdk/config.py) - Environment configurations
- [cdk/coffee_bean_stack.py](cdk/coffee_bean_stack.py) - Infrastructure definition
- [app.py](app.py) - CDK app entry point
- [scripts/deploy.ps1](scripts/deploy.ps1) - Windows deployment script
- [scripts/deploy.sh](scripts/deploy.sh) - Linux/macOS deployment script

## Common Tasks

### View what will be deployed
```bash
cdk diff -c environment=dev
```

### List all stacks
```bash
cdk list
```

### Destroy a stack
```bash
cdk destroy -c environment=dev
```

### Check DynamoDB table
```bash
aws dynamodb describe-table --table-name coffee-bean-data-dev
```

## Important Notes

⚠️ **Production Safety**: UAT and Prod tables have `RETAIN` policy - they won't be deleted when you run `cdk destroy`

⚠️ **Always test in dev first** before deploying to UAT or Production

✅ **Point-in-time recovery** is enabled for UAT and Production for data protection

For detailed documentation, see [CDK_README.md](CDK_README.md)
