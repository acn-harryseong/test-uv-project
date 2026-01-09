# PowerShell deployment script for Coffee Bean application
# Usage: .\scripts\deploy.ps1 [environment]
# Example: .\scripts\deploy.ps1 dev

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'uat', 'prod')]
    [string]$Environment = 'dev'
)

Write-Host "Deploying to $Environment environment..." -ForegroundColor Green

# Set environment variable
$env:ENVIRONMENT = $Environment

# Synthesize CloudFormation template
Write-Host "Synthesizing CDK stack..." -ForegroundColor Yellow
cdk synth -c environment=$Environment

# Deploy the stack
Write-Host "Deploying CDK stack..." -ForegroundColor Yellow
cdk deploy -c environment=$Environment --require-approval never

Write-Host "Deployment to $Environment completed successfully!" -ForegroundColor Green
