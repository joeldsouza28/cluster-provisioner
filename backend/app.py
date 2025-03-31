from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from backend.db.connection import register_startup_event, register_shutdown_event
from backend.db.dependency import get_db_connection
from backend.db.dao import GcpDao, AzureDao
from backend.utils import GCPUtils, AzureUtil, TerraformUtils, log_streamer, run_azure_terraform, run_kubernetes_terraform
app = FastAPI()
register_startup_event(app=app)
register_shutdown_event(app=app)

log_file_path = "terraform_output.log"

task_running = True
@app.get("/stream-logs/{log_id}")
def stream_logs(req: Request):
    """API endpoint to stream logs in real-time."""
    log_id = req.path_params.get("log_id")
    return StreamingResponse(log_streamer(log_id=log_id), media_type="text/plain")


# log_thread = threading.Thread(target=lambda: [print(log) for log in log_streamer(log_file_path)])
# log_thread.start()


# log_thread.join()

@app.get("/list-clusters/")
async def get_gke_clusters(db=Depends(get_db_connection)):
    """API endpoint to list GKE clusters in a given project and region."""
    gcp_utils = GCPUtils(db=db)
    azure_utils = AzureUtil(db=db)    

    await gcp_utils.set_gcp_env()
    await azure_utils.set_azure_env()

    gke_clusters = gcp_utils.list_gke_clusters()
    azure_clusters = azure_utils.list_azure_clusters()
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

@app.post("/add-azure-keys")
async def add_azure_key(req: Request, db=Depends(get_db_connection)):
    data = await req.json()
    azure_dao = AzureDao(db=db)

    key_data = {
        "client_id": data.get("client_id"),
        "client_secret": data.get("client_secret"),
        "tenant_id": data.get("tenant_id"),
        "subscription_id": data.get("subscription_id")
    }
    

    await azure_dao.add_azure_keys(data=key_data)

    return {
        "message": "Key successfully added"
    }


@app.post("/add-gke-cluster/")
async def add_cluster(req: Request, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):

    gcp_util = GCPUtils(db=db)
    tf_utils = TerraformUtils(db=db)
    await gcp_util.set_gcp_env()

    data = await req.json()
    gcp_util.update_gcp_tfvars(cluster_data=data)

    tf_log_id = await tf_utils.get_log_id(provider="GCP")
    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})


    return {"message": f"Cluster {data["name"]} creation started", "stream_url": f"/stream-logs/{tf_log_id}"}



@app.delete("/delete-gke-cluster/{cluster_name}")
async def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """
    gcp_utils = GCPUtils(db=db)
    tf_utils = TerraformUtils(db=db)
    await gcp_utils.set_gcp_env()
    gcp_utils.delete_from_gcp_tfvars(cluster_name=cluster_name)
    tf_log_id = await tf_utils.get_log_id(provider="GCP")

    
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})
    

    return {"message": f"Cluster '{cluster_name}' deletion started", "stream_url": f"/stream-logs/{tf_log_id}"}



@app.post("/add-azure-cluster")
async def add_azure_cluster(req: Request, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to add a new AKS cluster and trigger Terraform.
    """
    azure_util = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_util.set_azure_env()
    
    data = await req.json()
    azure_util.update_azure_tfvars(cluster_data=data)

    tf_log_id = await tf_utils.get_log_id(provider="Azure")

    
    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
    return {"message": f"Cluster {data["name"]} creation started", "stream_url": f"/stream-logs/{tf_log_id}"}



@app.delete("/delete-azure-cluster/{cluster_name}")
async def delete_azure_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """
    azure_utils = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_utils.set_azure_env()
    azure_utils.delete_from_azure_tfvars(cluster_name=cluster_name)

    tf_log_id = await tf_utils.get_log_id(provider="Azure")

    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
    return {"message": f"Cluster '{cluster_name}' deletion started","stream_url": f"/stream-logs/{tf_log_id}"}