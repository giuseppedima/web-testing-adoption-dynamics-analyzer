"""
Configuration management for the E2E testing analysis project.
Loads environment variables and defines global paths.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent

# Path to resources folder
RESOURCES_DIR = ROOT_DIR / 'resources'

# Load environment variables from .env file
env_file = RESOURCES_DIR / '.env'

if not env_file.exists():
    raise Exception(f'Environment file does not exist: {env_file}')

load_dotenv(env_file)

# Database configuration
DB_URL = os.environ.get('DB_URL')
if not DB_URL:
    raise Exception('DB_URL is not set in the .env file')

# GitHub API configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise Exception('GITHUB_TOKEN is not set in the .env file')

# Paths configuration
PATH_TO_ISSUES_DOWNLOAD = os.environ.get('PATH_TO_ISSUES_DOWNLOAD')
if not PATH_TO_ISSUES_DOWNLOAD:
    raise Exception('PATH_TO_ISSUES_DOWNLOAD is not set in the .env file')

PATH_TO_CLONE = os.environ.get('PATH_TO_CLONE')
if not PATH_TO_CLONE:
    raise Exception('PATH_TO_CLONE is not set in the .env file')
