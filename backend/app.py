from fastapi import FastAPI, File, UploadFile, Request, BackgroundTasks
import os
import subprocess
from fastapi.responses import StreamingResponse
import time
from google.cloud import container_v1
from kubernetes import client, config
import json

app = FastAPI()

GCP_KEY_PATH = "/tmp/terraform-sa-key.json"  # Temporary storage for the key

@app.post("/upload-gcp-key/")
async def upload_gcp_key(file: UploadFile = File(...)):
    try:
        # Save the uploaded JSON key file
        with open(GCP_KEY_PATH, "wb") as f:
            f.write(await file.read())

        # Set the environment variable for Terraform authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
        

        return {"message": "GCP key uploaded and configured successfully"}
    except Exception as e:
        return {"error": str(e)}



@app.post("/set-gcp-project-region")
async def set_gcp_project_and_region(req: Request):
    try:
        data = await req.json()
        project_id = data.get("project_id")
        region = data.get("region")
        os.environ["TF_VAR_project_id"] = project_id
        os.environ["TF_VAR_region"] = region
        return {"message": "project and region set"}
    except Exception as e:
        return {"error": str(e)}
        

@app.post("/set-gcp-gke-data")
async def set_gke_data(req: Request):
    try:
        data = await req.json()
        cluster_name = data.get("cluster_name")
        node_pool_name = data.get("node_pool_name")
        machine_type = data.get("machine_type")
        os.environ["TF_VAR_machine_type"] = machine_type
        os.environ["TF_VAR_cluster_name"] = cluster_name
        os.environ["TF_VAR_node_pool_name"] = node_pool_name
        return {"message": "cluster data set"}
    except Exception as e:
        return {"error": str(e)}
        

task_running=True
def run_terraform():
    """Runs Terraform in the background."""
    with open("terraform_output.log", "w") as log_file:
        terraform_dir = "../infra/gcp"
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            stdout=log_file, 
            stderr=log_file
        )
        process.wait() 
    task_running=False

@app.post("/create-gke-cluster")
async def create_gke_cluster(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_terraform)
    return {"message": "Terraform execution started in background."}



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


def list_gke_clusters(project_id: str, region: str):
    """Lists GKE clusters in a given project and region."""
    client = container_v1.ClusterManagerClient()
    parent = f"projects/{project_id}/locations/{region}"


    # container_v1
    try:
        response = client.list_clusters(parent=parent)
        clusters = [{"name": c.name, "status": c.status, "location": c.location} for c in response.clusters]
        return clusters if clusters else {"message": "No clusters found"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/list-gke-clusters/")
def get_gke_clusters(project_id: str, region: str):
    """API endpoint to list GKE clusters in a given project and region."""
    return list_gke_clusters(project_id, region)

@app.post("/add-gke-cluster/")
async def add_cluster(req: Request, background_tasks: BackgroundTasks):
    data = await req.json()
    cluster_name: str = data.get("cluster_name") 
    location: str = data.get("location")
    machine_type: str = data.get("machine_type")
    node_count: int = data.get("node_count")
    """
    API to add a new GKE cluster without deleting existing ones.
    Example request:
    {
        "cluster_name": "new-cluster",
        "location": "us-central1-a",
        "machine_type": "e2-medium",
        "node_count": 3
    }
    """
    TERRAFORM_DIR = "../infra/gcp"
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
    background_tasks.add_task(run_terraform)


    return {"message": f"Cluster '{cluster_name}' creation started"}



@app.delete("/delete-gke-cluster/{cluster_name}")
def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """

    TERRAFORM_DIR = "../infra/gcp"

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

    background_tasks.add_task(run_terraform)
    

    return {"message": f"Cluster '{cluster_name}' deletion started"}