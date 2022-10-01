"""Accessing the secrets"""
import google_crc32c
import os
# Import the Secret Manager client library.
from google.cloud import secretmanager

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()


def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

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
    # return the secret
    return payload


"""Configurations"""
#api_version_number = os.environ.get('API_VERSION_NUMBER')  # The version of current API
project_id = os.environ.get('SECRET_PROJECT_ID')  # the project ID for the APP secrets
database_name = os.environ.get('DATABASE_NAME')  # get the database name

"""Secrete IDs and its Secrete version"""
# get secrets name
secret_id_jwt, ver_secret_id_jwt = os.environ.get('JWT_SECRET_KEY'), os.environ.get('VERSION_JWT_SECRET_KEY')
secret_id_database_connection, ver_secret_id_database_connection = os.environ.get('DATABASE_CONNECTION'), os.environ.get('VERSION_DATABASE_CONNECTION')

# user id & password
secret_id_db_user_name,ver_secret_id_db_user_name = os.environ.get('MONGO_USERNAME'), os.environ.get('VERSION_MONGO_USERNAME')
secret_id_db_user_password,ver_secret_id_db_user_password = os.environ.get('MONGO_PASSWORD'), os.environ.get('VERSION_MONGO_PASSWORD')

# X509
secret_id_X509_certification,ver_secret_id_X509_certification = os.environ.get('X509_CERTIFICATION'),os.environ.get('VERSION_X509_CERTIFICATION')  # get the X509 secret id
secret_id_authSource,ver_secret_id_authSource = os.environ.get('AUTH_SOURCE'),os.environ.get('VERSION_AUTH_SOURCE')

# use the management tools to determine version at runtime, first version is 1
#version = 1

# load the secrets
JWT_SECRET_KEY = access_secret_version(project_id, secret_id_jwt, ver_secret_id_jwt)
DATABASE = access_secret_version(project_id, secret_id_database_connection, ver_secret_id_database_connection)

print(f", SECRET_PROJECT_ID is:{project_id}"
      f", DATABASE_CONNECTION is : {DATABASE}"
      f", authentication:{'X509' if secret_id_X509_certification else 'User ID & Password'}")

# if using X509 authentication method
if secret_id_X509_certification:
    # print("Authentication method: X509")
    X509_CERTIFICATE = access_secret_version(project_id, secret_id_X509_certification, ver_secret_id_X509_certification)

    """write X509_CERTIFICATE to file:"""
    save_path = "/tmp"  # tmp for GAE RAM
    file_name = "temp.pem"
    completeName = os.path.join(save_path, file_name)
    file = open(completeName, "w")
    file.write(X509_CERTIFICATE)
    file.close()
    """write end"""

    AUTH_SOURCE = access_secret_version(project_id, secret_id_authSource, ver_secret_id_authSource)
    MONGODB_SETTINGS = {
        "host": f"mongodb+srv://{DATABASE}/{database_name}?authSource={AUTH_SOURCE}&authMechanism={'MONGODB-X509'}&retryWrites=true&w=majority&tls=true&tlsCertificateKeyFile={'/tmp/temp.pem'}"}
    print(MONGODB_SETTINGS)
else:
    # print("Authentication method: username & password")
    USERNAME = access_secret_version(project_id, secret_id_db_user_name, ver_secret_id_db_user_name)
    PASSWORD = access_secret_version(project_id, secret_id_db_user_password, ver_secret_id_db_user_password)
    MONGODB_SETTINGS = {
        "host": f"mongodb+srv://{USERNAME}:{PASSWORD}@{DATABASE}/{database_name}?retryWrites=true&w=majority"}
