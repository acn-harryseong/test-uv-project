#!/usr/bin/env python3
"""
Entry point for running the Coffee Bean Data Extractor Agent.
"""
import argparse
import os
from agents.coffee_extractor import CoffeeExtractorAgent


def main():
    """Main entry point for the coffee extractor agent."""
    parser = argparse.ArgumentParser(
        description="Extract coffee bean data from photos in S3"
    )
    parser.add_argument(
        "s3_path",
        help="S3 path to the coffee bag photo (e.g., s3://bucket/path/to/image.jpg)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_REGION", "ap-southeast-1"),
        help="AWS region (default: ap-southeast-1)",
    )
    parser.add_argument(
        "--model",
        default="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        help="Bedrock model ID (default: Claude Sonnet 4.5)",
    )

    args = parser.parse_args()

    # Initialize the agent
    print(f"🤖 Initializing Coffee Extractor Agent...")
    print(f"   Region: {args.region}")
    print(f"   Model: {args.model}")
    print()

    agent = CoffeeExtractorAgent(
        region=args.region,
        model_id=args.model,
    )

    # Process the image
    print(f"📸 Processing image: {args.s3_path}")
    print()

    result = agent.extract_and_save(args.s3_path)
    print(result)


if __name__ == "__main__":
    main()
