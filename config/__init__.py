"""
Configuration package.
"""
from config.settings import (
    ENVIRONMENT,
    AWS_REGION,
    TABLE_NAME_COFFEE_BEAN,
    READ_CAPACITY_UNITS,
    WRITE_CAPACITY_UNITS,
)

__all__ = [
    "ENVIRONMENT",
    "AWS_REGION",
    "TABLE_NAME_COFFEE_BEAN",
    "READ_CAPACITY_UNITS",
    "WRITE_CAPACITY_UNITS",
]
