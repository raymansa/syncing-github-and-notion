import os
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

def get_secret(secret_id: str, project_id: str = None) -> str:
    """
    Retrieves a secret from Google Secret Manager or a local .env file.
    """
    # Check for local environment variable first
    local_secret = os.getenv(secret_id)
    if local_secret:
        print(f"Loaded secret '{secret_id}' from local .env file.")
        return local_secret

    if not project_id:
        raise ValueError("GCP Project ID is required when running in a non-local environment.")

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        print(f"Loaded secret '{secret_id}' from Google Secret Manager.")
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Could not retrieve secret '{secret_id}'. Error: {e}")
        raise
