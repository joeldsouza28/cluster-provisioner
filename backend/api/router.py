from fastapi.routing import APIRouter
from fastapi import Request, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from backend.utils import GCPUtils, AzureUtil, run_kubernetes_terraform, log_streamer, TerraformUtils
from backend.db.dependency import get_db_connection
from backend.db.dao import GcpDao, AzureDao
from backend.schema import GCPKeys, AzureKeys, GCPRemoteBackend, AzureRemoteBackend, AzureClusterDetails, GCPClusterDetails


api_router = APIRouter()


@api_router.get("/stream-logs/{log_id}")
def stream_logs(req: Request):
    """API endpoint to stream logs in real-time."""
    log_id = req.path_params.get("log_id")
    return StreamingResponse(
        log_streamer(log_id=log_id), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# log_thread = threading.Thread(target=lambda: [print(log) for log in log_streamer(log_file_path)])
# log_thread.start()


# log_thread.join()

@api_router.get("/list-clusters/")
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

@api_router.get("/get-gcp-regions")
async def get_gcp_regions(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    regions = await gcp_utils.get_gcp_regions()
    return {
        "regions": regions
    }

@api_router.get("/get-azure-regions")
async def get_azure_regions(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    await azure_utils.set_azure_env()
    regions = await azure_utils.get_azure_regions()
    return {
        "regions": regions
    }

@api_router.get("/get-gcp-zones")
async def get_gcp_zones(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    zones = await gcp_utils.get_gcp_zones()
    return {
        "zones": zones
    }

@api_router.get("/get-gcp-machine-types")
async def get_gcp_machine_types(region: str, db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    machine_types = await gcp_utils.get_gcp_machine_types(region=region)
    return {
        "machine_types": machine_types
    }

@api_router.get("/get-azure-machine-types")
async def get_azure_machine_types(region: str, db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    await azure_utils.set_azure_env()
    machine_types = await azure_utils.get_azure_machine_type(region=region)
    return {
        "machine_types": machine_types
    }


@api_router.get("/list-gcp-keys")
async def get_gcp_keys(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    data = await gcp_utils.get_gcp_keys()
    return {
        "gcp_keys": data
    }


@api_router.get("/list-azure-keys")
async def get_azure_keys(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    data = await azure_utils.get_azure_keys()
    return {
        "azure_keys": data
    }
    

@api_router.post("/add-gcp-remote-backend")
async def add_gcp_remote_backend(gcp_remote_backend: GCPRemoteBackend, db=Depends(get_db_connection)):
    gcp_dao = GcpDao(db=db)
    await gcp_dao.add_gcp_remote_bucket(bucket_name=gcp_remote_backend.bucket_name)
    return {
        "detail": "Added remote backend for gcp"
    }


@api_router.post("/add-azure-remote-backend")
async def add_azure_remote_backend(azure_remote_backend: AzureRemoteBackend, db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)
    await azure_dao.add_azure_remote_bucket(azure_remote_backend.model_dump())
    return {
        "detail": "Added remote backend for azure"
    }


@api_router.post("/add-gcp-keys")
async def add_gcp_key(gcp_keys: GCPKeys, db=Depends(get_db_connection)):

    gcp_dao = GcpDao(db=db)

    await gcp_dao.add_gcp_keys(data=gcp_keys.model_dump())

    return {
        "message": "Key successfully added"
    }

@api_router.post("/add-azure-keys")
async def add_azure_key(azure_keys: AzureKeys, db=Depends(get_db_connection)):
    
    azure_dao = AzureDao(db=db)

    await azure_dao.add_azure_keys(data=azure_keys.model_dump())

    return {
        "message": "Key successfully added"
    }


@api_router.post("/add-gke-cluster/")
async def add_cluster(gcp_cluster_details:GCPClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):

    gcp_util = GCPUtils(db=db)
    tf_utils = TerraformUtils(db=db)
    await gcp_util.set_gcp_env()

    gcp_util.update_gcp_tfvars(cluster_data=gcp_cluster_details.model_dump())

    tf_log_id = await tf_utils.get_log_id(provider="GCP")
    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})


    return {"message": f"Cluster {gcp_cluster_details.name} creation started", "stream_url": f"/api/stream-logs/{tf_log_id}"}


@api_router.get("/get-running-tasks")
async def get_running_task(db=Depends(get_db_connection)):
    from backend.utils import task_running
    log_ids = list(task_running.keys())
    logs_streams = []
    for log in log_ids:
        logs_streams.append(f"/api/stream-logs/{log}")

    tf_utils = TerraformUtils(db=db)
    file_data = await tf_utils.get_active_log_ids()
    logs_ids = [x["log_id"] for x in file_data]
    for log_id in logs_ids:
        if log_id in task_running and not task_running[log_id]:
            await tf_utils.update_active_log_id(id=log_id)
        elif log_id not in task_running:
            await tf_utils.update_active_log_id(id=log_id)

    file_data = await tf_utils.get_active_log_ids()
    final_data = []
    for data in file_data:
        final_data.append({
            "log_id": data["log_id"],
            "provider": data["provider"],
            "stream_status": data["stream_status"],
            "stream_url": f"/api/stream-logs/{data['log_id']}"
        })

    return {
        "logs_streams" : final_data
    }

@api_router.get("/")
def health_check(req: Request):
    return {"Success": True}


@api_router.delete("/delete-gke-cluster/{cluster_name}")
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
    

    return {"message": f"Cluster '{cluster_name}' deletion started", "stream_url": f"/api/stream-logs/{tf_log_id}"}



@api_router.post("/add-azure-cluster")
async def add_azure_cluster(azure_cluster_details: AzureClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to add a new AKS cluster and trigger Terraform.
    """
    azure_util = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_util.set_azure_env()
    
    # data = await req.json()
    azure_util.update_azure_tfvars(cluster_data=azure_cluster_details.model_dump())

    tf_log_id = await tf_utils.get_log_id(provider="Azure")

    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
    return {"message": f"Cluster {azure_cluster_details.name} creation started", "stream_url": f"/api/stream-logs/{tf_log_id}"}



@api_router.delete("/delete-azure-cluster/{cluster_name}")
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
    
    return {"message": f"Cluster '{cluster_name}' deletion started","stream_url": f"/api/stream-logs/{tf_log_id}"}