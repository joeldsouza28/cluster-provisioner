from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from backend.utils import GCPUtils, AzureUtil, TerraformUtils, log_streamer
from backend.db.dependency import get_db_connection



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
            "stream_url": f"/api/common/stream-logs/{data['log_id']}",
            "action": data["action"],
            "cluster_name": data["cluster_name"],
            "location": data["location"]
        })

    return {
        "logs_streams" : final_data
    }