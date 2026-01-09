"""
CDK Stack for Hello World Lambda function.
"""
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_logs as logs,
)
from constructs import Construct


class HelloWorldStack(Stack):
    """CDK Stack that creates a Lambda function that prints Hello World."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initialize the Hello World stack.

        Args:
            scope: CDK scope
            construct_id: Unique identifier for this construct
            **kwargs: Additional stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # Get the path to the Lambda function code
        lambda_dir = Path(__file__).parent.parent / "lambda_functions" / "hello_world"

        # Create the Lambda function
        self.hello_world_function = lambda_.Function(
            self,
            "HelloWorldFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(str(lambda_dir)),
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Lambda function that prints Hello World to CloudWatch logs",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )
