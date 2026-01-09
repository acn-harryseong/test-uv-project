"""
Unit tests for Coffee Bean Data model and service.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from models.coffee_bean import CoffeeBeanData
from services.coffee_service import CoffeeService


class TestCoffeeBeanData:
    """Tests for CoffeeBeanData model."""

    def test_model_attributes(self):
        """Test that the model has the correct attributes."""
        assert hasattr(CoffeeBeanData, 'coffee_roast_name')
        assert hasattr(CoffeeBeanData, 'country_of_origin')
        assert hasattr(CoffeeBeanData, 'roast_date')
        assert hasattr(CoffeeBeanData, 'flavour_notes')
        assert hasattr(CoffeeBeanData, 'vendor_name')

    def test_table_name(self):
        """Test that the table name is correctly set."""
        assert CoffeeBeanData.Meta.table_name == "coffee-bean-data"


class TestCoffeeService:
    """Tests for CoffeeService."""

    @patch('services.coffee_service.CoffeeBeanData')
    def test_create_coffee_bean(self, mock_model):
        """Test creating a coffee bean entry."""
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance

        roast_date = datetime.now()
        result = CoffeeService.create_coffee_bean(
            coffee_roast_name="Test Roast",
            country_of_origin="Colombia",
            roast_date=roast_date,
            flavour_notes=["chocolate", "nutty"],
            vendor_name="Test Vendor"
        )

        mock_model.assert_called_once_with(
            coffee_roast_name="Test Roast",
            country_of_origin="Colombia",
            roast_date=roast_date,
            flavour_notes=["chocolate", "nutty"],
            vendor_name="Test Vendor"
        )
        mock_instance.save.assert_called_once()

    @patch('services.coffee_service.CoffeeBeanData')
    def test_get_coffee_bean_found(self, mock_model):
        """Test getting a coffee bean that exists."""
        mock_coffee = MagicMock()
        mock_model.get.return_value = mock_coffee

        result = CoffeeService.get_coffee_bean("Test Roast")

        mock_model.get.assert_called_once_with("Test Roast")
        assert result == mock_coffee

    @patch('services.coffee_service.CoffeeBeanData')
    def test_get_coffee_bean_not_found(self, mock_model):
        """Test getting a coffee bean that doesn't exist."""
        from pynamodb.exceptions import DoesNotExist
        mock_model.get.side_effect = DoesNotExist()

        result = CoffeeService.get_coffee_bean("Nonexistent")

        assert result is None

    @patch('services.coffee_service.CoffeeBeanData')
    def test_delete_coffee_bean_success(self, mock_model):
        """Test deleting an existing coffee bean."""
        mock_coffee = MagicMock()
        mock_model.get.return_value = mock_coffee

        result = CoffeeService.delete_coffee_bean("Test Roast")

        mock_coffee.delete.assert_called_once()
        assert result is True

    @patch('services.coffee_service.CoffeeBeanData')
    def test_delete_coffee_bean_not_found(self, mock_model):
        """Test deleting a non-existent coffee bean."""
        from pynamodb.exceptions import DoesNotExist
        mock_model.get.side_effect = DoesNotExist()

        result = CoffeeService.delete_coffee_bean("Nonexistent")

        assert result is False
