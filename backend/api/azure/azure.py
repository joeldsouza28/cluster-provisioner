from fastapi.routing import APIRouter
from fastapi import Depends, BackgroundTasks
from backend.utils import AzureUtil, TerraformUtils, run_kubernetes_terraform
from backend.db.dao import AzureDao
from backend.schema import AzureKeys, AzureRemoteBackend, AzureClusterDetails
from backend.db.dependency import get_db_connection

api_router = APIRouter()

@api_router.get("/get-regions")
async def get_azure_regions(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    await azure_utils.set_azure_env()
    regions = await azure_utils.get_azure_regions()
    return {
        "regions": regions
    }


@api_router.get("/get-machine-types")
async def get_azure_machine_types(region: str, db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    await azure_utils.set_azure_env()
    machine_types = await azure_utils.get_azure_machine_type(region=region)
    return {
        "machine_types": machine_types
    }


@api_router.get("/list-keys")
async def get_azure_keys(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    data = await azure_utils.get_azure_keys()
    return {
        "keys": data
    }
    



@api_router.post("/add-remote-backend")
async def add_azure_remote_backend(azure_remote_backend: AzureRemoteBackend, db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)
    await azure_dao.add_azure_remote_bucket(azure_remote_backend.model_dump())
    return {
        "detail": "Added remote backend for azure"
    }

@api_router.post("/add-keys")
async def add_azure_key(azure_keys: AzureKeys, db=Depends(get_db_connection)):
    
    azure_dao = AzureDao(db=db)

    await azure_dao.add_azure_keys(data=azure_keys.model_dump())

    return {
        "message": "Key successfully added"
    }



@api_router.post("/add-cluster")
async def add_azure_cluster(azure_cluster_details: AzureClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to add a new AKS cluster and trigger Terraform.
    """
    azure_util = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_util.set_azure_env()
    
    # data = await req.json()
    azure_util.update_azure_tfvars(cluster_data=azure_cluster_details.model_dump())

    tf_log_id = await tf_utils.get_log_id(provider="Azure", action="add", cluster_name=azure_cluster_details.name, location=azure_cluster_details.location)

    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
    return {"message": f"Cluster {azure_cluster_details.name} creation started", "stream_url": f"/api/stream-logs/{tf_log_id}"}



@api_router.delete("/delete-cluster/{cluster_name}")
async def delete_azure_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """
    azure_utils = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_utils.set_azure_env()
    azure_utils.delete_from_azure_tfvars(cluster_name=cluster_name)

    tf_log_id = await tf_utils.get_log_id(provider="Azure", action="delete", cluster_name=cluster_name, location="")

    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
    return {"message": f"Cluster '{cluster_name}' deletion started","stream_url": f"/api/stream-logs/{tf_log_id}"}