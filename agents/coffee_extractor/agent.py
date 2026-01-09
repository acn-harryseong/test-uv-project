"""
Coffee Bean Data Extractor Agent using Strands SDK.
"""
import json
import boto3
from typing import Optional
from strands import Agent
from strands.models import BedrockModel
from agents.coffee_extractor.tools import save_coffee_bean_data


class CoffeeExtractorAgent:
    """
    Agent that extracts coffee bean data from photos stored in S3
    and saves the data to DynamoDB.
    """

    def __init__(
        self,
        region: str = "ap-southeast-1",
        model_id: str = "us.anthropic.claude-sonnet-4-5-v2:0",
    ):
        """
        Initialize the Coffee Extractor Agent.

        Args:
            region: AWS region
            model_id: Bedrock model ID to use
        """
        self.region = region
        self.model_id = model_id
        self.s3_client = boto3.client('s3', region_name=region)

        self.bedrock_model = BedrockModel(
            model_id=model_id,
            temperature=0.3,
            top_p=0.8,
        )

        # Create the Strands agent with tools
        self.agent = Agent(
            name="CoffeeExtractor",
            model=model_id,
            system_prompt=self._get_system_prompt(),
            tools=[save_coffee_bean_data],
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are a coffee bean data extraction specialist. Your task is to analyze photos of coffee bean bags and extract all relevant information.

When given a photo of a coffee bean bag, you should:

1. Carefully examine the image to identify all text and labels
2. Extract the following information:
   - Coffee roast name (the product name)
   - Country of origin
   - Roast date (convert to ISO format YYYY-MM-DD)
   - Flavour notes (as a list of strings like ["dried berry", "dark plum", "black grapes", "lavender"])
   - Vendor name (the roaster/company name like "NYLON")
   - Variety (coffee variety like "Red Catuai", "Bourbon", "Heirloom")
   - Process (processing method like "washed", "natural", "honey")
   - Producer (the farm or producer name)

3. Once you've extracted all the data, use the save_coffee_bean_data tool to save it to the database.

4. Return a summary of what was extracted and saved.

Important guidelines:
- If any information is not visible or unclear in the image, make a reasonable inference or note it as "Unknown"
- Roast dates should be in ISO format (YYYY-MM-DD)
- Flavour notes should be a list of descriptive terms
- Be thorough and accurate in your extraction
"""

    def _get_s3_image(self, s3_path: str) -> bytes:
        """
        Retrieve image from S3.

        Args:
            s3_path: S3 path in format s3://bucket/key

        Returns:
            Image bytes

        Raises:
            ValueError: If S3 path is invalid
        """
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Invalid S3 path: {s3_path}")

        # Parse S3 path
        path_parts = s3_path[5:].split('/', 1)
        if len(path_parts) != 2:
            raise ValueError(f"Invalid S3 path format: {s3_path}")

        bucket = path_parts[0]
        key = path_parts[1]

        # Download from S3
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    def extract_from_photo(self, s3_path: str) -> dict:
        """
        Extract coffee bean data from a photo stored in S3.

        Args:
            s3_path: S3 path to the photo (e.g., s3://bucket/path/to/image.jpg)

        Returns:
            Dictionary with extraction results
        """
        try:
            # Get the image from S3
            image_bytes = self._get_s3_image(s3_path)

            # Prepare the message with the image
            user_message = f"""Please analyze this coffee bean bag photo and extract all the coffee bean information.
The photo is from: {s3_path}

Extract all relevant data and save it using the save_coffee_bean_data tool."""

            # TODO: FIX AGENT INVOKE CODE
            # Run the agent with the image
            response = self.agent(
                user_message
            )

            return {
                "status": "success",
                "s3_path": s3_path,
                "response": response.content,
                "tool_calls": len(response.tool_calls) if hasattr(response, 'tool_calls') else 0,
            }

        except Exception as e:
            return {
                "status": "error",
                "s3_path": s3_path,
                "error": str(e),
            }

    def extract_and_save(self, s3_path: str) -> str:
        """
        Extract coffee bean data from photo and save to DynamoDB.

        This is a convenience method that returns a formatted string response.

        Args:
            s3_path: S3 path to the photo

        Returns:
            Formatted string with results
        """
        result = self.extract_from_photo(s3_path)

        if result["status"] == "success":
            return f"✅ Successfully processed {s3_path}\n\nAgent Response:\n{result['response']}"
        else:
            return f"❌ Error processing {s3_path}\n\nError: {result['error']}"
