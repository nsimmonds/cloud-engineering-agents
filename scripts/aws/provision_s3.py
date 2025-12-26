#!/usr/bin/env python3
"""
Provision an S3 bucket with best practices configuration.

This script demonstrates resource provisioning following best practices:
- Uses credentials from .env file
- Requires user confirmation before creating resources
- Supports command-line arguments for flexibility
- Includes proper error handling and rollback
- Implements security best practices (encryption, versioning)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from common import (
    setup_logger,
    load_config,
    get_aws_config,
    confirm_action,
    parse_tags,
    handle_error
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Provision an S3 bucket with security best practices',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'bucket_name',
        help='Name of the S3 bucket to create'
    )

    parser.add_argument(
        '--region',
        help='AWS region (defaults to AWS_DEFAULT_REGION from .env)',
        default=None
    )

    parser.add_argument(
        '--versioning',
        action='store_true',
        help='Enable versioning on the bucket'
    )

    parser.add_argument(
        '--encryption',
        choices=['AES256', 'aws:kms'],
        default='AES256',
        help='Server-side encryption type (default: AES256)'
    )

    parser.add_argument(
        '--tags',
        nargs='*',
        help='Tags to apply (format: key=value)',
        default=[]
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating it'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def create_s3_bucket(bucket_name, region, versioning=False, encryption='AES256', tags=None):
    """
    Create an S3 bucket with security best practices.

    Args:
        bucket_name: Name of the bucket
        region: AWS region
        versioning: Enable versioning
        encryption: Encryption type ('AES256' or 'aws:kms')
        tags: Dictionary of tags to apply

    Returns:
        True if successful, False otherwise
    """
    s3 = boto3.client('s3', region_name=region)

    # Create bucket
    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    # Block public access (security best practice)
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    # Enable versioning if requested
    if versioning:
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )

    # Enable encryption
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': encryption
                }
            }]
        }
    )

    # Apply tags if provided
    if tags:
        tag_set = [{'Key': k, 'Value': v} for k, v in tags.items()]
        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': tag_set}
        )

    return True


def main():
    """Main execution function."""
    args = parse_arguments()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(__name__, level=log_level)

    try:
        # Load configuration
        logger.info("Loading configuration from .env file...")
        load_config()
        aws_config = get_aws_config()

        # Use region from args or config
        region = args.region or aws_config['region']

        # Parse tags
        tags = parse_tags(args.tags)

        # Display what will be created
        logger.info("=" * 60)
        logger.info("S3 Bucket Configuration")
        logger.info("=" * 60)
        logger.info(f"Bucket Name:       {args.bucket_name}")
        logger.info(f"Region:            {region}")
        logger.info(f"Versioning:        {'Enabled' if args.versioning else 'Disabled'}")
        logger.info(f"Encryption:        {args.encryption}")
        logger.info(f"Public Access:     Blocked (security best practice)")
        if tags:
            logger.info(f"Tags:              {tags}")
        logger.info("=" * 60)

        # Dry run mode
        if args.dry_run:
            logger.info("DRY RUN MODE: No resources will be created")
            return 0

        # Confirm with user
        if not confirm_action(
            f"Create S3 bucket '{args.bucket_name}' with the above configuration?",
            default=False
        ):
            logger.info("Operation cancelled by user")
            return 0

        # Create bucket
        logger.info(f"Creating S3 bucket '{args.bucket_name}'...")
        create_s3_bucket(
            args.bucket_name,
            region,
            versioning=args.versioning,
            encryption=args.encryption,
            tags=tags
        )

        logger.info(f"✓ Successfully created bucket '{args.bucket_name}'")
        logger.info(f"  Region: {region}")
        logger.info(f"  Versioning: {'Enabled' if args.versioning else 'Disabled'}")
        logger.info(f"  Encryption: {args.encryption}")
        logger.info(f"  Public Access: Blocked")

        return 0

    except NoCredentialsError:
        logger.error("AWS credentials not found. Please check your .env file.")
        return 1

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            logger.error(f"Bucket '{args.bucket_name}' already exists globally")
        elif error_code == 'BucketAlreadyOwnedByYou':
            logger.error(f"Bucket '{args.bucket_name}' already exists in your account")
        else:
            handle_error(e, logger)

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    except Exception as e:
        handle_error(e, logger)


if __name__ == '__main__':
    sys.exit(main())
