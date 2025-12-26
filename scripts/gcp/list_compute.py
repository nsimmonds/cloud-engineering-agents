#!/usr/bin/env python3
"""
List Compute Engine instances in a GCP project.

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

from google.cloud import compute_v1
from google.auth.exceptions import DefaultCredentialsError

from common import setup_logger, load_config, get_gcp_config, format_output, handle_error


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List Compute Engine instances in GCP project',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--project',
        help='GCP project ID (defaults to GCP_PROJECT_ID from .env)',
        default=None
    )

    parser.add_argument(
        '--zone',
        help='Filter by zone (e.g., us-central1-a). If not specified, lists from all zones',
        default=None
    )

    parser.add_argument(
        '--status',
        help='Filter by instance status (RUNNING, STOPPED, TERMINATED)',
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


def list_compute_instances(project_id, zone=None, status_filter=None):
    """
    List Compute Engine instances in the specified project.

    Args:
        project_id: GCP project ID
        zone: Optional zone filter
        status_filter: Optional status filter (RUNNING, STOPPED, etc.)

    Returns:
        List of instance dictionaries
    """
    instances_client = compute_v1.InstancesClient()

    instances = []

    if zone:
        # List instances in specific zone
        request = compute_v1.ListInstancesRequest(
            project=project_id,
            zone=zone
        )
        instance_list = instances_client.list(request=request)

        for instance in instance_list:
            if status_filter and instance.status != status_filter:
                continue

            instances.append(format_instance(instance, zone))

    else:
        # List instances across all zones
        zones_client = compute_v1.ZonesClient()
        zones_request = compute_v1.ListZonesRequest(project=project_id)

        for zone_obj in zones_client.list(request=zones_request):
            zone_name = zone_obj.name
            request = compute_v1.ListInstancesRequest(
                project=project_id,
                zone=zone_name
            )

            try:
                instance_list = instances_client.list(request=request)
                for instance in instance_list:
                    if status_filter and instance.status != status_filter:
                        continue

                    instances.append(format_instance(instance, zone_name))
            except Exception:
                # Skip zones that may not be available
                continue

    return instances


def format_instance(instance, zone):
    """Format instance information into dictionary."""
    # Get internal IP
    internal_ip = 'N/A'
    if instance.network_interfaces:
        internal_ip = instance.network_interfaces[0].network_i_p

    # Get external IP
    external_ip = 'N/A'
    if instance.network_interfaces and instance.network_interfaces[0].access_configs:
        external_ip = instance.network_interfaces[0].access_configs[0].nat_i_p or 'N/A'

    return {
        'Name': instance.name,
        'Zone': zone,
        'MachineType': instance.machine_type.split('/')[-1],
        'Status': instance.status,
        'InternalIP': internal_ip,
        'ExternalIP': external_ip,
    }


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
        logger.info(f"Using GCP project: {project_id}")

        # List instances
        logger.info("Fetching Compute Engine instances...")
        instances = list_compute_instances(project_id, args.zone, args.status)

        if not instances:
            logger.info(f"No Compute Engine instances found in project {project_id}")
            if args.zone:
                logger.info(f"  (filtered by zone: {args.zone})")
            if args.status:
                logger.info(f"  (filtered by status: {args.status})")
            return 0

        # Output results
        logger.info(f"Found {len(instances)} instance(s)")
        print(format_output(instances, args.format))

        return 0

    except DefaultCredentialsError:
        logger.error(
            "GCP credentials not found. Please check GOOGLE_APPLICATION_CREDENTIALS in .env file."
        )
        return 1

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    except Exception as e:
        handle_error(e, logger)


if __name__ == '__main__':
    sys.exit(main())
