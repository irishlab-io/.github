from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path=".emv")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("ORG_NAME")
