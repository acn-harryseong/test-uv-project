"""
Tools for Coffee Bean Data Extractor Agent.
"""
from datetime import datetime
from typing import Any, Dict
from services.coffee_service import CoffeeService
from agents.coffee_extractor.logging_config import get_logger

logger = get_logger(__name__)


def save_coffee_bean_data(
    coffee_roast_name: str,
    country_of_origin: str,
    roast_date: str | None,
    flavour_notes: list[str],
    vendor_name: str,
    variety: str,
    process: str,
    producer: str,
    image_s3_path: str | None = None,
) -> Dict[str, Any]:
    """
    Save coffee bean data to DynamoDB.

    Args:
        coffee_roast_name: Name of the coffee roast
        country_of_origin: Country where the beans are from
        roast_date: Date when coffee was roasted (ISO format string), or None if not available
        flavour_notes: List of flavor characteristics
        vendor_name: Name of the vendor/roaster
        variety: Coffee variety (e.g., "Red Catuai", "Bourbon")
        process: Processing method (e.g., "washed", "natural")
        producer: Name of the coffee producer
        image_s3_path: S3 path to the coffee bag image (optional)

    Returns:
        Dictionary with status and message
    """
    try:
        logger.debug(f"Saving coffee bean data for: {coffee_roast_name}")

        # Parse the roast date if provided
        parsed_date = datetime.fromisoformat(roast_date.replace('Z', '+00:00')) if roast_date else None

        if roast_date:
            logger.debug(f"Parsed roast date: {roast_date} -> {parsed_date}")
        else:
            logger.debug("No roast date provided")

        # Save to DynamoDB
        coffee = CoffeeService.create_coffee_bean(
            coffee_roast_name=coffee_roast_name,
            country_of_origin=country_of_origin,
            roast_date=parsed_date,
            flavour_notes=flavour_notes,
            vendor_name=vendor_name,
            variety=variety,
            process=process,
            producer=producer,
            image_s3_path=image_s3_path,
        )

        logger.info(f"Successfully saved coffee bean data for '{coffee_roast_name}' to DynamoDB")

        return {
            "status": "success",
            "message": f"Successfully saved coffee bean data for '{coffee_roast_name}'",
            "coffee_roast_name": coffee.coffee_roast_name,
        }
    except Exception as e:
        logger.error(f"Failed to save coffee bean data for '{coffee_roast_name}': {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to save coffee bean data: {str(e)}",
        }
