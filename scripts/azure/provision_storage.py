#!/usr/bin/env python3
"""
Provision an Azure Storage Account with best practices configuration.

This script demonstrates resource provisioning following best practices:
- Uses credentials from .env file
- Requires user confirmation before creating resources
- Supports command-line arguments for flexibility
- Includes proper error handling
- Implements security best practices (encryption, secure transfer)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind,
    MinimumTlsVersion
)
from azure.core.exceptions import AzureError

from common import (
    setup_logger,
    load_config,
    get_azure_config,
    confirm_action,
    parse_tags,
    handle_error
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Provision an Azure Storage Account with security best practices',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'storage_account_name',
        help='Name of the storage account (3-24 lowercase alphanumeric characters)'
    )

    parser.add_argument(
        'resource_group',
        help='Name of the resource group'
    )

    parser.add_argument(
        '--subscription',
        help='Azure subscription ID (defaults to AZURE_SUBSCRIPTION_ID from .env)',
        default=None
    )

    parser.add_argument(
        '--location',
        help='Azure location (defaults to AZURE_LOCATION from .env or eastus)',
        default=None
    )

    parser.add_argument(
        '--sku',
        choices=['Standard_LRS', 'Standard_GRS', 'Standard_RAGRS', 'Standard_ZRS', 'Premium_LRS'],
        default='Standard_LRS',
        help='Storage account SKU (default: Standard_LRS)'
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


def get_azure_credential(azure_config):
    """Get Azure credential from configuration."""
    return ClientSecretCredential(
        tenant_id=azure_config['tenant_id'],
        client_id=azure_config['client_id'],
        client_secret=azure_config['client_secret']
    )


def create_storage_account(subscription_id, credential, storage_account_name,
                           resource_group, location, sku_name, tags=None):
    """
    Create an Azure Storage Account with security best practices.

    Args:
        subscription_id: Azure subscription ID
        credential: Azure credential object
        storage_account_name: Name of the storage account
        resource_group: Resource group name
        location: Azure location
        sku_name: SKU name
        tags: Dictionary of tags to apply

    Returns:
        Created storage account object
    """
    storage_client = StorageManagementClient(credential, subscription_id)

    # Create storage account parameters
    params = StorageAccountCreateParameters(
        sku=Sku(name=sku_name),
        kind=Kind.STORAGE_V2,
        location=location,
        tags=tags or {},
        enable_https_traffic_only=True,  # Security best practice
        minimum_tls_version=MinimumTlsVersion.TLS1_2,  # Security best practice
        allow_blob_public_access=False,  # Security best practice
    )

    # Create storage account (this is a long-running operation)
    poller = storage_client.storage_accounts.begin_create(
        resource_group,
        storage_account_name,
        params
    )

    # Wait for completion
    storage_account = poller.result()

    return storage_account


def main():
    """Main execution function."""
    args = parse_arguments()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(__name__, level=log_level)

    try:
        # Validate storage account name
        if not (3 <= len(args.storage_account_name) <= 24):
            logger.error("Storage account name must be 3-24 characters")
            return 1

        if not args.storage_account_name.islower() or not args.storage_account_name.isalnum():
            logger.error("Storage account name must be lowercase alphanumeric")
            return 1

        # Load configuration
        logger.info("Loading configuration from .env file...")
        load_config()
        azure_config = get_azure_config()

        # Use subscription and location from args or config
        subscription_id = args.subscription or azure_config['subscription_id']
        location = args.location or azure_config.get('location', 'eastus')

        # Get credential
        credential = get_azure_credential(azure_config)

        # Parse tags
        tags = parse_tags(args.tags)

        # Display what will be created
        logger.info("=" * 60)
        logger.info("Azure Storage Account Configuration")
        logger.info("=" * 60)
        logger.info(f"Account Name:          {args.storage_account_name}")
        logger.info(f"Resource Group:        {args.resource_group}")
        logger.info(f"Subscription:          {subscription_id}")
        logger.info(f"Location:              {location}")
        logger.info(f"SKU:                   {args.sku}")
        logger.info(f"HTTPS Only:            Enabled (security best practice)")
        logger.info(f"Minimum TLS:           1.2 (security best practice)")
        logger.info(f"Public Blob Access:    Disabled (security best practice)")
        if tags:
            logger.info(f"Tags:                  {tags}")
        logger.info("=" * 60)

        # Dry run mode
        if args.dry_run:
            logger.info("DRY RUN MODE: No resources will be created")
            return 0

        # Confirm with user
        if not confirm_action(
            f"Create storage account '{args.storage_account_name}' with the above configuration?",
            default=False
        ):
            logger.info("Operation cancelled by user")
            return 0

        # Create storage account
        logger.info(f"Creating storage account '{args.storage_account_name}'...")
        logger.info("This may take a few minutes...")

        storage_account = create_storage_account(
            subscription_id,
            credential,
            args.storage_account_name,
            args.resource_group,
            location,
            args.sku,
            tags
        )

        logger.info(f"✓ Successfully created storage account '{storage_account.name}'")
        logger.info(f"  Resource Group: {args.resource_group}")
        logger.info(f"  Location: {location}")
        logger.info(f"  SKU: {args.sku}")
        logger.info(f"  HTTPS Only: Enabled")
        logger.info(f"  Minimum TLS: 1.2")
        logger.info(f"  Public Blob Access: Disabled")

        return 0

    except AzureError as e:
        logger.error(f"Azure API Error: {str(e)}")
        return 1

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    except Exception as e:
        handle_error(e, logger)


if __name__ == '__main__':
    sys.exit(main())
