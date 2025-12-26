#!/usr/bin/env python3
"""
Provision a Cloud Storage bucket with best practices configuration.

This script demonstrates resource provisioning following best practices:
- Uses credentials from .env file
- Requires user confirmation before creating resources
- Supports command-line arguments for flexibility
- Includes proper error handling
- Implements security best practices (uniform access, encryption)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import Conflict, GoogleAPIError

from common import (
    setup_logger,
    load_config,
    get_gcp_config,
    confirm_action,
    parse_tags,
    handle_error
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Provision a Cloud Storage bucket with security best practices',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'bucket_name',
        help='Name of the Cloud Storage bucket to create'
    )

    parser.add_argument(
        '--project',
        help='GCP project ID (defaults to GCP_PROJECT_ID from .env)',
        default=None
    )

    parser.add_argument(
        '--location',
        help='Bucket location (e.g., US, EU, us-central1)',
        default='US'
    )

    parser.add_argument(
        '--storage-class',
        choices=['STANDARD', 'NEARLINE', 'COLDLINE', 'ARCHIVE'],
        default='STANDARD',
        help='Storage class (default: STANDARD)'
    )

    parser.add_argument(
        '--versioning',
        action='store_true',
        help='Enable versioning on the bucket'
    )

    parser.add_argument(
        '--labels',
        nargs='*',
        help='Labels to apply (format: key=value)',
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


def create_storage_bucket(bucket_name, project_id, location='US',
                          storage_class='STANDARD', versioning=False, labels=None):
    """
    Create a Cloud Storage bucket with security best practices.

    Args:
        bucket_name: Name of the bucket
        project_id: GCP project ID
        location: Bucket location
        storage_class: Storage class
        versioning: Enable versioning
        labels: Dictionary of labels to apply

    Returns:
        Created bucket object
    """
    storage_client = storage.Client(project=project_id)

    # Create bucket
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = storage_class

    # Enable uniform bucket-level access (security best practice)
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True

    # Create the bucket
    bucket = storage_client.create_bucket(
        bucket,
        location=location
    )

    # Enable versioning if requested
    if versioning:
        bucket.versioning_enabled = True
        bucket.patch()

    # Apply labels if provided
    if labels:
        bucket.labels = labels
        bucket.patch()

    return bucket


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
        gcp_config = get_gcp_config()

        # Use project from args or config
        project_id = args.project or gcp_config['project_id']

        # Parse labels
        labels = parse_tags(args.labels)

        # Display what will be created
        logger.info("=" * 60)
        logger.info("Cloud Storage Bucket Configuration")
        logger.info("=" * 60)
        logger.info(f"Bucket Name:           {args.bucket_name}")
        logger.info(f"Project:               {project_id}")
        logger.info(f"Location:              {args.location}")
        logger.info(f"Storage Class:         {args.storage_class}")
        logger.info(f"Versioning:            {'Enabled' if args.versioning else 'Disabled'}")
        logger.info(f"Uniform Access:        Enabled (security best practice)")
        if labels:
            logger.info(f"Labels:                {labels}")
        logger.info("=" * 60)

        # Dry run mode
        if args.dry_run:
            logger.info("DRY RUN MODE: No resources will be created")
            return 0

        # Confirm with user
        if not confirm_action(
            f"Create Cloud Storage bucket '{args.bucket_name}' with the above configuration?",
            default=False
        ):
            logger.info("Operation cancelled by user")
            return 0

        # Create bucket
        logger.info(f"Creating Cloud Storage bucket '{args.bucket_name}'...")
        bucket = create_storage_bucket(
            args.bucket_name,
            project_id,
            location=args.location,
            storage_class=args.storage_class,
            versioning=args.versioning,
            labels=labels
        )

        logger.info(f"✓ Successfully created bucket '{bucket.name}'")
        logger.info(f"  Project: {project_id}")
        logger.info(f"  Location: {args.location}")
        logger.info(f"  Storage Class: {args.storage_class}")
        logger.info(f"  Versioning: {'Enabled' if args.versioning else 'Disabled'}")
        logger.info(f"  Uniform Access: Enabled")

        return 0

    except DefaultCredentialsError:
        logger.error(
            "GCP credentials not found. Please check GOOGLE_APPLICATION_CREDENTIALS in .env file."
        )
        return 1

    except Conflict:
        logger.error(f"Bucket '{args.bucket_name}' already exists")
        return 1

    except GoogleAPIError as e:
        logger.error(f"GCP API Error: {str(e)}")
        return 1

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    except Exception as e:
        handle_error(e, logger)


if __name__ == '__main__':
    sys.exit(main())
