from fastapi.routing import APIRouter
from fastapi import Depends, BackgroundTasks
from backend.db.dependency import get_db_connection
from backend.utils import GCPUtils, TerraformUtils, run_kubernetes_terraform
from backend.db.dao import GcpDao
from backend.schema import GCPKeys, GCPRemoteBackend, GCPClusterDetails, ActiveKey
import os

api_router = APIRouter()


@api_router.get("/get-regions")
async def get_gcp_regions(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    regions = await gcp_utils.get_gcp_regions()
    return {
        "regions": regions
    }


@api_router.get("/get-zones")
async def get_gcp_zones(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    zones = await gcp_utils.get_gcp_zones()
    return {
        "zones": zones
    }


@api_router.get("/get-machine-types")
async def get_gcp_machine_types(region: str, db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    await gcp_utils.set_gcp_env()
    machine_types = await gcp_utils.get_gcp_machine_types(region=region)
    return {
        "machine_types": machine_types
    }

@api_router.get("/list-keys")
async def get_gcp_keys(db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    data = await gcp_utils.get_gcp_keys()
    return {
        "keys": data
    }



@api_router.post("/add-remote-backend")
async def add_gcp_remote_backend(gcp_remote_backend: GCPRemoteBackend, db=Depends(get_db_connection)):
    gcp_utils = GCPUtils(db=db)
    gcp_dao = GcpDao(db=db)
    await gcp_utils.set_gcp_env(id=gcp_remote_backend.project_id)
    await gcp_utils.create_gcp_bucket(bucket_name=gcp_remote_backend.bucket_name, location=gcp_remote_backend.location)
    await gcp_dao.add_gcp_remote_bucket(bucket_name=gcp_remote_backend.bucket_name, project_id=gcp_remote_backend.project_id)
    await gcp_utils.initialize_backend(bucket_name=gcp_remote_backend.bucket_name)
    return {
        "detail": "Added remote backend for gcp"
    }


@api_router.get("/get-remote-backend")
async def get_gcp_remote_backend(db=Depends(get_db_connection)):
    gcp_dao = GcpDao(db=db)
    remote_buckets = await gcp_dao.get_gcp_remote_buckets()
    return {
        "remote_backends": remote_buckets
    }
    pass

@api_router.post("/add-keys")
async def add_gcp_key(gcp_keys: GCPKeys, db=Depends(get_db_connection)):

    gcp_dao = GcpDao(db=db)

    await gcp_dao.add_gcp_keys(data=gcp_keys.model_dump())

    return {
        "message": "Key successfully added"
    }


@api_router.delete("/delete-keys/{id}")
async def delete_gcp_key(id: int, db=Depends(get_db_connection)):

    gcp_dao = GcpDao(db=db)

    await gcp_dao.delete_gcp_keys(id=id)

    return {
        "message": "Key successfully removed"
    }

@api_router.post("/set-active")
async def set_active(active_key: ActiveKey, db=Depends(get_db_connection)):
    gcp_dao = GcpDao(db=db)
    await gcp_dao.set_active_gcp_active_key(id=active_key.id, active=True)

    return {
        "message": "Key successfully activated"
    }


@api_router.post("/add-cluster/")
async def add_cluster(gcp_cluster_details:GCPClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):

    gcp_util = GCPUtils(db=db)
    tf_utils = TerraformUtils(db=db)
    await gcp_util.set_gcp_env()
    project_id = os.environ.get("TF_VAR_project_id")
    bucket_data = await gcp_util.get_remote_bucket(project_id=project_id)
    await gcp_util.initialize_backend(bucket_name=bucket_data["bucket_name"])
    
    gcp_util.update_gcp_tfvars(cluster_data=gcp_cluster_details.model_dump())

    tf_log_id = await tf_utils.get_log_id(provider="GCP", action="add", cluster_name=gcp_cluster_details.name, location=gcp_cluster_details.location)
    # Run Terraform
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})


    return {"message": f"Cluster {gcp_cluster_details.name} creation started", "stream_url": f"/api/stream-logs/{tf_log_id}"}


@api_router.delete("/delete-cluster/{cluster_name}")
async def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
    """
    API to delete a specific GKE cluster.
    Example request: DELETE /delete-gke-cluster/cluster-1
    """
    gcp_utils = GCPUtils(db=db)
    tf_utils = TerraformUtils(db=db)
    await gcp_utils.set_gcp_env()
    gcp_utils.delete_from_gcp_tfvars(cluster_name=cluster_name)
    tf_log_id = await tf_utils.get_log_id(provider="GCP", action="delete", cluster_name=cluster_name, location="")

    
    background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})
    

    return {"message": f"Cluster '{cluster_name}' deletion started", "stream_url": f"/api/stream-logs/{tf_log_id}"}
