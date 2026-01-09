#!/usr/bin/env python3
"""
Script to create DynamoDB tables.
"""
from models.coffee_bean import CoffeeBeanData
from config.settings import READ_CAPACITY_UNITS, WRITE_CAPACITY_UNITS


def create_coffee_bean_table():
    """
    Create the Coffee Bean Data DynamoDB table if it doesn't exist.
    """
    try:
        if not CoffeeBeanData.exists():
            print(f"Creating table '{CoffeeBeanData.Meta.table_name}'...")
            CoffeeBeanData.create_table(
                read_capacity_units=READ_CAPACITY_UNITS,
                write_capacity_units=WRITE_CAPACITY_UNITS,
                wait=True
            )
            print(f"Table '{CoffeeBeanData.Meta.table_name}' created successfully!")
        else:
            print(f"Table '{CoffeeBeanData.Meta.table_name}' already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise


def main():
    """
    Main function to create all tables.
    """
    print("Creating DynamoDB tables...")
    create_coffee_bean_table()
    print("Done!")


if __name__ == "__main__":
    main()
