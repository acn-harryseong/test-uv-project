"""
Coffee bean service for CRUD operations.
"""
from datetime import datetime
from typing import List, Optional
from pynamodb.exceptions import DoesNotExist, PutError
from models.coffee_bean import CoffeeBeanData


class CoffeeService:
    """
    Service class for managing coffee bean data operations.
    """

    @staticmethod
    def create_coffee_bean(
        coffee_roast_name: str,
        country_of_origin: str,
        roast_date: Optional[datetime],
        flavour_notes: List[str],
        vendor_name: str,
        variety: str,
        process: str,
        producer: str,
        image_s3_path: Optional[str] = None,
    ) -> CoffeeBeanData:
        """
        Create a new coffee bean entry.

        Args:
            coffee_roast_name: Name of the coffee roast
            country_of_origin: Country of origin
            roast_date: Date when coffee was roasted (optional)
            flavour_notes: List of flavor characteristics
            vendor_name: Vendor/roaster name
            variety: Coffee variety (e.g., "Red Catuai", "Bourbon")
            process: Processing method (e.g., "washed", "natural")
            producer: Name of the coffee producer
            image_s3_path: S3 path to the coffee bag image (optional)

        Returns:
            Created CoffeeBeanData instance

        Raises:
            PutError: If the item cannot be saved
        """
        coffee = CoffeeBeanData(
            coffee_roast_name=coffee_roast_name,
            country_of_origin=country_of_origin,
            roast_date=roast_date,
            flavour_notes=flavour_notes,
            vendor_name=vendor_name,
            variety=variety,
            process=process,
            producer=producer,
            image_s3_path=image_s3_path,
        )
        coffee.save()
        return coffee

    @staticmethod
    def get_coffee_bean(coffee_roast_name: str) -> Optional[CoffeeBeanData]:
        """
        Retrieve a coffee bean entry by roast name.

        Args:
            coffee_roast_name: Name of the coffee roast

        Returns:
            CoffeeBeanData instance if found, None otherwise
        """
        try:
            return CoffeeBeanData.get(coffee_roast_name)
        except DoesNotExist:
            return None

    @staticmethod
    def update_coffee_bean(
        coffee_roast_name: str,
        country_of_origin: Optional[str] = None,
        roast_date: Optional[datetime] = None,
        flavour_notes: Optional[List[str]] = None,
        vendor_name: Optional[str] = None,
        variety: Optional[str] = None,
        process: Optional[str] = None,
        producer: Optional[str] = None,
        image_s3_path: Optional[str] = None,
    ) -> Optional[CoffeeBeanData]:
        """
        Update an existing coffee bean entry.

        Args:
            coffee_roast_name: Name of the coffee roast
            country_of_origin: New country of origin (optional)
            roast_date: New roast date (optional)
            flavour_notes: New flavor notes (optional)
            vendor_name: New vendor name (optional)
            variety: New coffee variety (optional)
            process: New processing method (optional)
            producer: New producer name (optional)
            image_s3_path: New S3 path to the coffee bag image (optional)

        Returns:
            Updated CoffeeBeanData instance if found, None otherwise
        """
        coffee = CoffeeService.get_coffee_bean(coffee_roast_name)
        if not coffee:
            return None

        actions = []
        if country_of_origin is not None:
            actions.append(CoffeeBeanData.country_of_origin.set(country_of_origin))
        if roast_date is not None:
            actions.append(CoffeeBeanData.roast_date.set(roast_date))
        if flavour_notes is not None:
            actions.append(CoffeeBeanData.flavour_notes.set(flavour_notes))
        if vendor_name is not None:
            actions.append(CoffeeBeanData.vendor_name.set(vendor_name))
        if variety is not None:
            actions.append(CoffeeBeanData.variety.set(variety))
        if process is not None:
            actions.append(CoffeeBeanData.process.set(process))
        if producer is not None:
            actions.append(CoffeeBeanData.producer.set(producer))
        if image_s3_path is not None:
            actions.append(CoffeeBeanData.image_s3_path.set(image_s3_path))

        if actions:
            coffee.update(actions=actions)
            coffee.refresh()

        return coffee

    @staticmethod
    def delete_coffee_bean(coffee_roast_name: str) -> bool:
        """
        Delete a coffee bean entry.

        Args:
            coffee_roast_name: Name of the coffee roast

        Returns:
            True if deleted, False if not found
        """
        coffee = CoffeeService.get_coffee_bean(coffee_roast_name)
        if coffee:
            coffee.delete()
            return True
        return False

    @staticmethod
    def list_all_coffee_beans() -> List[CoffeeBeanData]:
        """
        List all coffee bean entries.

        Returns:
            List of all CoffeeBeanData instances
        """
        return list(CoffeeBeanData.scan())

    @staticmethod
    def find_by_vendor(vendor_name: str) -> List[CoffeeBeanData]:
        """
        Find all coffee beans from a specific vendor.

        Args:
            vendor_name: Vendor name to search for

        Returns:
            List of CoffeeBeanData instances from the vendor
        """
        return list(
            CoffeeBeanData.scan(
                CoffeeBeanData.vendor_name == vendor_name
            )
        )

    @staticmethod
    def find_by_country(country: str) -> List[CoffeeBeanData]:
        """
        Find all coffee beans from a specific country.

        Args:
            country: Country of origin to search for

        Returns:
            List of CoffeeBeanData instances from the country
        """
        return list(
            CoffeeBeanData.scan(
                CoffeeBeanData.country_of_origin == country
            )
        )

    @staticmethod
    def find_by_variety(variety: str) -> List[CoffeeBeanData]:
        """
        Find all coffee beans of a specific variety.

        Args:
            variety: Coffee variety to search for

        Returns:
            List of CoffeeBeanData instances of the variety
        """
        return list(
            CoffeeBeanData.scan(
                CoffeeBeanData.variety == variety
            )
        )

    @staticmethod
    def find_by_process(process: str) -> List[CoffeeBeanData]:
        """
        Find all coffee beans with a specific processing method.

        Args:
            process: Processing method to search for

        Returns:
            List of CoffeeBeanData instances with the process
        """
        return list(
            CoffeeBeanData.scan(
                CoffeeBeanData.process == process
            )
        )

    @staticmethod
    def find_by_producer(producer: str) -> List[CoffeeBeanData]:
        """
        Find all coffee beans from a specific producer.

        Args:
            producer: Producer name to search for

        Returns:
            List of CoffeeBeanData instances from the producer
        """
        return list(
            CoffeeBeanData.scan(
                CoffeeBeanData.producer == producer
            )
        )
