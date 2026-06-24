import os
import boto3
from botocore.config import Config
from app.core.configuracion import config

for key in list(os.environ.keys()):
    if key.startswith("AWS_") or "PROXY" in key.upper():
        os.environ.pop(key, None)

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

print(f"Connecting to DynamoDB Local at {config.DYNAMODB_ENDPOINT}...")

session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION
)

dynamodb = session.resource(
    'dynamodb',
    endpoint_url=config.DYNAMODB_ENDPOINT,
    config=Config(signature_version='v4')
)

tabla_smartstop = dynamodb.Table(config.DYNAMODB_TABLA)  # type: ignore[attr-defined]