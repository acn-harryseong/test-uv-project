#!/usr/bin/env python3
"""
AWS CDK App entry point for Coffee Bean application deployment.
"""
import os
import aws_cdk as cdk
from cdk.coffee_bean_stack import CoffeeBeanStack
from cdk.config import get_env_config


app = cdk.App()

# Get environment from context or environment variable (default: dev)
environment = app.node.try_get_context("environment") or os.getenv("ENVIRONMENT", "dev")

# Get environment-specific configuration
env_config = get_env_config(environment)

# Create the stack for the specified environment
CoffeeBeanStack(
    app,
    f"CoffeeBeanStack-{environment}",
    environment=environment,
    env_config=env_config,
    description=f"Coffee Bean application infrastructure - {environment}",
    env=cdk.Environment(
        account=env_config["account"] or os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=env_config["region"],
    ),
    tags={
        "Environment": environment,
        "Application": "CoffeeBeanApp",
        "ManagedBy": "CDK",
    },
)

app.synth()
