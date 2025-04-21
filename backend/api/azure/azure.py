from fastapi.routing import APIRouter
from fastapi import Depends, BackgroundTasks
from backend.utils import AzureUtil, TerraformUtils, run_kubernetes_terraform
from backend.db.dao import AzureDao
from backend.schema import AzureKeys, AzureRemoteBackend, AzureClusterDetails, ActiveKey
from backend.db.dependency import get_db_connection
from fastapi import status, HTTPException

api_router = APIRouter()


@api_router.get("/get-regions")
async def get_azure_regions(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    azure_keys = await azure_utils.set_azure_env()
    if azure_keys:
        regions = await azure_utils.get_azure_regions()
    else:
        regions = []
    return {"regions": regions}


@api_router.get("/get-machine-types")
async def get_azure_machine_types(region: str, db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    azure_keys = await azure_utils.set_azure_env()
    if azure_keys:
        machine_types = await azure_utils.get_azure_machine_type(region=region)
    else:
        machine_types = []
    return {"machine_types": machine_types}


@api_router.get("/list-keys")
async def get_azure_keys(db=Depends(get_db_connection)):
    azure_utils = AzureUtil(db=db)
    data = await azure_utils.get_azure_keys()
    return {"keys": data}


@api_router.get("/get-remote-backend")
async def get_azure_remote_backend(db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)
    remote_buckets = await azure_dao.get_azure_remote_buckets()
    return {"remote_backends": remote_buckets}


@api_router.post("/add-remote-backend")
async def add_azure_remote_backend(
    azure_remote_backend: AzureRemoteBackend, db=Depends(get_db_connection)
):
    azure_dao = AzureDao(db=db)
    azure_utils = AzureUtil(db=db)
    azure_keys = await azure_utils.set_azure_env()
    if azure_keys:
        await azure_utils.create_azure_container(
            resource_group=azure_remote_backend.resource_group_name,
            location=azure_remote_backend.location,
            storage_account=azure_remote_backend.storage_account_name,
            container_name=azure_remote_backend.container_name,
        )
        await azure_dao.add_azure_remote_bucket(azure_remote_backend.model_dump())
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please add atleast one azure configuration keys")
    return {"detail": "Added remote backend for azure"}


@api_router.post("/set-active")
async def set_active(active_key: ActiveKey, db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)
    azure_utils = AzureUtil(db=db)

    from backend.utils import task_running

    log_values = list(task_running.values())
    if True in log_values:
        raise HTTPException(
            detail="Cannot set active now as you have certain terraform task running",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await azure_dao.set_active_azure_active_key(id=active_key.id, active=True)
    azure_keys = await azure_dao.get_azure_key()
    await azure_utils.set_azure_env(key_id=azure_keys["subscription_id"])
    azure_bucket_data = await azure_dao.get_azure_remote_bucket(
        key_id=azure_keys["subscription_id"]
    )
    await azure_utils.initialize_backend(azure_bucket_data=azure_bucket_data)

    return {"message": "Key successfully activated"}


@api_router.post("/add-keys")
async def add_azure_key(azure_keys: AzureKeys, db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)

    await azure_dao.add_azure_keys(data=azure_keys.model_dump())

    return {"message": "Key successfully added"}


@api_router.delete("/delete-keys/{id}")
async def delete_gcp_key(id: int, db=Depends(get_db_connection)):
    azure_dao = AzureDao(db=db)

    await azure_dao.delete_gcp_keys(id=id)

    return {"message": "Key successfully removed"}


@api_router.post("/add-cluster")
async def add_azure_cluster(
    azure_cluster_details: AzureClusterDetails,
    background_tasks: BackgroundTasks,
    db=Depends(get_db_connection),
):
    """
    API to add a new AKS cluster and trigger Terraform.
    """
    azure_util = AzureUtil(db=db)
    azure_dao = AzureDao(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_util.set_azure_env()

    azure_keys = await azure_dao.get_azure_key()
    azure_bucket = await azure_dao.get_azure_remote_bucket(key_id=azure_keys["subscription_id"])
    await azure_util.initialize_backend(azure_bucket_data=azure_bucket)

    # data = await req.json()
    azure_util.update_azure_tfvars(cluster_data=azure_cluster_details.model_dump())

    tf_log_id = await tf_utils.get_log_id(
        provider="Azure",
        action="add",
        cluster_name=azure_cluster_details.name,
        location=azure_cluster_details.location,
    )

    # Run Terraform
    background_tasks.add_task(
        run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"}
    )

    return {
        "message": f"Cluster {azure_cluster_details.name} creation started",
        "stream_url": f"/api/stream-logs/{tf_log_id}",
    }


@api_router.delete("/delete-cluster/{cluster_name}")
async def delete_azure_cluster(
    cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)
):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """
    azure_utils = AzureUtil(db=db)
    tf_utils = TerraformUtils(db=db)
    await azure_utils.set_azure_env()
    azure_utils.delete_from_azure_tfvars(cluster_name=cluster_name)

    tf_log_id = await tf_utils.get_log_id(
        provider="Azure", action="delete", cluster_name=cluster_name, location=""
    )

    background_tasks.add_task(
        run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"}
    )

    return {
        "message": f"Cluster '{cluster_name}' deletion started",
        "stream_url": f"/api/stream-logs/{tf_log_id}",
    }
