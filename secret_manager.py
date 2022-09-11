"""Accessing the secretes"""

# Import the Secret Manager client library.
from google.cloud import secretmanager
import google_crc32c

# GCP project in which to store secrets in Secret Manager.
project_id = "lucky-reactor-359516"

# ID of the secret to create.
secret_id_db_user_name = "PAM_MONGO_USERNAME"
secret_id_db_user_password = "PAM_MONGO_PASSWORD"
secret_id_jwt = "PAM_JWT_SECRET_KEY"

# use the management tools to determine version at runtime, first version is 1
version = 1

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()


def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response
    payload = response.payload.data.decode("UTF-8")
    # return the secrete
    return payload


USERNAME = access_secret_version(project_id, secret_id_db_user_name, version)
PASSWORD = access_secret_version(project_id, secret_id_db_user_password, version)
JWT_SECRET_KEY = access_secret_version(project_id, secret_id_jwt, version)
MONGODB_SETTINGS = {"host": f"mongodb+srv://{USERNAME}:{PASSWORD}@pam.nhzb5tp.mongodb.net/PAM-Database?retryWrites=true&w=majority"}
