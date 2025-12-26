# Cloud Engineering Scripts

This directory contains reusable, production-ready scripts for managing multi-cloud infrastructure following the script philosophy defined in [bootstrap.md](../bootstrap.md).

## Directory Structure

```
scripts/
├── common/              # Shared utilities for all scripts
│   ├── config.py       # Environment variable loading and configuration
│   ├── logger.py       # Logging utilities
│   └── utils.py        # Common helper functions
├── aws/                # AWS-specific scripts
│   ├── list_ec2.py     # List EC2 instances (inspection)
│   └── provision_s3.py # Provision S3 bucket (provisioning)
├── gcp/                # GCP-specific scripts
│   ├── list_compute.py       # List Compute Engine instances
│   └── provision_bucket.py   # Provision Cloud Storage bucket
├── azure/              # Azure-specific scripts
│   ├── list_vms.py           # List Virtual Machines
│   └── provision_storage.py  # Provision Storage Account
└── admin/              # Administrative tool scripts
    └── (future Jira scripts, etc.)
```

## Script Philosophy

All scripts in this directory follow these principles:

1. **Reusable and Maintainable**: Scripts are designed for team use, not one-off execution
2. **Environment-Based Configuration**: Credentials and settings from `.env` file
3. **Proper Error Handling**: Comprehensive error messages and exit codes
4. **Command-Line Arguments**: Flexible parameters instead of hardcoded values
5. **User Confirmation**: Interactive prompts before making changes
6. **Security-First**: Best practices for encryption, access control, and credentials

## Prerequisites

### Python Dependencies

Install required packages:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install boto3 google-cloud-compute google-cloud-storage azure-identity azure-mgmt-compute azure-mgmt-storage
```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Fill in your credentials in `.env`:
   - AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
   - GCP: `GOOGLE_APPLICATION_CREDENTIALS`, `GCP_PROJECT_ID`, `GCP_REGION`
   - Azure: `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`

## Usage Examples

### AWS Scripts

#### List EC2 Instances

```bash
# List all instances in default region (table format)
python scripts/aws/list_ec2.py

# List running instances in specific region (JSON format)
python scripts/aws/list_ec2.py --region us-west-2 --state running --format json

# Verbose output
python scripts/aws/list_ec2.py --verbose
```

#### Provision S3 Bucket

```bash
# Dry run - see what would be created
python scripts/aws/provision_s3.py my-bucket-name --dry-run

# Create bucket with versioning and encryption
python scripts/aws/provision_s3.py my-bucket-name \
  --region us-east-1 \
  --versioning \
  --encryption AES256 \
  --tags environment=prod team=engineering

# Interactive mode will prompt for confirmation before creating
```

### GCP Scripts

#### List Compute Engine Instances

```bash
# List all instances across all zones
python scripts/gcp/list_compute.py

# List running instances in specific zone
python scripts/gcp/list_compute.py --zone us-central1-a --status RUNNING

# JSON output
python scripts/gcp/list_compute.py --format json
```

#### Provision Cloud Storage Bucket

```bash
# Dry run
python scripts/gcp/provision_bucket.py my-bucket-name --dry-run

# Create bucket with configuration
python scripts/gcp/provision_bucket.py my-bucket-name \
  --location US \
  --storage-class STANDARD \
  --versioning \
  --labels environment=prod team=engineering
```

### Azure Scripts

#### List Virtual Machines

```bash
# List all VMs in subscription
python scripts/azure/list_vms.py

# List VMs in specific resource group
python scripts/azure/list_vms.py --resource-group my-rg

# List only running VMs (table format)
python scripts/azure/list_vms.py --status running --format table
```

#### Provision Storage Account

```bash
# Dry run
python scripts/azure/provision_storage.py mystorageacct my-resource-group --dry-run

# Create storage account
python scripts/azure/provision_storage.py mystorageacct my-resource-group \
  --location eastus \
  --sku Standard_LRS \
  --tags environment=prod team=engineering

