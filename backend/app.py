from fastapi import FastAPI, File, UploadFile, Request, BackgroundTasks, HTTPException, Depends
import os
import subprocess
from fastapi.responses import StreamingResponse
import time
from google.cloud import container_v1, compute_v1
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from backend.db.connection import register_startup_event, register_shutdown_event
from backend.db.dependency import get_db_connection
from backend.db.dao import GcpDao

app = FastAPI()
register_startup_event(app=app)
register_shutdown_event(app=app)

GCP_KEY_PATH = "/tmp/terraform-sa-key.json"  # Temporary storage for the key
AZURE_KEY_PATH = "/tmp/azure.json"  # Temporary storage for the key


@app.post("/upload-azure-key/")
async def upload_gcp_key(file: UploadFile = File(...)):
    try:
        # Save the uploaded JSON key file
        with open(AZURE_KEY_PATH, "wb") as f:
            f.write(await file.read())

        # Set the environment variable for Terraform authentication
        os.environ["AZURE_APPLICATION_CREDENTIALS"] = AZURE_KEY_PATH
        with open(AZURE_KEY_PATH, "r") as file:
            data = json.load(file)
            os.environ["TF_VAR_client_id"] = data["clientId"]
            os.environ["TF_VAR_client_secret"] = data["clientSecret"]
            os.environ["TF_VAR_tenant_id"] = data["tenantId"]
            os.environ["AZURE_CLIENT_ID"] = data["clientId"]
            os.environ["AZURE_TENANT_ID"] = data["tenantId"]
            os.environ["AZURE_CLIENT_SECRET"] = data["clientSecret"]
            os.environ["TF_VAR_subscription_id"] = data["subscriptionId"]


        return {"message": "Azure key uploaded and configured successfully"}
    except Exception as e:
        return {"error": str(e)}


        

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

def run_azure_terraform():
    """Runs Terraform in the background."""
    with open("terraform_output.log", "w") as log_file:
        terraform_dir = "../infra/azure"
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file, 
            stderr=log_file
        )
        process.wait() 
    task_running=False




def log_streamer(file_path: str):
    """Generator function to yield log file contents in real-time."""
    with open(file_path, "r") as file:
        file.seek(0, 2)  # Move to the end of the file
        while task_running:
            line = file.readline()
            if not line:
                time.sleep(1)  # Wait for new logs
                continue
            yield line

@app.get("/stream-logs/")
def stream_logs():
    """API endpoint to stream logs in real-time."""
    return StreamingResponse(log_streamer("terraform_output.log"), media_type="text/plain")

def get_all_gcp_zones():
    """Fetches all available GCP zones dynamically."""
    compute_client = compute_v1.ZonesClient()
    project_id = os.environ.get("TF_VAR_project_id")
    zones = [zone.name for zone in compute_client.list(project=project_id)]
    return zones

def list_gke_clusters():
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
    
def list_azure_clusters():
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
        print(ex)
        return []

@app.get("/list-clusters/")
def get_gke_clusters():
    """API endpoint to list GKE clusters in a given project and region."""
    gke_clusters = list_gke_clusters()
    azure_clusters = list_azure_clusters()
    return {
        "clusters": gke_clusters + azure_clusters
    }
    
@app.post("/add-gcp-keys")
async def add_gcp_key(req: Request, db=Depends(get_db_connection)):
    data = await req.json()
    gcp_dao = GcpDao(db=db)

    key_data = {
        "client_id": data.get("client_id"),
        "client_email": data.get("client_email"),
        "private_key": data.get("private_key"),
        "private_key_id": data.get("private_key_id"),
        "project_id": data.get("project_id"),
        "type": data.get("type")
    }
    

    await gcp_dao.add_gcp_keys(data=key_data)

    return {
        "message": "Key successfully added"
    }


@app.post("/add-gke-cluster/")
async def add_cluster(req: Request, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):

    gcp_dao = GcpDao(db=db)
    gcp_keys = await gcp_dao.get_gcp_key()
    with open(GCP_KEY_PATH, "w", encoding="utf-8") as file:
        json.dump(gcp_keys, file, ensure_ascii=False, indent=4)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
    
    data = await req.json()
    cluster_name: str = data.get("cluster_name") 
    location: str = data.get("location")
    machine_type: str = data.get("machine_type")
    node_count: int = data.get("node_count")
    
    TERRAFORM_DIR = "./infra/gcp"
    tf_vars_path = os.path.join(TERRAFORM_DIR, "terraform.auto.tfvars.json")

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

    # Run Terraform
    background_tasks.add_task(run_gke_terraform)


    return {"message": f"Cluster '{cluster_name}' creation started"}



@app.delete("/delete-gke-cluster/{cluster_name}")
async def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """

    TERRAFORM_DIR = "./infra/gcp"

    gcp_dao = GcpDao(db=db)
    gcp_keys = await gcp_dao.get_gcp_key()
    with open(GCP_KEY_PATH, "w", encoding="utf-8") as file:
        json.dump(gcp_keys, file, ensure_ascii=False, indent=4)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH

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

    background_tasks.add_task(run_gke_terraform)
    

    return {"message": f"Cluster '{cluster_name}' deletion started"}


def update_azure_tfvars(cluster_data):
    """Update terraform.tfvars.json with new cluster data."""
    try:
        TFVARS_FILE = "../infra/azure"
        
        # Load existing tfvars file
        tf_vars_path = os.path.join(TFVARS_FILE, "terraform.auto.tfvars.json")
        print(tf_vars_path)

        if os.path.exists(tf_vars_path):
            with open(tf_vars_path, "r") as f:
                tf_vars = json.load(f)
        else:
            tf_vars = {"clusters": {}}
        # Extract cluster details from request
        cluster_name = cluster_data["cluster_name"]

        # Format data to match Terraform structure
        tf_vars["clusters"][cluster_name] = {
            "name": cluster_data["cluster_name"],
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



@app.post("/add-azure-cluster")
async def add_azure_cluster(req: Request, background_tasks: BackgroundTasks):
    """
    API to add a new AKS cluster and trigger Terraform.
    """
    data = await req.json()
    update_azure_tfvars(cluster_data=data)
    
    # Run Terraform
    background_tasks.add_task(run_azure_terraform)
    
    return {"message": "Cluster creation triggered successfully"}



@app.delete("/delete-azure-cluster/{cluster_name}")
def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """

    TERRAFORM_DIR = "../infra/azure"

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

    background_tasks.add_task(run_azure_terraform)
    
    return {"message": f"Cluster '{cluster_name}' deletion started"}