#!/usr/bin/env python3
"""
List EC2 instances in an AWS account.

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

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from common import setup_logger, load_config, get_aws_config, format_output, handle_error


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List EC2 instances in AWS account',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--region',
        help='AWS region (defaults to AWS_DEFAULT_REGION from .env)',
        default=None
    )

    parser.add_argument(
        '--state',
        help='Filter by instance state (running, stopped, terminated, etc.)',
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


def list_ec2_instances(region, state_filter=None):
    """
    List EC2 instances in the specified region.

    Args:
        region: AWS region name
        state_filter: Optional state filter (running, stopped, etc.)

    Returns:
        List of instance dictionaries
    """
    ec2 = boto3.client('ec2', region_name=region)

    filters = []
    if state_filter:
        filters.append({'Name': 'instance-state-name', 'Values': [state_filter]})

    response = ec2.describe_instances(Filters=filters) if filters else ec2.describe_instances()

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Extract relevant information
            name_tag = next(
                (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                'N/A'
            )

            instances.append({
                'InstanceId': instance['InstanceId'],
                'Name': name_tag,
                'Type': instance['InstanceType'],
                'State': instance['State']['Name'],
                'PrivateIP': instance.get('PrivateIpAddress', 'N/A'),
                'PublicIP': instance.get('PublicIpAddress', 'N/A'),
                'LaunchTime': instance['LaunchTime'].isoformat(),
            })

    return instances


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
        logger.info(f"Using AWS region: {region}")

        # List instances
        logger.info("Fetching EC2 instances...")
        instances = list_ec2_instances(region, args.state)

        if not instances:
            logger.info(f"No EC2 instances found in {region}")
            if args.state:
                logger.info(f"  (filtered by state: {args.state})")
            return 0

        # Output results
        logger.info(f"Found {len(instances)} instance(s)")
        print(format_output(instances, args.format))

        return 0

    except NoCredentialsError:
        logger.error("AWS credentials not found. Please check your .env file.")
        return 1

    except ClientError as e:
        handle_error(e, logger)

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    except Exception as e:
        handle_error(e, logger)


if __name__ == '__main__':
    sys.exit(main())
