## Coffee Bean Data Extractor Agent

An AI-powered agent that extracts coffee bean information from photos of coffee bags stored in S3 and automatically saves the data to DynamoDB.

## Overview

The Coffee Extractor Agent uses:
- **AWS Bedrock** with Anthropic Claude Sonnet 4.5 for vision and data extraction
- **Strands SDK** for agent orchestration and tool calling
- **Bedrock AgentCore SDK** for inference configuration
- **boto3** for S3 image retrieval
- **PynamoDB** for DynamoDB data persistence

## Architecture

```
┌─────────────┐
│  S3 Bucket  │  Coffee bag photos
│ (Input)     │
└──────┬──────┘
       │
       ├─> Agent retrieves image
       │
┌──────▼────────────────┐
│  Strands Agent        │
│  - Vision analysis    │
│  - Data extraction    │
│  - Tool orchestration │
└──────┬────────────────┘
       │
       ├─> Calls save_coffee_bean_data tool
       │
┌──────▼──────┐
│  DynamoDB   │  Structured coffee data
│  (Output)   │
└─────────────┘
```

## Agent Features

### Vision Analysis
The agent analyzes coffee bag photos to extract:
- Coffee roast name
- Country of origin
- Roast date
- Flavour notes
- Vendor/roaster name
- Coffee variety
- Processing method
- Producer name

### Intelligent Tool Use
The agent autonomously:
1. Analyzes the image using Claude Sonnet 4.5's vision capabilities
2. Extracts structured JSON data from the photo
3. Calls the `save_coffee_bean_data` tool to persist to DynamoDB
4. Returns a confirmation summary

## Project Structure

```
agents/
├── __init__.py
└── coffee_extractor/
    ├── __init__.py
    ├── agent.py          # Main agent implementation
    └── tools.py          # Agent tools (save_coffee_bean_data)

run_coffee_extractor.py   # CLI entry point
```

## Setup

### Prerequisites

1. **AWS Credentials**: Configured with access to:
   - Amazon Bedrock (Claude Sonnet 4.5)
   - S3 (read access to coffee-beans-data bucket)
   - DynamoDB (write access to coffee-bean-data table)

2. **Bedrock Model Access**: Request access to Claude Sonnet 4.5 in Bedrock console

3. **Python Dependencies**: Already included in pyproject.toml:
   ```
   - strands-agents
   - bedrock-agentcore
   - boto3
   - pynamodb
   ```

### Deploy Infrastructure

First, deploy the CDK stack which creates the S3 bucket and DynamoDB table:

```bash
cdk deploy -c environment=dev
```

This creates:
- S3 bucket: `coffee-beans-data-{account_id}-{region}`
- DynamoDB table: `coffee-bean-data-dev`

## Usage

### Basic Usage

```bash
python run_coffee_extractor.py s3://coffee-beans-data-{account}-{region}/photos/ethiopian-coffee.jpg
```

### With Custom Region/Model

```bash
python run_coffee_extractor.py \
  s3://coffee-beans-data-123456789012-us-east-1/photos/colombian.jpg \
  --region us-east-1 \
  --model us.anthropic.claude-sonnet-4-5-v2:0
```

### Programmatic Usage

```python
from agents.coffee_extractor import CoffeeExtractorAgent

# Initialize agent
agent = CoffeeExtractorAgent(
    region="ap-southeast-1",
    model_id="us.anthropic.claude-sonnet-4-5-v2:0"
)

# Extract and save from S3 photo
result = agent.extract_and_save(
    "s3://coffee-beans-data-123456789012-ap-southeast-1/photos/beans.jpg"
)

print(result)
```

## Upload Photos to S3

```bash
# Upload a photo
aws s3 cp my-coffee-bag.jpg s3://coffee-beans-data-{account}-{region}/photos/

# Or use the AWS Console
# Navigate to S3 > coffee-beans-data-{account}-{region} > Upload
```

## Example Output

