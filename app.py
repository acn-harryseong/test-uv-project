#!/usr/bin/env python3
"""
AWS CDK App entry point for Hello World Lambda deployment.
"""
import aws_cdk as cdk
from cdk.hello_world_stack import HelloWorldStack


app = cdk.App()

HelloWorldStack(
    app,
    "HelloWorldStack",
    description="Stack containing Hello World Lambda function",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region"),
    ),
)

app.synth()
