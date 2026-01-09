"""
Tools for Coffee Bean Data Extractor Agent.
"""
from datetime import datetime
from typing import Any, Dict
from services.coffee_service import CoffeeService


def save_coffee_bean_data(
    coffee_roast_name: str,
    country_of_origin: str,
    roast_date: str,
    flavour_notes: list[str],
    vendor_name: str,
    variety: str,
    process: str,
    producer: str,
) -> Dict[str, Any]:
    """
    Save coffee bean data to DynamoDB.

    Args:
        coffee_roast_name: Name of the coffee roast
        country_of_origin: Country where the beans are from
        roast_date: Date when coffee was roasted (ISO format string)
        flavour_notes: List of flavor characteristics
        vendor_name: Name of the vendor/roaster
        variety: Coffee variety (e.g., "Red Catuai", "Bourbon")
        process: Processing method (e.g., "washed", "natural")
        producer: Name of the coffee producer

    Returns:
        Dictionary with status and message
    """
    try:
        # Parse the roast date
        parsed_date = datetime.fromisoformat(roast_date.replace('Z', '+00:00'))

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
        )

        return {
            "status": "success",
            "message": f"Successfully saved coffee bean data for '{coffee_roast_name}'",
            "coffee_roast_name": coffee.coffee_roast_name,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save coffee bean data: {str(e)}",
        }