# Note: Storage account names must be 3-24 lowercase alphanumeric characters
```

## Common Options

Most scripts support these common flags:

- `--verbose`: Enable detailed logging
- `--format json|table|text`: Choose output format (inspection scripts)
- `--dry-run`: Preview changes without executing (provisioning scripts)
- `--help`: Show detailed usage information

## Script Development Guidelines

When creating new scripts, follow these patterns:

### 1. File Structure

```python
#!/usr/bin/env python3
"""
Script description.

Detailed explanation of what the script does.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common import setup_logger, load_config, ...

def parse_arguments():
    """Parse command-line arguments."""
    # ... argument parsing

def main():
    """Main execution function."""
    # ... main logic
    return 0  # Exit code

if __name__ == '__main__':
    sys.exit(main())
```

### 2. Use Common Utilities

```python
from common import (
    setup_logger,      # Consistent logging
    load_config,       # Load .env file
    get_aws_config,    # Get AWS credentials
    confirm_action,    # User confirmation prompts
    format_output,     # Format data for display
    handle_error,      # Error handling
)

# Setup logger
logger = setup_logger(__name__, level='INFO')

# Load credentials
load_config()
aws_config = get_aws_config()

# Confirm before changes
if confirm_action("Create this resource?", default=False):
    # ... proceed
```

### 3. Command-Line Arguments

Always support flexible configuration via arguments:

```python
parser.add_argument('resource_name', help='Name of the resource')
parser.add_argument('--region', default=None, help='Override default region')
parser.add_argument('--dry-run', action='store_true', help='Preview only')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
```

### 4. Error Handling

Use try-except blocks and provide helpful error messages:

```python
try:
    # ... operations
    return 0
except ClientError as e:
    logger.error(f"AWS API Error: {e}")
    return 1
except Exception as e:
    handle_error(e, logger)
```

### 5. Security Best Practices

- Never hardcode credentials
- Load sensitive data from `.env`
- Never log credentials or secrets
- Implement secure defaults (encryption, private access, etc.)
- Require explicit confirmation for changes

### 6. User Confirmation

Always confirm before making changes:

```python
# Display what will be created
logger.info("=" * 60)
logger.info("Resource Configuration")
logger.info("=" * 60)
logger.info(f"Name: {name}")
logger.info(f"Type: {type}")
logger.info("=" * 60)

# Dry run support
if args.dry_run:
    logger.info("DRY RUN MODE: No changes will be made")
    return 0

# Confirm with user
if not confirm_action("Create this resource?", default=False):
    logger.info("Operation cancelled")
    return 0

# Proceed with creation
```

## Testing Scripts

Before committing new scripts:

1. **Test with --dry-run**: Ensure dry-run mode works correctly
2. **Test with invalid input**: Verify error handling
3. **Test without .env**: Ensure helpful error messages
4. **Test output formats**: Verify json, table, and text formats
5. **Document in this README**: Add usage examples

## Troubleshooting

### "No .env file found"

Create a `.env` file from the template:
```bash
cp .env.example .env
```
Then fill in your credentials.

### "Credentials not found"

Check that your `.env` file contains the required variables for the cloud provider:
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- GCP: `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON)
- Azure: `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`

### Import Errors

Ensure you're in the virtual environment and have installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

Verify your cloud credentials have the necessary permissions for the operations you're attempting.

## Contributing

When adding new scripts:

1. Follow the script philosophy and development guidelines above
2. Add appropriate error handling and logging
3. Support `--dry-run` for provisioning scripts
4. Support `--format` for inspection scripts
5. Update this README with usage examples
6. Test thoroughly before committing

## Future Enhancements

- Administrative tool scripts (Jira automation)
- Multi-cloud comparison scripts
- Cost analysis scripts
- Backup and restore scripts
- Monitoring and alerting integration
- CI/CD pipeline scripts

---

For questions or issues with scripts, refer to the main [README.md](../README.md) or open an issue.
