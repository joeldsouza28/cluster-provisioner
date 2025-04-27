import os
from backend.db.dao import GcpDao, AzureDao, TerraformLogDao
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from google.cloud import container_v1
from google.cloud import compute_v1
import time
import subprocess
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
import requests
from google.cloud import storage
from fastapi import HTTPException
from fastapi import status
from google.cloud import resourcemanager_v3

GCP_KEY_PATH = "/tmp/gcp_sa_key.json"  # Temporary storage for the key

task_running = {}


class TerraformUtils:
    def __init__(self, db):
        self.db = db

    async def get_log_id(self, provider, action, cluster_name, location):
        tf_dao = TerraformLogDao(db=self.db)
        tf_id = await tf_dao.create_log_file(
            provider=provider, action=action, cluster_name=cluster_name, location=location
        )
        return tf_id

    async def get_active_log_ids(self):
        tf_dao = TerraformLogDao(db=self.db)
        tf_data = await tf_dao.get_active_log_ids()
        return tf_data

    async def update_active_log_id(self, id):
        tf_dao = TerraformLogDao(db=self.db)
        await tf_dao.update_log_file(log_id=id, stream_status=True)


def run_kubernetes_terraform(data: dict):
    """Runs Terraform in the background."""
    global task_running
    tf_log_id = data.get("log_id")
    terraform_dir = data.get("terraform_dir")
    task_running[tf_log_id] = True

    with open(f"terraform_output_{tf_log_id}.log", "w") as log_file:
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file,
            stderr=log_file,
        )
    process.wait()
    task_running[tf_log_id] = False


def run_azure_terraform(data: dict):
    """Runs Terraform in the background."""
    global task_running
    tf_log_id = data.get("log_id")
    task_running[tf_log_id] = True

    with open(f"terraform_output_{tf_log_id}.log", "w") as log_file:
        terraform_dir = "./infra/azure"
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file,
            stderr=log_file,
        )
    process.wait()
    task_running[tf_log_id] = False


def log_streamer(log_id):
    """Generator function to yield log file contents in real-time."""
    file_path = f"terraform_output_{log_id}.log"
    with open(file_path, "r") as file:
        for line in file:
            yield line

        while task_running.get(log_id, False):
            line = file.readline()
            if not line:
                time.sleep(1)  # Wait for new logs
                continue
            yield line

    time.sleep(2)  # Wait a bit to ensure all logs are written
    yield "\n--- Final Terraform Output ---\n"
    with open(file_path, "r") as file:
        final_lines = file.readlines()[-10:]  # Read the last 10 lines from the log
        for line in final_lines:
            yield line


def is_terraform_initialized(path="."):
    return os.path.isdir(os.path.join(path, ".terraform"))


def configure_backend(backend_config, infra, bucket_name):
    config_file = f"./infra/{infra}/backend-{bucket_name}.config"
    with open(config_file, "w") as f:
        f.write(backend_config)

    process = subprocess.Popen(
        ["terraform", "init", f"-backend-config=backend-{bucket_name}.config", "-reconfigure"],
        cwd=f"./infra/{infra}",
    )
    process.wait()


