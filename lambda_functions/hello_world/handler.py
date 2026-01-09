"""
Lambda function handler for Hello World example.
"""
import json
from typing import Any, Dict


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function handler that prints Hello World to CloudWatch logs.

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        Response dictionary with status code and message
    """
    print("Hello world")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello world"
        })
    }
