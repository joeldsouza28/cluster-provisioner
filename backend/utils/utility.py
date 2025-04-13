import os
from backend.db.dao import GcpDao, AzureDao, TerraformLogDao
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.compute import ComputeManagementClient
from google.cloud import container_v1
from google.cloud import compute_v1
import time
import subprocess
from googleapiclient.discovery import build
from azure.mgmt.resource import SubscriptionClient
from google.auth import default
import requests

GCP_KEY_PATH = "/tmp/gcp_sa_key.json"  # Temporary storage for the key

task_running = {}

class TerraformUtils():
    def __init__(self, db):
        self.db = db

    async def get_log_id(self, provider):
        tf_dao = TerraformLogDao(db=self.db)
        tf_id = await tf_dao.create_log_file(provider=provider)
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
            stderr=log_file
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
            stderr=log_file
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

def configure_backend(backend_config, infra):
    

    config_file = f"./infra/{infra}/backend.config"
    if not is_terraform_initialized(path=f"./infra/{infra}"):
        with open(config_file, "w") as f:
            f.write(backend_config)

        process = subprocess.Popen(
            ["terraform", "init", "-backend-config=backend.config", "-migrate-state"],
            cwd=f"./infra/{infra}",
        )
        process.wait()


class GCPUtils():
    def __init__(self, db):
        self.db = db

    async def set_gcp_remote_backend(self, bucket_name):
        gcp_dao = GcpDao(db=self.db)
        await gcp_dao.add_gcp_remote_bucket(bucket_name=bucket_name)

    
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
        
    async def get_gcp_keys(self):
        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_keys()
        return gcp_keys

    async def set_gcp_env(self):

        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_key()
        gcp_bucket_data = await gcp_dao.get_gcp_remote_bucket()
        with open(GCP_KEY_PATH, "w", encoding="utf-8") as file:
            gcp_keys["token_uri"] = "https://oauth2.googleapis.com/token"
            json.dump(gcp_keys, file, ensure_ascii=False, indent=4)
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
        os.environ["TF_VAR_project_id"] = gcp_keys["project_id"]
        
        backend_config = f"""bucket  = "{gcp_bucket_data.bucket_name}"
        prefix  = "terraform/state"
        """

        configure_backend(backend_config=backend_config, infra="gcp")
        # os.environ["TF_VAR_bucket_name"] = gcp_bucket_data.bucket_name

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


    def list_gke_clusters(self):
        """Lists GKE clusters in a given project and region."""
        # parent = f"projects/{project_id}/locations/{region}"


        # container_v1
        try:
            client = container_v1.ClusterManagerClient()
            project_id = os.environ.get("TF_VAR_project_id")
            
            all_clusters = []
    
            response = client.list_clusters(parent=f"projects/{project_id}/locations/-")
            for cluster in response.clusters:
                all_clusters.append({
                    "name": cluster.name,
                    "location": cluster.location,
                    "status": cluster.status,
                    "cloud": "GCP"
                })
            return all_clusters 
        
        except Exception as e:
            return []




class AzureUtil():

    def __init__(self, db):
        self.db = db

    async def set_azure_remote_backend(self, data):
        azure_dao = AzureDao(db=self.db)
        await azure_dao.add_azure_remote_bucket(data=data)

    async def get_azure_keys(self):
        azure_dao = AzureDao(db=self.db)
        azure_keys = await azure_dao.get_gcp_keys()
        return azure_keys

    
    async def get_azure_regions(self):
        credential = DefaultAzureCredential()
        SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")

        url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/locations?api-version=2016-06-01"

        token = credential.get_token("https://management.azure.com/.default").token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        regions = []
        if response.status_code == 200:
            data = response.json()
            for region in data["value"]:
                regions.append(region['name'])

        return regions

    async def get_azure_machine_type(self, region):
        credential = DefaultAzureCredential()
        SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")

        token = credential.get_token("https://management.azure.com/.default").token


        url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/providers/Microsoft.Compute/locations/{region}/vmSizes?api-version=2024-07-01"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        machine_types = []
        if response.status_code == 200:
            data = response.json()
            for size in data["value"]:
                machine_types.append(size['name'])
        
        return machine_types

    async def set_azure_env(self):
        azure_dao = AzureDao(db=self.db)
        azure_key = await azure_dao.get_azure_key()
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

        azure_bucket_data = await azure_dao.get_azure_remote_bucket()

        backend_config = f"""
        resource_group_name  = "{azure_bucket_data.resource_group_name}"
        storage_account_name  = "{azure_bucket_data.storage_account_name}"
        container_name = "{azure_bucket_data.container_name}"
        key = "{azure_bucket_data.key}"
        """

        # backend_config = "./infra/azure/backend.config"

        configure_backend(backend_config=backend_config, infra="azure")


    

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
        except Exception as e:
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

    def list_azure_clusters(self):
        try:
            credential = DefaultAzureCredential()
            SUBSCRIPTION_ID = os.environ.get("TF_VAR_subscription_id")
            aks_client = ContainerServiceClient(credential, SUBSCRIPTION_ID)

            clusters = aks_client.managed_clusters.list()
            cluster_list = []
            
            for cluster in clusters:
                cluster_list.append({
                    "name": cluster.name,
                    "location": cluster.location,
                    "status": cluster.provisioning_state,
                    "cloud": "Azure"
                })

            return cluster_list
        except Exception as ex:
            return []



