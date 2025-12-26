#!/usr/bin/env python3
"""
List Virtual Machines in an Azure subscription.

This script demonstrates infrastructure inspection following best practices:
- Uses credentials from .env file
- Supports command-line arguments
- Provides multiple output formats
- Includes proper error handling
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import AzureError

from common import setup_logger, load_config, get_azure_config, format_output, handle_error


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List Virtual Machines in Azure subscription',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--subscription',
        help='Azure subscription ID (defaults to AZURE_SUBSCRIPTION_ID from .env)',
        default=None
    )

    parser.add_argument(
        '--resource-group',
        help='Filter by resource group',
        default=None
    )

    parser.add_argument(
        '--status',
        help='Filter by power state (running, stopped, deallocated)',
        default=None
    )

    parser.add_argument(
        '--format',
        choices=['json', 'table', 'text'],
        default='table',
        help='Output format (default: table)'
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


def list_virtual_machines(subscription_id, credential, resource_group=None, status_filter=None):
    """
    List Virtual Machines in the specified subscription.

    Args:
        subscription_id: Azure subscription ID
        credential: Azure credential object
        resource_group: Optional resource group filter
        status_filter: Optional power state filter

    Returns:
        List of VM dictionaries
    """
    compute_client = ComputeManagementClient(credential, subscription_id)

    vms = []

    if resource_group:
        # List VMs in specific resource group
        vm_list = compute_client.virtual_machines.list(resource_group)
    else:
        # List all VMs in subscription
        vm_list = compute_client.virtual_machines.list_all()

    for vm in vm_list:
        # Get instance view for power state
        instance_view = compute_client.virtual_machines.instance_view(
            vm.id.split('/')[4],  # resource group name
            vm.name
        )

        # Extract power state
        power_state = 'unknown'
        for status in instance_view.statuses:
            if status.code.startswith('PowerState/'):
                power_state = status.code.split('/')[-1]
                break

        # Apply status filter if specified
        if status_filter and power_state.lower() != status_filter.lower():
            continue

        # Extract VM information
        vms.append({
            'Name': vm.name,
            'ResourceGroup': vm.id.split('/')[4],
            'Location': vm.location,
            'VMSize': vm.hardware_profile.vm_size,
            'PowerState': power_state,
            'OSType': vm.storage_profile.os_disk.os_type.name if vm.storage_profile.os_disk else 'N/A',
        })

    return vms


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
        azure_config = get_azure_config()

        # Use subscription from args or config
        subscription_id = args.subscription or azure_config['subscription_id']
        logger.info(f"Using Azure subscription: {subscription_id}")

        # Get credential
        credential = get_azure_credential(azure_config)

        # List VMs
        logger.info("Fetching Virtual Machines...")
        vms = list_virtual_machines(
            subscription_id,
            credential,
            args.resource_group,
            args.status
        )

        if not vms:
            logger.info(f"No Virtual Machines found in subscription")
            if args.resource_group:
                logger.info(f"  (filtered by resource group: {args.resource_group})")
            if args.status:
                logger.info(f"  (filtered by status: {args.status})")
            return 0

        # Output results
        logger.info(f"Found {len(vms)} VM(s)")
        print(format_output(vms, args.format))

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
