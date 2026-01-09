# Coffee Bean Data Application

A Python application for managing coffee bean data using PynamoDB and AWS DynamoDB, with AWS CDK infrastructure as code. Includes an AI-powered agent for extracting coffee data from photos using AWS Bedrock and Strands SDK.

## Project Structure

```
test-uv-project/
├── agents/                      # AI Agents
│   └── coffee_extractor/
│       ├── __init__.py
│       ├── agent.py            # Strands agent implementation
│       └── tools.py            # Agent tools (DynamoDB save)
├── models/                      # DynamoDB models
│   ├── __init__.py
│   └── coffee_bean.py          # CoffeeBeanData model
├── services/                    # Business logic layer
│   ├── __init__.py
│   └── coffee_service.py       # CRUD operations for coffee beans
├── config/                      # Configuration
│   ├── __init__.py
│   └── settings.py             # AWS region, table settings
├── scripts/                     # Deployment scripts
│   ├── __init__.py
│   ├── deploy.sh               # Bash deployment script
│   └── deploy.ps1              # PowerShell deployment script
├── cdk/                         # AWS CDK infrastructure
│   ├── __init__.py
│   ├── config.py               # Environment configurations
│   └── coffee_bean_stack.py    # Main application stack
├── lambda_functions/            # Lambda function code
│   └── hello_world/
│       └── handler.py          # Hello World Lambda
├── tests/                       # Unit tests
│   ├── __init__.py
│   └── test_coffee_bean.py     # Tests for coffee bean model/service
├── app.py                       # CDK app entry point
├── main.py                      # Application entry point
├── run_coffee_extractor.py     # Coffee extractor agent CLI
├── pyproject.toml              # Python dependencies
└── README.md
```

## Features

- **Coffee Bean Data Model**: Track coffee roasts with attributes like origin, roast date, flavor notes, variety, process, and producer
- **AI-Powered Data Extraction**: Extract coffee data from photos using AWS Bedrock (Claude Sonnet 4.5) and Strands SDK
- **Service Layer**: Clean separation of business logic with CRUD operations
- **S3 Storage**: Secure photo storage in environment-specific S3 buckets
- **Configuration Management**: Environment-based settings for dev/uat/prod
- **AWS CDK Infrastructure**: Multi-environment infrastructure deployment with DynamoDB, S3, and Lambda
- **Unit Tests**: Comprehensive test coverage with pytest

## Prerequisites

- Python 3.13+
- AWS CLI configured with valid credentials
- uv package manager
- AWS CDK CLI (for infrastructure deployment)
- AWS Bedrock access to Claude Sonnet 4.5 (for AI agent)

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

- `ENVIRONMENT` - Environment (dev, uat, prod) (default: dev)
- `AWS_REGION` - AWS region (default: ap-southeast-1)
- `TABLE_NAME_COFFEE_BEAN` - DynamoDB table name (default: coffee-bean-data-{ENVIRONMENT})

## Infrastructure Deployment

**DynamoDB tables are created via AWS CDK**, not through Python scripts. See [CDK_README.md](CDK_README.md) for full deployment instructions.

Quick deployment:
```bash
# Deploy to dev environment
cdk deploy -c environment=dev

# Or use the deployment script (Windows)
.\scripts\deploy.ps1 dev
```

## Usage

### AI-Powered Photo Extraction (Recommended)

Extract coffee bean data from photos automatically:

```bash
# Upload photo to S3
aws s3 cp my-coffee-bag.jpg s3://coffee-beans-data-{account}-{region}/photos/

# Run the extractor agent
python run_coffee_extractor.py s3://coffee-beans-data-{account}-{region}/photos/my-coffee-bag.jpg
```

The agent will:
1. Retrieve the photo from S3
2. Analyze it using Claude Sonnet 4.5's vision capabilities
3. Extract all coffee bean data (name, origin, variety, process, etc.)
4. Automatically save to DynamoDB

See [AGENT_README.md](AGENT_README.md) for detailed agent documentation.

### Manual Data Entry

Run the application for manual operations:

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
    vendor_name="Blue Bottle Coffee",
    variety="Heirloom",
    process="washed",
    producer="Gedeb Cooperative"
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

# Find by variety
bourbon_coffees = CoffeeService.find_by_variety("Bourbon")

# Find by process
washed_coffees = CoffeeService.find_by_process("washed")

# Find by producer
producer_coffees = CoffeeService.find_by_producer("Octavio Peralta")
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

See [CDK_README.md](CDK_README.md) for detailed CDK deployment instructions and [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for quick reference.

Quick start:
```bash
# Deploy to dev environment
cdk deploy -c environment=dev

# Deploy to uat environment
cdk deploy -c environment=uat

# Deploy to prod environment
cdk deploy -c environment=prod

# Destroy dev infrastructure (table will be deleted)
cdk destroy -c environment=dev
```

## Coffee Bean Data Model

**Table**: `coffee-bean-data-{environment}` (e.g., `coffee-bean-data-dev`)

**Attributes**:
- `coffee_roast_name` (Primary Key) - Name of the coffee roast
- `country_of_origin` - Country where the beans are from
- `roast_date` - Date when the coffee was roasted
- `flavour_notes` - List of flavor characteristics
- `vendor_name` - Name of the vendor/roaster
- `variety` - Coffee variety (e.g., "Red Catuai", "Bourbon", "Heirloom")
- `process` - Processing method (e.g., "washed", "natural", "natural anaerobic")
- `producer` - Name of the coffee producer (e.g., "Octavio Peralta")

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