class GCPUtils:
    def __init__(self, db):
        self.db = db

    async def set_gcp_remote_backend(self, bucket_name):
        gcp_dao = GcpDao(db=self.db)
        await gcp_dao.add_gcp_remote_bucket(bucket_name=bucket_name)

    async def create_gcp_bucket(self, bucket_name, location):
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        try:
            new_bucket = client.create_bucket(bucket, location=location)
        except Exception:
            raise HTTPException(
                detail="The request bucket name is not available",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def get_gcp_regions(self):
        client = compute_v1.RegionsClient()
        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_key()

        regions = client.list(project=gcp_keys["project_id"])
        regions_list = []
        for region in regions:
            regions_list.append(region.name)
        return regions_list

    async def get_gcp_zones(self):
        client = compute_v1.ZonesClient()
        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_key()

        zones = client.list(project=gcp_keys["project_id"])
        zones_list = []
        for zone in zones:
            zones_list.append(zone.name)
        return zones_list

    async def get_gcp_machine_types(self, region):
        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_key()

        machine_client = compute_v1.MachineTypesClient()
        zone_list = compute_v1.ZonesClient()

        zones = zone_list.list(project=gcp_keys["project_id"])
        zone_names = [zone.name for zone in zones if zone.name.startswith(region)]
        machine_types_set = set()
        for zone in zone_names:
            machine_types = machine_client.list(project=gcp_keys["project_id"], zone=zone)
            for machine in machine_types:
                machine_types_set.add(machine.name)

        return sorted(list(machine_types_set))

    async def get_remote_bucket(self, project_id):
        gcp_dao = GcpDao(db=self.db)
        bucket_data = await gcp_dao.get_gcp_remote_bucket(key_id=project_id)
        return bucket_data

    async def get_gcp_keys(self):
        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_keys()
        gcp_keys_list = []
        for gcp_key in gcp_keys:
            await self.set_gcp_env(id=gcp_key["project_id"])
            client = resourcemanager_v3.ProjectsClient()
            project_path = f"projects/{gcp_key['project_id']}"
            project = client.get_project(name=project_path)
            gcp_keys_list.append({
                **gcp_key,
                "display_name": project.display_name
            })
        return gcp_keys_list

    async def initialize_backend(self, bucket_name):
        backend_config = f"""bucket  = "{bucket_name}"
        prefix  = "terraform/state"
        """

        configure_backend(backend_config=backend_config, infra="gcp", bucket_name=bucket_name)

    async def set_gcp_env(self, id=None):
        gcp_dao = GcpDao(db=self.db)
        if id:
            gcp_keys = await gcp_dao.get_gcp_key_by_id(project_id=id)
        else:
            gcp_keys = await gcp_dao.get_gcp_key()

        if gcp_keys is not None:
            with open(GCP_KEY_PATH, "w", encoding="utf-8") as file:
                gcp_keys["token_uri"] = "https://oauth2.googleapis.com/token"
                gcp_keys["private_key"] = gcp_keys["private_key"].replace("\\n", "\n")
                json.dump(gcp_keys, file, ensure_ascii=False, indent=4)

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
            os.environ["TF_VAR_project_id"] = gcp_keys["project_id"]

        return gcp_keys

    def update_gcp_tfvars(self, cluster_data):
        TERRAFORM_DIR = "./infra/gcp"

        cluster_name: str = cluster_data.get("name")
        location: str = cluster_data.get("location")

        tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")
        os.environ["TF_VAR_region"] = location

        # Load existing Terraform variables
        if os.path.exists(tf_vars_path):
            with open(tf_vars_path, "r") as f:
                tf_vars = json.load(f)
        else:
            tf_vars = {"clusters": {}}

        # Add the new cluster
        tf_vars["clusters"][cluster_name] = cluster_data

        # Save updated variables
        with open(tf_vars_path, "w") as f:
            json.dump(tf_vars, f, indent=2)

    def delete_from_gcp_tfvars(self, cluster_name):
        TERRAFORM_DIR = "./infra/gcp"

        tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")

        # Load existing Terraform variables
        if os.path.exists(tf_vars_path):
            with open(tf_vars_path, "r") as f:
                tf_vars = json.load(f)
        else:
            return {"error": "No clusters found in Terraform configuration"}

        # Check if the cluster exists
        if cluster_name not in tf_vars["clusters"]:
            return {"error": f"Cluster '{cluster_name}' does not exist"}

        # Remove the cluster
        del tf_vars["clusters"][cluster_name]

        # Save updated variables
        with open(tf_vars_path, "w") as f:
            json.dump(tf_vars, f, indent=2)

    def list_gke_clusters(self, gcp_mapper):
        """Lists GKE clusters in a given project and region."""
        # parent = f"projects/{project_id}/locations/{region}"
        gke_cluster_status = {
            0: "Status Unspecified",
            1: "Provisioning",
            2: "Running",
            3: "Reconciling",
            4: "Stopping",
            5: "Error",
            6: "Degraded",
        }

        # container_v1
        try:
            client = container_v1.ClusterManagerClient()
            project_id = os.environ.get("TF_VAR_project_id")

            all_clusters = []

            response = client.list_clusters(parent=f"projects/{project_id}/locations/-")
            for cluster in response.clusters:
                all_clusters.append(
                    {
                        "name": cluster.name,
                        "location": cluster.location,
                        "status": gke_cluster_status[cluster.status],
                        "cloud": "GCP",
                        "key_id": project_id,
                        "display_name": gcp_mapper[project_id],
                    }
                )
            return all_clusters

        except Exception as ex:
            print(ex)
            return []

    async def get_project_name(self):
        keys = await self.get_gcp_keys()
        gcp_mapper = {}
        for key in keys:
            await self.set_gcp_env(id=key["project_id"])
            client = resourcemanager_v3.ProjectsClient()
            project_path = f"projects/{key['project_id']}"
            project = client.get_project(name=project_path)
            gcp_mapper[key["project_id"]] = project.display_name

        return gcp_mapper


class AzureUtil:
    def __init__(self, db):
        self.db = db

    async def set_azure_remote_backend(self, data):
        azure_dao = AzureDao(db=self.db)
        await azure_dao.add_azure_remote_bucket(data=data)

    async def get_azure_keys(self):
        azure_dao = AzureDao(db=self.db)
        azure_keys = await azure_dao.get_azure_keys()
        azure_key_list = []
        for azure_key in azure_keys:
            await self.set_azure_env(key_id=azure_key["subscription_id"])
            azure_mapper = self.get_subscriptions()
            azure_key_list.append(
                {**azure_key, "display_name": azure_mapper[azure_key["subscription_id"]]}
            )
        return azure_key_list

    async def get_azure_regions(self):
        credential = DefaultAzureCredential()
        SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")

        url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/locations?api-version=2016-06-01"

        token = credential.get_token("https://management.azure.com/.default").token
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.get(url, headers=headers)
        regions = []
        if response.status_code == 200:
            data = response.json()
            for region in data["value"]:
                regions.append(region["name"])

        return regions

    async def get_azure_machine_type(self, region):
        credential = DefaultAzureCredential()
        SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")

        token = credential.get_token("https://management.azure.com/.default").token

        url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/providers/Microsoft.Compute/locations/{region}/vmSizes?api-version=2024-07-01"

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        machine_types = []
        if response.status_code == 200:
            data = response.json()
            for size in data["value"]:
                machine_types.append(size["name"])

        return machine_types

    async def set_azure_env(self, key_id=None):
        azure_dao = AzureDao(db=self.db)
        if key_id is not None:
            azure_key = await azure_dao.get_azure_key_by_id(key_id=key_id)
        else:
            azure_key = await azure_dao.get_azure_key()
        if azure_key is not None:
            os.environ["TF_VAR_client_id"] = azure_key["client_id"]
            os.environ["TF_VAR_client_secret"] = azure_key["client_secret"]
            os.environ["TF_VAR_tenant_id"] = azure_key["tenant_id"]
            os.environ["AZURE_CLIENT_ID"] = azure_key["client_id"]
            os.environ["AZURE_TENANT_ID"] = azure_key["tenant_id"]
            os.environ["AZURE_CLIENT_SECRET"] = azure_key["client_secret"]

            os.environ["ARM_CLIENT_ID"] = azure_key["client_id"]
            os.environ["ARM_CLIENT_SECRET"] = azure_key["client_secret"]
            os.environ["ARM_SUBSCRIPTION_ID"] = azure_key["subscription_id"]
            os.environ["ARM_TENANT_ID"] = azure_key["tenant_id"]
            os.environ["TF_VAR_subscription_id"] = azure_key["subscription_id"]

        return azure_key

        # azure_bucket_data = await azure_dao.get_azure_remote_bucket()

        # backend_config = f"""
        # resource_group_name  = "{azure_bucket_data.resource_group_name}"
        # storage_account_name  = "{azure_bucket_data.storage_account_name}"
        # container_name = "{azure_bucket_data.container_name}"
        # key = "{azure_bucket_data.key}"
        # """

        # backend_config = "./infra/azure/backend.config"

        # configure_backend(backend_config=backend_config, infra="azure")

    def update_azure_tfvars(self, cluster_data):
        try:
            TERRAFORM_DIR = "./infra/azure"

            # Load existing tfvars file
            tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")

            if os.path.exists(tf_vars_path):
                with open(tf_vars_path, "r") as f:
                    tf_vars = json.load(f)
            else:
                tf_vars = {"clusters": {}}
            # Extract cluster details from request
            cluster_name = cluster_data["name"]

            # Format data to match Terraform structure
            tf_vars["clusters"][cluster_name] = cluster_data

            # Save updated tfvars.json
            with open(tf_vars_path, "w") as file:
                json.dump(tf_vars, file, indent=4)

            return True
        except Exception:
            return False

    def delete_from_azure_tfvars(self, cluster_name):
        TERRAFORM_DIR = "./infra/azure"

        tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")

        # Load existing Terraform variables
        if os.path.exists(tf_vars_path):
            with open(tf_vars_path, "r") as f:
                tf_vars = json.load(f)
        else:
            return {"error": "No clusters found in Terraform configuration"}

        # Check if the cluster exists
        if cluster_name not in tf_vars["clusters"]:
            return {"error": f"Cluster '{cluster_name}' does not exist"}

        # Remove the cluster
        del tf_vars["clusters"][cluster_name]

        # Save updated variables
        with open(tf_vars_path, "w") as f:
            json.dump(tf_vars, f, indent=2)

    def get_subscriptions(self):
        credential = DefaultAzureCredential()
        subscription_client = SubscriptionClient(credential)
        subscription_mapper = {}
        for sub in subscription_client.subscriptions.list():
            subscription_mapper[sub.subscription_id] = sub.display_name

        return subscription_mapper

    def list_azure_clusters(self, azure_subscription_mapper):
        try:
            credential = DefaultAzureCredential()
            SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")
            aks_client = ContainerServiceClient(credential, SUBSCRIPTION_ID)

            clusters = aks_client.managed_clusters.list()
            cluster_list = []

            for cluster in clusters:
                cluster_list.append(
                    {
                        "name": cluster.name,
                        "location": cluster.location,
                        "status": cluster.provisioning_state,
                        "cloud": "Azure",
                        "key_id": SUBSCRIPTION_ID,
                        "display_name": azure_subscription_mapper[SUBSCRIPTION_ID],
                    }
                )

            return cluster_list
        except Exception as ex:
            print(ex)
            return []

    async def create_azure_container(
        self, resource_group, location, storage_account, container_name
    ):
        try:
            subscription_id = os.environ.get("ARM_SUBSCRIPTION_ID")

            credential = DefaultAzureCredential()

            resource_client = ResourceManagementClient(credential, subscription_id)
            resource_client.resource_groups.create_or_update(resource_group, {"location": location})

            storage_client = StorageManagementClient(credential, subscription_id)
            storage_async_operation = storage_client.storage_accounts.begin_create(
                resource_group,
                storage_account,
                {
                    "location": location,
                    "sku": {"name": "Standard_LRS"},
                    "kind": "StorageV2",
                    "enable_https_traffic_only": True,
                },
            )
            storage_account_result = storage_async_operation.result()

            keys = storage_client.storage_accounts.list_keys(resource_group, storage_account)
            account_key = keys.keys[0].value
            connection_str = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={account_key};EndpointSuffix=core.windows.net"

            blob_service_client = BlobServiceClient.from_connection_string(connection_str)
            blob_service_client.create_container(container_name)

        except Exception as ex:
            print(ex)
            raise HTTPException(
                detail="The request bucket name is not available",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def initialize_backend(self, azure_bucket_data):
        backend_config = f"""
        resource_group_name  = "{azure_bucket_data["resource_group_name"]}"
        storage_account_name  = "{azure_bucket_data["storage_account_name"]}"
        container_name = "{azure_bucket_data["container_name"]}"
        key = "{azure_bucket_data["key"]}"
        """

        configure_backend(
            backend_config=backend_config,
            infra="azure",
            bucket_name=azure_bucket_data["container_name"],
        )
