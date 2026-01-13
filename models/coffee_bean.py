"""
Coffee Bean Data DynamoDB model.
"""
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
    ListAttribute,
)
from config.settings import AWS_REGION, TABLE_NAME_COFFEE_BEAN


class CoffeeBeanData(Model):
    """
    PynamoDB model for Coffee Bean Data table.

    Attributes:
        coffee_roast_name: Primary key - name of the coffee roast
        country_of_origin: Country where the coffee beans are from
        roast_date: Date when the coffee was roasted
        flavour_notes: List of flavor characteristics
        vendor_name: Name of the vendor/roaster
        variety: Coffee variety (e.g., "Red Catuai", "Tabi", "Bourbon")
        process: Processing method (e.g., "washed", "natural", "natural anaerobic")
        producer: Name of the coffee producer (e.g., "Octavio Peralta")
        image_s3_path: S3 path to the coffee bag image (optional)
    """
    class Meta:
        table_name = TABLE_NAME_COFFEE_BEAN
        region = AWS_REGION

    # Primary key: Coffee roast name
    coffee_roast_name = UnicodeAttribute(hash_key=True)

    # Attributes
    country_of_origin = UnicodeAttribute()
    roast_date = UTCDateTimeAttribute(null=True)
    flavour_notes = ListAttribute(of=UnicodeAttribute)
    vendor_name = UnicodeAttribute()
    variety = UnicodeAttribute()
    process = UnicodeAttribute()
    producer = UnicodeAttribute()
    image_s3_path = UnicodeAttribute(null=True)
