# Coffee Bean Data Application

A Python application for managing coffee bean data using PynamoDB and AWS DynamoDB, with AWS CDK infrastructure as code.

## Project Structure

```
test-uv-project/
├── models/                      # DynamoDB models
│   ├── __init__.py
│   └── coffee_bean.py          # CoffeeBeanData model
├── services/                    # Business logic layer
│   ├── __init__.py
│   └── coffee_service.py       # CRUD operations for coffee beans
├── config/                      # Configuration
│   ├── __init__.py
│   └── settings.py             # AWS region, table settings
├── scripts/                     # Utility scripts
│   ├── __init__.py
│   └── create_tables.py        # DynamoDB table creation
├── cdk/                         # AWS CDK infrastructure
│   ├── __init__.py
│   └── hello_world_stack.py    # Lambda stack definition
├── lambda_functions/            # Lambda function code
│   └── hello_world/
│       └── handler.py          # Hello World Lambda
├── tests/                       # Unit tests
│   ├── __init__.py
│   └── test_coffee_bean.py     # Tests for coffee bean model/service
├── app.py                       # CDK app entry point
├── main.py                      # Application entry point
├── pyproject.toml              # Python dependencies
└── README.md
```

## Features

- **Coffee Bean Data Model**: Track coffee roasts with attributes like origin, roast date, flavor notes, and vendor
- **Service Layer**: Clean separation of business logic with CRUD operations
- **Configuration Management**: Environment-based settings for AWS region and DynamoDB capacity
- **AWS CDK Infrastructure**: Deploy Lambda functions with Infrastructure as Code
- **Unit Tests**: Comprehensive test coverage with pytest

## Prerequisites

- Python 3.13+
- AWS CLI configured with valid credentials
- uv package manager
- AWS CDK CLI (for infrastructure deployment)

## Installation

1. Clone the repository
2. Activate the virtual environment:
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies (already configured via uv):
```bash
uv sync
```

## Configuration

Configure settings via environment variables in [config/settings.py](config/settings.py):

- `AWS_REGION` - AWS region (default: ap-southeast-1)
- `TABLE_NAME_COFFEE_BEAN` - DynamoDB table name (default: coffee-bean-data)
- `READ_CAPACITY_UNITS` - Read capacity (default: 5)
- `WRITE_CAPACITY_UNITS` - Write capacity (default: 5)

## Usage

### Create DynamoDB Tables

```bash
python scripts/create_tables.py
```

### Run the Application

```bash
python main.py
```

This will demonstrate example operations:
- Creating a coffee bean entry
- Retrieving coffee bean data
- Listing all coffee beans

### Using the Coffee Service

```python
from datetime import datetime
from services.coffee_service import CoffeeService

# Create a new coffee bean
coffee = CoffeeService.create_coffee_bean(
    coffee_roast_name="Ethiopian Yirgacheffe",
    country_of_origin="Ethiopia",
    roast_date=datetime.now(),
    flavour_notes=["floral", "citrus", "berry"],
    vendor_name="Blue Bottle Coffee"
)

# Get a coffee bean
coffee = CoffeeService.get_coffee_bean("Ethiopian Yirgacheffe")

# Update a coffee bean
CoffeeService.update_coffee_bean(
    coffee_roast_name="Ethiopian Yirgacheffe",
    flavour_notes=["floral", "citrus", "berry", "tea-like"]
)

# Delete a coffee bean
CoffeeService.delete_coffee_bean("Ethiopian Yirgacheffe")

# List all coffee beans
all_coffees = CoffeeService.list_all_coffee_beans()

# Find by vendor
vendor_coffees = CoffeeService.find_by_vendor("Blue Bottle Coffee")

# Find by country
ethiopian_coffees = CoffeeService.find_by_country("Ethiopia")
```

## Running Tests

```bash
pytest tests/
```

For verbose output:
```bash
pytest tests/ -v
```

For coverage report:
```bash
pytest tests/ --cov=models --cov=services
```

## AWS CDK Deployment

See [CDK_README.md](CDK_README.md) for detailed CDK deployment instructions.

Quick start:
```bash
# Synthesize CloudFormation template
cdk synth

# Deploy Lambda infrastructure
cdk deploy

# Destroy infrastructure
cdk destroy
```

## Coffee Bean Data Model

**Table**: `coffee-bean-data`

**Attributes**:
- `coffee_roast_name` (Primary Key) - Name of the coffee roast
- `country_of_origin` - Country where the beans are from
- `roast_date` - Date when the coffee was roasted
- `flavour_notes` - List of flavor characteristics
- `vendor_name` - Name of the vendor/roaster

## Development

### Code Style

This project uses ruff for linting:
```bash
ruff check .
```

### Project Structure Best Practices

- **models/**: PynamoDB model definitions only
- **services/**: Business logic and data access operations
- **config/**: Application configuration and settings
- **scripts/**: Standalone utility scripts
- **tests/**: Unit and integration tests
- **cdk/**: Infrastructure as Code definitions

## License

This project is open source.
