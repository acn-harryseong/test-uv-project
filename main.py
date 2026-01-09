"""
Coffee Bean Data DynamoDB Table using PynamoDB
"""
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
    ListAttribute,
)


class CoffeeBeanData(Model):
    """
    PynamoDB model for Coffee Bean Data table.
    """
    class Meta:
        table_name = "coffee-bean-data"
        region = "us-east-1"  # Change to your preferred region

    # Primary key: Coffee roast name
    coffee_roast_name = UnicodeAttribute(hash_key=True)

    # Attributes
    country_of_origin = UnicodeAttribute()
    roast_date = UTCDateTimeAttribute()
    flavour_notes = ListAttribute(of=UnicodeAttribute)
    vendor_name = UnicodeAttribute()


def create_table():
    """
    Create the DynamoDB table if it doesn't exist.
    """
    try:
        if not CoffeeBeanData.exists():
            CoffeeBeanData.create_table(
                read_capacity_units=5,
                write_capacity_units=5,
                wait=True
            )
            print("Table 'coffee-bean-data' created successfully!")
        else:
            print("Table 'coffee-bean-data' already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")


def main():
    """
    Main function to create the coffee bean data table.
    """
    print("Creating Coffee Bean Data DynamoDB table...")
    create_table()


if __name__ == "__main__":
    main()
