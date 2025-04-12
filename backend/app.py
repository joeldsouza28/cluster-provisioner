from fastapi import FastAPI
from backend.db.connection import register_startup_event, register_shutdown_event
from fastapi.responses import UJSONResponse
from importlib import metadata
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router

def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    origins = [
        "http://localhost:5173",  # React dev server
    ]

    app = FastAPI(
        title="backend",
        version=metadata.version("backend"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # or ["*"] to allow all (not recommended for prod)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    register_startup_event(app=app)
    register_shutdown_event(app=app)
    return app


# app = FastAPI()



# @app.get("/stream-logs/{log_id}")
# def stream_logs(req: Request):
#     """API endpoint to stream logs in real-time."""
#     log_id = req.path_params.get("log_id")
#     return StreamingResponse(log_streamer(log_id=log_id), media_type="text/plain")


# @app.get("/list-clusters/")
# async def get_gke_clusters(db=Depends(get_db_connection)):
#     """API endpoint to list GKE clusters in a given project and region."""
#     gcp_utils = GCPUtils(db=db)
#     azure_utils = AzureUtil(db=db)    

#     await gcp_utils.set_gcp_env()
#     await azure_utils.set_azure_env()

#     gke_clusters = gcp_utils.list_gke_clusters()
#     azure_clusters = azure_utils.list_azure_clusters()
#     return {
#         "clusters": gke_clusters + azure_clusters
#     }
    
# @app.post("/add-gcp-remote-backend")
# async def add_gcp_remote_backend(gcp_remote_backend: GCPRemoteBackend, db=Depends(get_db_connection)):
#     gcp_dao = GcpDao(db=db)
#     await gcp_dao.add_gcp_remote_bucket(bucket_name=gcp_remote_backend.bucket_name)
#     return {
#         "detail": "Added remote backend for gcp"
#     }


# @app.post("/add-azure-remote-backend")
# async def add_azure_remote_backend(azure_remote_backend: AzureRemoteBackend, db=Depends(get_db_connection)):
#     azure_dao = AzureDao(db=db)
#     await azure_dao.add_azure_remote_bucket(azure_remote_backend.model_dump())
#     return {
#         "detail": "Added remote backend for azure"
#     }


# @app.post("/add-gcp-keys")
# async def add_gcp_key(gcp_keys: GCPKeys, db=Depends(get_db_connection)):

#     gcp_dao = GcpDao(db=db)

#     await gcp_dao.add_gcp_keys(data=gcp_keys.model_dump())

#     return {
#         "message": "Key successfully added"
#     }

# @app.post("/add-azure-keys")
# async def add_azure_key(azure_keys: AzureKeys, db=Depends(get_db_connection)):
    
#     azure_dao = AzureDao(db=db)

#     await azure_dao.add_azure_keys(data=azure_keys.model_dump())

#     return {
#         "message": "Key successfully added"
#     }


# @app.post("/add-gke-cluster/")
# async def add_cluster(gcp_cluster_details:GCPClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):

#     gcp_util = GCPUtils(db=db)
#     tf_utils = TerraformUtils(db=db)
#     await gcp_util.set_gcp_env()

#     gcp_util.update_gcp_tfvars(cluster_data=gcp_cluster_details.model_dump())

#     tf_log_id = await tf_utils.get_log_id(provider="GCP")
#     # Run Terraform
#     background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})


#     return {"message": f"Cluster {gcp_cluster_details.name} creation started", "stream_url": f"/stream-logs/{tf_log_id}"}


# @app.get("/")
# def health_check(req: Request):
#     return {"Success": True}


# @app.delete("/delete-gke-cluster/{cluster_name}")
# async def delete_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
#     """
#     API to delete a specific GKE cluster.
#     Example request: DELETE /delete-gke-cluster/cluster-1
#     """
#     gcp_utils = GCPUtils(db=db)
#     tf_utils = TerraformUtils(db=db)
#     await gcp_utils.set_gcp_env()
#     gcp_utils.delete_from_gcp_tfvars(cluster_name=cluster_name)
#     tf_log_id = await tf_utils.get_log_id(provider="GCP")

    
#     background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/gcp"})
    

#     return {"message": f"Cluster '{cluster_name}' deletion started", "stream_url": f"/stream-logs/{tf_log_id}"}



# @app.post("/add-azure-cluster")
# async def add_azure_cluster(azure_cluster_details: AzureClusterDetails, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
#     """
#     API to add a new AKS cluster and trigger Terraform.
#     """
#     azure_util = AzureUtil(db=db)
#     tf_utils = TerraformUtils(db=db)
#     await azure_util.set_azure_env()
    
#     # data = await req.json()
#     azure_util.update_azure_tfvars(cluster_data=azure_cluster_details.model_dump())

#     tf_log_id = await tf_utils.get_log_id(provider="Azure")

#     # Run Terraform
#     background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
#     return {"message": f"Cluster {azure_cluster_details.name} creation started", "stream_url": f"/stream-logs/{tf_log_id}"}



# @app.delete("/delete-azure-cluster/{cluster_name}")
# async def delete_azure_cluster(cluster_name: str, background_tasks: BackgroundTasks, db=Depends(get_db_connection)):
#     """
#     API to delete a specific GKE cluster.
#     Example request: DELETE /delete-gke-cluster/cluster-1
#     """
#     azure_utils = AzureUtil(db=db)
#     tf_utils = TerraformUtils(db=db)
#     await azure_utils.set_azure_env()
#     azure_utils.delete_from_azure_tfvars(cluster_name=cluster_name)

#     tf_log_id = await tf_utils.get_log_id(provider="Azure")

#     background_tasks.add_task(run_kubernetes_terraform, {"log_id": tf_log_id, "terraform_dir": "./infra/azure"})
    
#     return {"message": f"Cluster '{cluster_name}' deletion started","stream_url": f"/stream-logs/{tf_log_id}"}