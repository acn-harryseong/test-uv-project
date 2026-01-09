"""
CDK environment configuration for different stages.
"""
from typing import TypedDict


class EnvironmentConfig(TypedDict):
    """Environment configuration type."""
    account: str
    region: str
    read_capacity: int
    write_capacity: int
    removal_policy: str
    enable_point_in_time_recovery: bool


# Environment configurations
ENVIRONMENTS: dict[str, EnvironmentConfig] = {
    "dev": {
        "account": None,  # Will use default AWS account from CLI
        "region": "ap-southeast-1",
        "read_capacity": 1,
        "write_capacity": 1,
        "removal_policy": "DESTROY",  # Allow table deletion in dev
        "enable_point_in_time_recovery": False,
    },
    "uat": {
        "account": None,  # Will use default AWS account from CLI
        "region": "ap-southeast-1",
        "read_capacity": 5,
        "write_capacity": 5,
        "removal_policy": "RETAIN",  # Protect table in UAT
        "enable_point_in_time_recovery": True,
    },
    "prod": {
        "account": None,  # Will use default AWS account from CLI
        "region": "ap-southeast-1",
        "read_capacity": 10,
        "write_capacity": 10,
        "removal_policy": "RETAIN",  # Protect table in production
        "enable_point_in_time_recovery": True,
    },
}


def get_env_config(environment: str) -> EnvironmentConfig:
    """
    Get configuration for a specific environment.

    Args:
        environment: Environment name (dev, uat, prod)

    Returns:
        Environment configuration

    Raises:
        ValueError: If environment is not recognized
    """
    if environment not in ENVIRONMENTS:
        raise ValueError(
            f"Unknown environment: {environment}. "
            f"Valid environments: {', '.join(ENVIRONMENTS.keys())}"
        )
    return ENVIRONMENTS[environment]
