"""
Coffee Bean Data Extractor Agent using Strands SDK.
"""
import json
import boto3
from io import BytesIO
from typing import Any
from botocore.exceptions import ClientError, BotoCoreError
from PIL import Image, UnidentifiedImageError
from strands import Agent
from agents.coffee_extractor.tools import save_coffee_bean_data
from agents.coffee_extractor.models import CoffeeBeanData
from agents.coffee_extractor.prompts import COFFEE_EXTRACTOR_SYSTEM_PROMPT
from agents.coffee_extractor.logging_config import get_logger

logger = get_logger(__name__)


class S3PathError(ValueError):
    """Exception raised for invalid S3 paths."""
    pass


class ImageProcessingError(Exception):
    """Exception raised for image processing errors."""
    pass


class CoffeeExtractorAgent:
    """
    Agent that extracts coffee bean data from photos stored in S3
    and saves the data to DynamoDB.

    Example:
        >>> agent = CoffeeExtractorAgent(region="ap-southeast-1")
        >>> result = agent.extract_from_photo("s3://my-bucket/coffee.jpg")
        >>> print(result["status"])
        'success'
    """

    def __init__(
        self,
        region: str = "ap-southeast-1",
        model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        compression_height: int = 720,
        compression_quality: int = 85,
        compressed_suffix: str = "_compressed.jpg",
        upload_compressed: bool = True,
        system_prompt: str | None = None,
    ):
        """
        Initialize the Coffee Extractor Agent.

        Args:
            region: AWS region
            model_id: Bedrock model ID to use
            compression_height: Maximum height in pixels for compressed images
            compression_quality: JPEG compression quality (1-100)
            compressed_suffix: Suffix to add to compressed image filenames
            upload_compressed: Whether to upload compressed image back to S3
            system_prompt: Custom system prompt (defaults to COFFEE_EXTRACTOR_SYSTEM_PROMPT)
        """
        self.region = region
        self.model_id = model_id
        self.compression_height = compression_height
        self.compression_quality = compression_quality
        self.compressed_suffix = compressed_suffix
        self.upload_compressed = upload_compressed
        self.s3_client = boto3.client('s3', region_name=region)

        # Create the Strands agent with tools
        self.agent = Agent(
            name="CoffeeExtractor",
            model=model_id,
            system_prompt=system_prompt or COFFEE_EXTRACTOR_SYSTEM_PROMPT,
            tools=[save_coffee_bean_data],
        )

        logger.info(f"Initialized CoffeeExtractorAgent with model={model_id}, region={region}")

    def _parse_s3_path(self, s3_path: str) -> tuple[str, str]:
        """
        Parse S3 path into bucket and key components.

        Args:
            s3_path: S3 path in format s3://bucket/key

        Returns:
            Tuple of (bucket, key)

        Raises:
            S3PathError: If S3 path format is invalid

        Example:
            >>> agent._parse_s3_path("s3://my-bucket/path/to/file.jpg")
            ('my-bucket', 'path/to/file.jpg')
        """
        if not s3_path.startswith('s3://'):
            raise S3PathError(f"Invalid S3 path format: {s3_path}. Expected format: s3://bucket/key")

        path_without_prefix = s3_path[5:]  # Remove 's3://'
        if '/' not in path_without_prefix:
            raise S3PathError(f"Invalid S3 path format: {s3_path}. Missing key component.")

        parts = path_without_prefix.split('/', 1)
        bucket = parts[0]
        key = parts[1]

        if not bucket or not key:
            raise S3PathError(f"Invalid S3 path format: {s3_path}. Bucket or key is empty.")

        return bucket, key

    def _get_s3_image(self, s3_path: str) -> bytes:
        """
        Retrieve image from S3 with error handling.

        Args:
            s3_path: S3 path in format s3://bucket/key

        Returns:
            Image bytes

        Raises:
            S3PathError: If S3 path format is invalid
            ClientError: If S3 object cannot be retrieved
        """
        bucket, key = self._parse_s3_path(s3_path)

        try:
            logger.debug(f"Downloading image from S3: bucket={bucket}, key={key}")
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            image_bytes = response['Body'].read()
            logger.info(f"Successfully downloaded {len(image_bytes)} bytes from {s3_path}")
            return image_bytes
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Failed to download from S3: {error_code} - {str(e)}")
            raise
        except BotoCoreError as e:
            logger.error(f"BotoCore error while downloading from S3: {str(e)}")
            raise

    def _compress_image(self, image_bytes: bytes, max_height: int | None = None) -> bytes:
        """
        Compress and resize image to reduce file size.

        Args:
            image_bytes: Original image bytes
            max_height: Maximum height in pixels (uses self.compression_height if None)

        Returns:
            Compressed image bytes as JPEG

        Raises:
            ImageProcessingError: If image cannot be processed
        """
        if max_height is None:
            max_height = self.compression_height

        try:
            # Open the image
            img = Image.open(BytesIO(image_bytes))
            original_size = (img.width, img.height)
            logger.debug(f"Original image size: {original_size}")

            # Skip compression if image is already smaller
            if img.height <= max_height:
                logger.info(f"Image height ({img.height}px) already at or below target ({max_height}px), skipping resize")
                max_height = img.height

            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = img.width / img.height
            new_height = max_height
            new_width = int(aspect_ratio * new_height)

            # Resize the image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.debug(f"Resized image to: ({new_width}, {new_height})")

            # Convert to RGB if necessary (for JPEG compatibility)
            if img_resized.mode in ('RGBA', 'LA', 'P'):
                logger.debug(f"Converting image from {img_resized.mode} to RGB")
                background = Image.new('RGB', img_resized.size, (255, 255, 255))
                if img_resized.mode == 'P':
                    img_resized = img_resized.convert('RGBA')
                background.paste(img_resized, mask=img_resized.split()[-1] if img_resized.mode in ('RGBA', 'LA') else None)
                img_resized = background

            # Save to bytes with JPEG compression
            output = BytesIO()
            img_resized.save(output, format='JPEG', quality=self.compression_quality, optimize=True)
            compressed_bytes = output.getvalue()

            compression_ratio = len(compressed_bytes) / len(image_bytes) * 100
            logger.info(f"Compressed image: {len(image_bytes)} -> {len(compressed_bytes)} bytes ({compression_ratio:.1f}%)")

            return compressed_bytes

        except UnidentifiedImageError as e:
            logger.error(f"Cannot identify image format: {str(e)}")
            raise ImageProcessingError(f"Invalid or unsupported image format: {str(e)}")
        except Exception as e:
            logger.error(f"Image compression failed: {str(e)}")
            raise ImageProcessingError(f"Failed to compress image: {str(e)}")

    def _upload_compressed_image(self, compressed_bytes: bytes, s3_path: str) -> str:
        """
        Upload compressed image to S3.

        Args:
            compressed_bytes: Compressed image bytes
            s3_path: Original S3 path

        Returns:
            S3 path of the uploaded compressed image

        Raises:
            S3PathError: If S3 path is invalid
            ClientError: If upload fails
        """
        bucket, key = self._parse_s3_path(s3_path)

        # Create compressed image key by adding suffix before the extension
        if '.' in key:
            base_key, _ = key.rsplit('.', 1)
            compressed_key = f"{base_key}{self.compressed_suffix}"
        else:
            compressed_key = f"{key}{self.compressed_suffix}"

        compressed_s3_path = f"s3://{bucket}/{compressed_key}"

        try:
            logger.debug(f"Uploading compressed image to S3: bucket={bucket}, key={compressed_key}")
            self.s3_client.put_object(
                Bucket=bucket,
                Key=compressed_key,
                Body=compressed_bytes,
                ContentType='image/jpeg'
            )
            logger.info(f"Successfully uploaded compressed image to {compressed_s3_path}")
            return compressed_s3_path
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Failed to upload compressed image to S3: {error_code} - {str(e)}")
            raise
        except BotoCoreError as e:
            logger.error(f"BotoCore error while uploading to S3: {str(e)}")
            raise

    def _extract_coffee_data(self, image_bytes: bytes) -> CoffeeBeanData:
        """
        Extract coffee bean data from image using AI model.

        Args:
            image_bytes: Image bytes to analyze

        Returns:
            Extracted coffee bean data

        Raises:
            Exception: If extraction fails
        """
        logger.debug("Starting AI extraction of coffee data")

        coffee_data = self.agent.structured_output(
            CoffeeBeanData,
            [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {
                            "bytes": image_bytes,
                        },
                    },
                },
                {
                    "text": "Please analyze this coffee bean bag photo and extract all the coffee bean information from the image.",
                },
            ]
        )

        logger.info(f"Successfully extracted coffee data: {coffee_data.coffee_roast_name}")
        logger.debug(f"Extracted data: {json.dumps(coffee_data.model_dump())}")

        return coffee_data

    def extract_from_photo(self, s3_path: str) -> dict[str, Any]:
        """
        Extract coffee bean data from a photo stored in S3.

        This method orchestrates the full extraction pipeline:
        1. Download image from S3
        2. Compress image for AI processing
        3. Optionally upload compressed image back to S3
        4. Extract coffee data using AI
        5. Save extracted data to DynamoDB

        Args:
            s3_path: S3 path to the photo (e.g., s3://bucket/path/to/image.jpg)

        Returns:
            Dictionary with extraction results containing:
                - status: "success" or "error"
                - s3_path: Original S3 path
                - compressed_s3_path: Path to compressed image (if uploaded)
                - extracted_data: Extracted coffee bean data
                - save_result: Result of database save operation
                - error: Error message (if status is "error")

        Example:
            >>> result = agent.extract_from_photo("s3://my-bucket/coffee.jpg")
            >>> print(result["status"])
            'success'
        """
        logger.info(f"Starting extraction for {s3_path}")

        try:
            # Step 1: Download image from S3
            image_bytes = self._get_s3_image(s3_path)

            # Step 2: Compress the image
            compressed_image_bytes = self._compress_image(image_bytes)

            # Step 3: Upload compressed image to S3 (if enabled)
            compressed_s3_path = None
            if self.upload_compressed:
                compressed_s3_path = self._upload_compressed_image(compressed_image_bytes, s3_path)

            # Step 4: Extract coffee data using AI
            coffee_data = self._extract_coffee_data(compressed_image_bytes)

            # Step 5: Save to DynamoDB
            logger.debug("Saving extracted data to DynamoDB")
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

            logger.info(f"Successfully completed extraction for {s3_path}")

            result = {
                "status": "success",
                "s3_path": s3_path,
                "extracted_data": coffee_data.model_dump(),
                "save_result": save_result,
            }

            if compressed_s3_path:
                result["compressed_s3_path"] = compressed_s3_path

            return result

        except S3PathError as e:
            logger.error(f"S3 path error: {str(e)}")
            return {
                "status": "error",
                "s3_path": s3_path,
                "error": f"Invalid S3 path: {str(e)}",
                "error_type": "S3PathError",
            }
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"AWS client error: {error_code} - {str(e)}")
            return {
                "status": "error",
                "s3_path": s3_path,
                "error": f"AWS error ({error_code}): {str(e)}",
                "error_type": "ClientError",
            }
        except ImageProcessingError as e:
            logger.error(f"Image processing error: {str(e)}")
            return {
                "status": "error",
                "s3_path": s3_path,
                "error": f"Image processing failed: {str(e)}",
                "error_type": "ImageProcessingError",
            }
        except Exception as e:
            logger.exception(f"Unexpected error during extraction: {str(e)}")
            return {
                "status": "error",
                "s3_path": s3_path,
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__,
            }

    def extract_and_save(self, s3_path: str) -> str:
        """
        Extract coffee bean data from photo and save to DynamoDB.

        This is a convenience method that returns a formatted string response.
        Use this for CLI/user-facing output. For programmatic access, use
        extract_from_photo() instead.

        Args:
            s3_path: S3 path to the photo

        Returns:
            Formatted string with results (human-readable)

        Example:
            >>> result = agent.extract_and_save("s3://my-bucket/coffee.jpg")
            >>> print(result)
            ✅ Successfully processed s3://my-bucket/coffee.jpg
            ...
        """
        logger.info(f"extract_and_save called for {s3_path}")
        result = self.extract_from_photo(s3_path)

        if result["status"] == "success":
            output = f"✅ Successfully processed {s3_path}\n\nAgent Response:\n{json.dumps(result, indent=2)}"
            logger.info(f"extract_and_save completed successfully for {s3_path}")
            return output
        else:
            output = f"❌ Error processing {s3_path}\n\nError: {json.dumps(result, indent=2)}"
            logger.warning(f"extract_and_save failed for {s3_path}: {result.get('error', 'Unknown error')}")
            return output
