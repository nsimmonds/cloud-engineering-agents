"""
Configuration management for cloud engineering scripts.

Handles loading environment variables from .env file and providing
configuration values to scripts.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any


def find_env_file() -> Optional[Path]:
    """
    Find the .env file by searching up from current directory.

    Returns:
        Path to .env file if found, None otherwise
    """
    current = Path.cwd()

    # Search up to 5 levels
    for _ in range(5):
        env_path = current / '.env'
        if env_path.exists():
            return env_path

        if current == current.parent:
            break
        current = current.parent

    return None


def load_config() -> Dict[str, Any]:
    """
    Load configuration from .env file.

    Returns:
        Dictionary of configuration values

    Raises:
        FileNotFoundError: If .env file cannot be found
    """
    env_path = find_env_file()

    if env_path is None:
        raise FileNotFoundError(
            "No .env file found. Please create one from .env.example:\n"
            "  cp .env.example .env\n"
            "Then fill in your credentials."
        )

    config = {}

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                config[key] = value

                # Also set in os.environ for compatibility
                os.environ[key] = value

    return config


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable value.

    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raise error if not found

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required is True and variable not found
    """
    value = os.environ.get(key, default)

    if required and value is None:
        raise ValueError(
            f"Required environment variable '{key}' not found. "
            f"Please set it in your .env file."
        )

    return value


def get_aws_config() -> Dict[str, str]:
    """Get AWS-specific configuration."""
    return {
        'access_key_id': get_env('AWS_ACCESS_KEY_ID', required=True),
        'secret_access_key': get_env('AWS_SECRET_ACCESS_KEY', required=True),
        'region': get_env('AWS_DEFAULT_REGION', default='us-east-1'),
        'session_token': get_env('AWS_SESSION_TOKEN'),
    }


def get_gcp_config() -> Dict[str, str]:
    """Get GCP-specific configuration."""
    return {
        'credentials_path': get_env('GOOGLE_APPLICATION_CREDENTIALS', required=True),
        'project_id': get_env('GCP_PROJECT_ID', required=True),
        'region': get_env('GCP_REGION', default='us-central1'),
        'zone': get_env('GCP_ZONE', default='us-central1-a'),
    }


def get_azure_config() -> Dict[str, str]:
    """Get Azure-specific configuration."""
    return {
        'subscription_id': get_env('AZURE_SUBSCRIPTION_ID', required=True),
        'tenant_id': get_env('AZURE_TENANT_ID', required=True),
        'client_id': get_env('AZURE_CLIENT_ID', required=True),
        'client_secret': get_env('AZURE_CLIENT_SECRET', required=True),
        'location': get_env('AZURE_LOCATION', default='eastus'),
    }