```
🤖 Initializing Coffee Extractor Agent...
   Region: ap-southeast-1
   Model: us.anthropic.claude-sonnet-4-5-v2:0

📸 Processing image: s3://coffee-beans-data-123456789012-ap-southeast-1/photos/ethiopian.jpg

✅ Successfully processed s3://coffee-beans-data-123456789012-ap-southeast-1/photos/ethiopian.jpg

Agent Response:
I've successfully analyzed the coffee bag photo and extracted the following information:

- Coffee Roast Name: Ethiopian Yirgacheffe Natural
- Country of Origin: Ethiopia
- Roast Date: 2024-01-15
- Flavour Notes: [floral, blueberry, jasmine, bergamot]
- Vendor Name: Blue Bottle Coffee
- Variety: Heirloom
- Process: natural
- Producer: Gedeb Cooperative

The data has been saved to the database successfully.
```

## Agent Configuration

### Model Selection

The agent defaults to Claude Sonnet 4.5 (`us.anthropic.claude-sonnet-4-5-v2:0`), but you can use other vision-capable Bedrock models:

```python
agent = CoffeeExtractorAgent(
    model_id="us.anthropic.claude-opus-4-0:0"  # More capable, higher cost
)
```

### Inference Settings

Configured in [agents/coffee_extractor/agent.py](agents/coffee_extractor/agent.py#L39-L42):

```python
InferenceConfig(
    max_tokens=4096,      # Maximum response length
    temperature=0.0,      # Deterministic output for data extraction
)
```

## Tools

### save_coffee_bean_data

The agent has access to one tool defined in [agents/coffee_extractor/tools.py](agents/coffee_extractor/tools.py):

**Function**: `save_coffee_bean_data(coffee_roast_name, country_of_origin, roast_date, flavour_notes, vendor_name, variety, process, producer)`

**Purpose**: Saves extracted coffee bean data to DynamoDB

**Returns**: Status dictionary with success/error information

## Troubleshooting

### Bedrock Model Access

If you get access denied errors:
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to Claude Sonnet 4.5
4. Wait for approval (usually instant for Claude models)

### S3 Permissions

Ensure your AWS credentials have:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::coffee-beans-data-*",
    "arn:aws:s3:::coffee-beans-data-*/*"
  ]
}
```

### DynamoDB Permissions

Required permissions:
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem",
    "dynamodb:GetItem"
  ],
  "Resource": "arn:aws:dynamodb:*:*:table/coffee-bean-data-*"
}
```

## Advanced Usage

### Batch Processing

Process multiple images:

```python
from agents.coffee_extractor import CoffeeExtractorAgent

agent = CoffeeExtractorAgent()

s3_paths = [
    "s3://bucket/photo1.jpg",
    "s3://bucket/photo2.jpg",
    "s3://bucket/photo3.jpg",
]

for path in s3_paths:
    print(f"\nProcessing: {path}")
    result = agent.extract_and_save(path)
    print(result)
```

### Custom Error Handling

```python
result = agent.extract_from_photo("s3://bucket/photo.jpg")

if result["status"] == "success":
    print(f"Extracted data in {result['tool_calls']} tool calls")
    print(f"Response: {result['response']}")
else:
    print(f"Error: {result['error']}")
```

## Cost Considerations

### Bedrock Pricing
- **Claude Sonnet 4.5**: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **Images**: Counted as input tokens based on resolution
- **Typical cost per image**: $0.01 - $0.05

### S3 Costs
- **Storage**: $0.023 per GB/month (first 50TB)
- **GET requests**: $0.0004 per 1,000 requests

### DynamoDB Costs
- **Provisioned capacity**: Based on CDK configuration
- **Dev**: 1 RCU/WCU = ~$0.65/month
- **Prod**: 10 RCU/WCU = ~$6.50/month

## Best Practices

1. **Image Quality**: Use high-resolution, well-lit photos for best extraction
2. **Consistent Format**: Photos should clearly show all label information
3. **Error Handling**: Always check the status in production code
4. **Monitoring**: Log all extractions for audit trails
5. **Validation**: Review agent-extracted data before production use

## Integration with Existing Services

The agent integrates seamlessly with existing services:

```python
from agents.coffee_extractor import CoffeeExtractorAgent
from services.coffee_service import CoffeeService

# Extract from photo
agent = CoffeeExtractorAgent()
agent.extract_and_save("s3://bucket/photo.jpg")

# Query the saved data
coffee = CoffeeService.get_coffee_bean("Ethiopian Yirgacheffe Natural")
print(f"Found: {coffee.variety} from {coffee.producer}")
```

## Related Documentation

- [Main README](README.md) - Project overview
- [CDK README](CDK_README.md) - Infrastructure deployment
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Quick deployment reference
