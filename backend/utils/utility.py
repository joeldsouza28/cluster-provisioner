import os
from backend.db.dao import GcpDao, AzureDao
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from google.cloud import container_v1
import time
import subprocess

GCP_KEY_PATH = "/tmp/gcp_sa_key.json"  # Temporary storage for the key
log_file_path = "terraform_output.log"


task_running=True
def run_gke_terraform():
    """Runs Terraform in the background."""
    with open("terraform_output.log", "w") as log_file:
        terraform_dir = "./infra/gcp"
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file, 
            stderr=log_file
        )
        process.wait() 
        task_running=False


task_running = True  # Flag to control log streaming

def log_streamer(file_path: str):
    """Generator function to yield log file contents in real-time."""
    global task_running
    with open(file_path, "r") as file:
        file.seek(0, 2)  # Move to the end of the file
        while task_running:
            line = file.readline()
            if not line:
                time.sleep(1)  # Wait for new logs
                continue
            yield line

def run_azure_terraform():
    """Runs Terraform in the background and stops log streaming when done."""
    global task_running
    terraform_dir = "./infra/azure"
    
    with open(log_file_path, "w") as log_file:
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file,
            stderr=log_file,
            text=True
        )
    
    process.wait()  # Wait for Terraform to finish
    task_running = False  # Stop the log streamer


async def event_generator(request):
    global task_running
    with open(log_file_path, "r") as file:
        file.seek(0, 2)  # Move to the end of the file
        while task_running:
            if await request.is_disconnected():  # Stop if client disconnects
                print("Client disconnected, stopping log stream")
                return
            line = file.readline()
            if not line:
                time.sleep(1)  # Wait for new logs
                continue
            yield line




class GCPUtils():
    def __init__(self, db):
        self.db = db


    async def set_gcp_env(self):

        gcp_dao = GcpDao(db=self.db)
        gcp_keys = await gcp_dao.get_gcp_key()
        print(gcp_keys)
        with open(GCP_KEY_PATH, "w", encoding="utf-8") as file:
            gcp_keys["token_uri"] = "https://oauth2.googleapis.com/token"
            json.dump(gcp_keys, file, ensure_ascii=False, indent=4)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
        os.environ["TF_VAR_project_id"] = gcp_keys["project_id"]

    def update_gcp_tfvars(self, cluster_data):
        TERRAFORM_DIR = "./infra/gcp"

        cluster_name: str = cluster_data.get("cluster_name") 
        location: str = cluster_data.get("location")
        machine_type: str = cluster_data.get("machine_type")
        node_count: int = cluster_data.get("node_count")
        
        tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")
        os.environ["TF_VAR_region"] = location

        # Load existing Terraform variables
        if os.path.exists(tf_vars_path):
            with open(tf_vars_path, "r") as f:
                tf_vars = json.load(f)
        else:
            tf_vars = {"clusters": {}}

        # Add the new cluster
        tf_vars["clusters"][cluster_name] = {
            "location": location,
            "machine_type": machine_type,
            "node_count": node_count
        }

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
            print(e)
            return []




class AzureUtil():

    def __init__(self, db):
        self.db = db

    async def set_azure_env(self):
        azure_dao = AzureDao(db=self.db)
        azure_key = await azure_dao.get_azure_key()
        os.environ["TF_VAR_client_id"] = azure_key["client_id"]
        os.environ["TF_VAR_client_secret"] = azure_key["client_secret"]
        os.environ["TF_VAR_tenant_id"] = azure_key["tenant_id"]
        os.environ["AZURE_CLIENT_ID"] = azure_key["client_id"]
        os.environ["AZURE_TENANT_ID"] = azure_key["tenant_id"]
        os.environ["AZURE_CLIENT_SECRET"] = azure_key["client_secret"]
        os.environ["TF_VAR_subscription_id"] = azure_key["subscription_id"]

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
            tf_vars["clusters"][cluster_name] = {
                "name": cluster_data["name"],
                "location": cluster_data["location"],
                "vm_size": cluster_data["vm_size"],
                "node_count": cluster_data["node_count"],
                "resource_group_name": cluster_data["resource_group_name"],
                "dns_prefix": cluster_data["dns_prefix"]
            }

            # Save updated tfvars.json
            with open(tf_vars_path, "w") as file:
                json.dump(tf_vars, file, indent=4)

            return True
        except Exception as e:
            print(f"Error updating tfvars: {e}")
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
                    "provisioning_state": cluster.provisioning_state,
                    "cloud": "Azure"
                })

            return cluster_list
        except Exception as ex:
            return []



