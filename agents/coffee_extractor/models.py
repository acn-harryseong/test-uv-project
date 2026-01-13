"""
Data models for Coffee Bean Data Extractor Agent.
"""
from pydantic import BaseModel, Field


class CoffeeBeanData(BaseModel):
    """Structured data model for coffee bean information extracted from photos."""
    coffee_roast_name: str = Field(description="Name of the coffee roast/product")
    country_of_origin: str = Field(description="Country where the beans are from")
    roast_date: str | None = Field(default=None, description="Date when coffee was roasted (ISO format YYYY-MM-DD), or null if not visible")
    flavour_notes: list[str] = Field(description="List of flavor characteristics")
    vendor_name: str = Field(description="Name of the vendor/roaster")
    variety: str = Field(description="Coffee variety (e.g., 'Red Catuai', 'Bourbon', 'Heirloom')")
    process: str = Field(description="Processing method (e.g., 'washed', 'natural', 'honey')")
    producer: str = Field(description="Name of the coffee producer/farm")
