# Setup Google App Engine
Follow the steps to deploy your GAE


# Part1: Prerequisite
## 1. Creating a project
You will need to set up a project first. 
> 1. Go to the [Manage resources page](https://console.cloud.google.com/cloud-resource-manager?walkthrough_id=resource-manager--create-project&_ga=2.219046815.768635686.1661177913-1193766713.1651689019)
> 2. On the Select organization drop-down list at the top of the page, select the organization resource in which you want to create a project. If you are a free trial user, skip this step, as this list does not appear.
> 3. Click **Create Project**.
> 4. In the **New Project** window that appears, enter a project name and select a billing account as applicable. A project name can contain only letters, numbers, single quotes, hyphens, spaces, or exclamation points, and must be between 4 and 30 characters.
> 5. Enter the parent organization or folder resource in the Location box. That resource will be the hierarchical parent of the new project. If **No organization** is an option, you can select it to create your new project as the top level of its own resource hierarchy.
> 6. When you're finished entering new project details, click **Create**.


## 2. Check if billing is enabled on a project.
Typically, projects are linked to a billing account at the time that you create the project. You can skip it if no issue is encountered with billing

>Go to the [Verify the billing status page](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled) and follow the steps to check your billing status

## 3. Enable APIs
> 1. Go to [enable Cloud Build API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com&_ga=2.117968143.768635686.1661177913-1193766713.1651689019) page, click on **Next**, then click on **ENABLE**
> 2. Go to [enable Secret Manager API](https://console.cloud.google.com/flows/enableapi?apiid=secretmanager.googleapis.com&redirect=https://console.cloud.google.com&_ga=2.10889010.768635686.1661177913-1193766713.1651689019) page, click on **Next**, then click on **ENABLE**

## 4. Install and initialize the gcloud CLI
> 1. Download [Google Cloud CLI installer](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe), and finish the installation steps.
> 2. Open the Google Cloud SDK shell and input:\
>   ``` gcloud init ```
> 3. The terminal will automatically open a page in the browser for you to log in your google cloud account. Click on **Allow** to grant permissions to access google cloud resources.
> 4. Now you will need to select the project you just created:
> ![image 1](./GAE_resources/1.png)
> 5. Initialize your App Engine app:\
> ```gcloud app create --project=[YOUR_PROJECT_ID]```
> 6. Select the region:\
> Here I select us-central(17)
> ![image 2](./GAE_resources/2.png)
> 7. Run the following command to install the gcloud component that includes the App Engine extension for Python 3:\
> ```gcloud components install app-engine-python```


## 5. Set IAM




# Part 2: Configure Secret
Make sure you enable the **Secret Manager API** before proceeding.

## How to create secrets
> 1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?_ga=2.55652141.768635686.1661177913-1193766713.1651689019)
> 2. Click on **Create secret**
> - Under Name, enter your secret name
> - Copy the **mongodb user name** and put it in the **Secret value**
> 3. Click the **Create secret** button to finish.
> 4. Repeat the same process for:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
a. **mongodb user password Secret**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
b. **JWT Secret**\
It will looks like:
![image 4](./GAE_resources/4.png)




## How to access the secrets (In Python app)
```python 
"""In ./PAM/secrete_manager file"""
#define a function for retrieve secrete
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

    # return the secrete
    payload = response.payload.data.decode("UTF-8")
    return payload

# GCP project in which to store secrets in Secret Manager.
project_id = "lucky-reactor-359516"
# ID of the secret to create.
#secret_id = "YOUR_SECRET_ID"
secret_id_db_user_name = "PAM_MONGO_PASSWORD"
secret_id_db_user_password = "PAM_MONGO_USERNAME"
secret_id_jwt = "PAM_JWT_SECRET_KEY"
# use the management tools to determine version at runtime, first version is 1
version_id = 1

#....


 ```





















# Part 3: Deployment (Single time)
1. Make sure you have the git Installed
2. app.yaml file in the PAM (if .yaml file is not named "app", then need to specify when run deployment)
3. Local environment: windows

## 1. Clone/Pull the repo
> open the git bash, in the terminal clone the repo to local directory(or pull the newest version):\
> ```git clone https://github.com/dataperformance/PAM.git```
## 2. Deploy
> In the same directory, run command``` gcloud app deploy```
> ![image 5](./GAE_resources/5.png)
> Useful information for managing the service:\
> [Service Page](https://console.cloud.google.com/appengine/services?_ga=2.9325619.768635686.1661177913-1193766713.1651689019)\
> [App settings](https://console.cloud.google.com/appengine/settings?_ga=2.215425169.768635686.1661177913-1193766713.1651689019)


# Part 4: Deployment (continuous)

## 1. Create and Add the **cloud build configuration** file
> cloudbuild.yaml
```yaml
steps:
- name: "gcr.io/cloud-builders/gcloud"
  args: ["app", "deploy"]
timeout: "1600s"

options:
  logging: CLOUD_LOGGING_ONLY

```
## 2. Enable API
[Identity and Access Management (IAM) API](https://console.cloud.google.com/apis/library/iam.googleapis.com)

## 3. Fork the PAM repo to your Github account 

## 4. Build a trigger
>1. Go to [trigger page](https://console.cloud.google.com/cloud-build/triggers?_ga=2.9390899.768635686.1661177913-1193766713.1651689019)
>2. Click on **Create Trigger**
>3. Define a **Name** for the trigger
>4. Select a Region for the trigger
>5. Define an **EVENT** that invokes the trigger
>6. Select the **Repository** for the forked PAM repo
>7. put ```.*``` in the **Branch** (any branch)
>8. For the Configuration type, select **Autodetected**
>9. Leave the **service account blank**, it will use the default Cloud Build service account
>It will look like:\
>![image 7](./GAE_resources/7.png)\
>![image 9](./GAE_resources/9.png)
>
>9. Click on **Create**
>10. Click on **Run** to test the trigger\
>![image 8](./GAE_resources/11.png)
>11. Select **Dev** branch and click on **Run trigger**
>![image 10](./GAE_resources/10.png)


## 5. Monitor Build history
>1. Go to [trigger page](https://console.cloud.google.com/cloud-build/triggers?_ga=2.9390899.768635686.1661177913-1193766713.1651689019)
>2. Click on **History**
>3. You can find the build history there