"""
Coffee Bean Data Extractor Agent using Strands SDK.
"""
import json
import boto3
from io import BytesIO
from PIL import Image
from strands import Agent
from strands.models import BedrockModel
from agents.coffee_extractor.tools import save_coffee_bean_data
from agents.coffee_extractor.models import CoffeeBeanData
from agents.coffee_extractor.prompts import COFFEE_EXTRACTOR_SYSTEM_PROMPT


class CoffeeExtractorAgent:
    """
    Agent that extracts coffee bean data from photos stored in S3
    and saves the data to DynamoDB.
    """

    def __init__(
        self,
        region: str = "ap-southeast-1",
        model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
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
            temperature=0,
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
        return COFFEE_EXTRACTOR_SYSTEM_PROMPT

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

    def _compress_image(self, image_bytes: bytes, max_height: int = 240) -> bytes:
        """
        Compress and resize image to reduce file size.

        Args:
            image_bytes: Original image bytes
            max_height: Maximum height in pixels (default 240p)

        Returns:
            Compressed image bytes as JPEG
        """
        # Open the image
        img = Image.open(BytesIO(image_bytes))

        # Calculate new dimensions maintaining aspect ratio
        aspect_ratio = img.width / img.height
        new_height = max_height
        new_width = int(aspect_ratio * new_height)

        # Resize the image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for JPEG compatibility)
        if img_resized.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img_resized.size, (255, 255, 255))
            if img_resized.mode == 'P':
                img_resized = img_resized.convert('RGBA')
            background.paste(img_resized, mask=img_resized.split()[-1] if img_resized.mode in ('RGBA', 'LA') else None)
            img_resized = background

        # Save to bytes with JPEG compression
        output = BytesIO()
        img_resized.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()

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

            # Compress the image to reduce file size (720p resolution)
            compressed_image_bytes = self._compress_image(image_bytes, max_height=720)

            # Generate compressed image S3 path
            # Parse the original S3 path
            path_parts = s3_path[5:].split('/', 1)
            bucket = path_parts[0]
            key = path_parts[1]

            # Create compressed image key by adding _compressed before the extension
            if '.' in key:
                base_key, ext = key.rsplit('.', 1)
                compressed_key = f"{base_key}_compressed.jpg"
            else:
                compressed_key = f"{key}_compressed.jpg"

            compressed_s3_path = f"s3://{bucket}/{compressed_key}"

            # Upload compressed image to S3
            self.s3_client.put_object(
                Bucket=bucket,
                Key=compressed_key,
                Body=compressed_image_bytes,
                ContentType='image/jpeg'
            )

            # Run the agent with structured output and image
            # Using Strands SDK format: image field with format and source containing bytes
            coffee_data = self.agent.structured_output(
                CoffeeBeanData,
                [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": compressed_image_bytes,
                            },
                        },
                    },
                    {
                        "text": f"Please analyze this coffee bean bag photo and extract all the coffee bean information from the image.",
                    },
                ]
            )

            print(f"Agent structured output response: {json.dumps(coffee_data.model_dump())}")

            # Save the extracted data using the tool
            save_result = save_coffee_bean_data(
                coffee_roast_name=coffee_data.coffee_roast_name,
                country_of_origin=coffee_data.country_of_origin,
                roast_date=coffee_data.roast_date,
                flavour_notes=coffee_data.flavour_notes,
                vendor_name=coffee_data.vendor_name,
                variety=coffee_data.variety,
                process=coffee_data.process,
                producer=coffee_data.producer,
                image_s3_path=s3_path,
            )

            return {
                "status": "success",
                "s3_path": s3_path,
                "compressed_s3_path": compressed_s3_path,
                "extracted_data": coffee_data.model_dump(),
                "save_result": save_result,
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
            return f"✅ Successfully processed {s3_path}\n\nAgent Response:\n{json.dumps(result)}"
        else:
            return f"❌ Error processing {s3_path}\n\nError: {json.dumps(result)}"
