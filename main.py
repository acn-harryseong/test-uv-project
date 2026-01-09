#!/usr/bin/env python3
"""
Coffee Bean Data Application - Example usage.
"""
from datetime import datetime
from services.coffee_service import CoffeeService


def main():
    """
    Main application demonstrating coffee bean data operations.
    """
    print("Coffee Bean Data Application")
    print("=" * 50)

    # Example: Create a new coffee bean entry
    print("\n1. Creating a new coffee bean entry...")
    try:
        coffee = CoffeeService.create_coffee_bean(
            coffee_roast_name="Ethiopian Yirgacheffe",
            country_of_origin="Ethiopia",
            roast_date=datetime.now(),
            flavour_notes=["floral", "citrus", "berry"],
            vendor_name="Blue Bottle Coffee",
            variety="Heirloom",
            process="washed",
            producer="Gedeb Cooperative"
        )
        print(f"   Created: {coffee.coffee_roast_name}")
    except Exception as e:
        print(f"   Note: {e}")

    # Example: Get a coffee bean
    print("\n2. Retrieving coffee bean...")
    coffee = CoffeeService.get_coffee_bean("Ethiopian Yirgacheffe")
    if coffee:
        print(f"   Found: {coffee.coffee_roast_name}")
        print(f"   Origin: {coffee.country_of_origin}")
        print(f"   Vendor: {coffee.vendor_name}")
        print(f"   Variety: {coffee.variety}")
        print(f"   Process: {coffee.process}")
        print(f"   Producer: {coffee.producer}")
        print(f"   Flavours: {', '.join(coffee.flavour_notes)}")
    else:
        print("   Not found")

    # Example: List all coffee beans
    print("\n3. Listing all coffee beans...")
    all_coffees = CoffeeService.list_all_coffee_beans()
    print(f"   Total: {len(all_coffees)} coffee beans")
    for c in all_coffees:
        print(f"   - {c.coffee_roast_name} ({c.vendor_name})")

    print("\n" + "=" * 50)
    print("To deploy infrastructure, run: cdk deploy -c environment=dev")
    print("For more info, see: CDK_README.md")


if __name__ == "__main__":
    main()
