from os import getenv

S3_ENDPOINT = getenv("S3_ENDPOINT")
S3_REGION = getenv("S3_REGION")
S3_ACCESS_KEY_ID = getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = getenv("S3_SECRET_ACCESS_KEY")
S3_SESSION_TOKEN = getenv("S3_SESSION_TOKEN")
USE_SSL = getenv("USE_SSL", "true").lower() in ["true", "t", "y", "yes"]
