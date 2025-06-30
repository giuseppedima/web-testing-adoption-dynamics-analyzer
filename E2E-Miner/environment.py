import os
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parent / 'resources' / '.env'

if not env_file.exists():
    raise Exception('env files do not exist')

load_dotenv(env_file)

DB_URL = os.environ.get('DB_URL')
if not DB_URL:
    raise Exception('DB_URL is not set in the .env file')

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise Exception('GITHUB_TOKEN is not set in the .env file')

PATH_TO_ISSUES_DOWNLOAD = os.environ.get('PATH_TO_ISSUES_DOWNLOAD')
if not PATH_TO_ISSUES_DOWNLOAD:
    raise Exception('PATH_TO_ISSUES_DOWNLOAD is not set in the .env file')

PATH_TO_CLONE= os.environ.get('PATH_TO_CLONE')
if not PATH_TO_CLONE:
    raise Exception('PATH_TO_CLONE is not set in the .env file')