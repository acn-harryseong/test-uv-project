"""
CDK Stack for Coffee Bean application infrastructure.
"""
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_logs as logs,
)
from constructs import Construct
from cdk.config import EnvironmentConfig


class CoffeeBeanStack(Stack):
    """
    CDK Stack that creates Coffee Bean application infrastructure.

    Resources:
        - DynamoDB table for coffee bean data
        - Lambda function for Hello World example
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment: str,
        env_config: EnvironmentConfig,
        **kwargs
    ) -> None:
        """
        Initialize the Coffee Bean stack.

        Args:
            scope: CDK scope
            construct_id: Unique identifier for this construct
            environment: Environment name (dev, uat, prod)
            env_config: Environment-specific configuration
            **kwargs: Additional stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # Set removal policy based on environment
        removal_policy = (
            RemovalPolicy.DESTROY
            if env_config["removal_policy"] == "DESTROY"
            else RemovalPolicy.RETAIN
        )

        # Create DynamoDB table for coffee bean data
        self.coffee_bean_table = dynamodb.Table(
            self,
            "CoffeeBeanDataTable",
            table_name=f"coffee-bean-data-{environment}",
            partition_key=dynamodb.Attribute(
                name="coffee_roast_name",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=env_config["read_capacity"],
            write_capacity=env_config["write_capacity"],
            removal_policy=removal_policy,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=env_config["enable_point_in_time_recovery"]
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Get the path to the Lambda function code
        lambda_dir = Path(__file__).parent.parent / "lambda_functions" / "hello_world"

        # Create CloudWatch log group for Lambda function
        log_group = logs.LogGroup(
            self,
            "HelloWorldFunctionLogGroup",
            log_group_name=f"/aws/lambda/CoffeeBeanStack-{environment}-HelloWorldFunction",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=removal_policy,
        )

        # Create the Lambda function
        self.hello_world_function = lambda_.Function(
            self,
            "HelloWorldFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(str(lambda_dir)),
            timeout=Duration.seconds(30),
            memory_size=128,
            description=f"Hello World Lambda function - {environment}",
            log_group=log_group,
            environment={
                "ENVIRONMENT": environment,
                "TABLE_NAME": self.coffee_bean_table.table_name,
            },
        )

        # Grant Lambda function read/write access to DynamoDB table
        self.coffee_bean_table.grant_read_write_data(self.hello_world_function)
