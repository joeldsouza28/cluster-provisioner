from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from backend.utils import GCPUtils, AzureUtil, TerraformUtils, log_streamer
from backend.db.dependency import get_db_connection
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
import os

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
        },
    )

client_id = os.environ.get("GITHUB_CLIENT_ID")
client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

config_data = {
    'GITHUB_CLIENT_ID': client_id,
    'GITHUB_CLIENT_SECRET': client_secret,
}




config = Config(environ=config_data)
oauth = OAuth(config)
oauth.register(
    name='github',
    client_id=config_data["GITHUB_CLIENT_ID"],
    client_secret=config_data["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email read:user'},
)

@api_router.get("/check-session")
async def check_session(request: Request):
    print(request.session)
    if not bool(request.session):
        print("here")
        return RedirectResponse("/login")
    else:
        print("here1")
        return {
            "user": request.session["user"]
        }


@api_router.get("/logout")
async def logout(request: Request):
    request.session["user"] = None
    return {
        "message": "Logged out"
    } 

@api_router.get("/oauth")
async def oauth_login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@api_router.get("/callback", name="auth")
async def auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    profile = await oauth.github.get('user', token=token)
    user_data = profile.json()
    print(user_data)
    request.session["user"] = user_data
    return RedirectResponse(url="/")


@api_router.get("/list-clusters")
async def get_gke_clusters(db=Depends(get_db_connection)):
    """API endpoint to list GKE clusters in a given project and region."""
    gcp_utils = GCPUtils(db=db)
    azure_utils = AzureUtil(db=db)
    gke_clusters = []
    azure_clusters = []
    azure_keys = await azure_utils.get_azure_keys()
    gcp_keys = await gcp_utils.get_gcp_keys()

    for key in azure_keys:
        await azure_utils.set_azure_env(key_id=key["subscription_id"])
        azure_clusters += azure_utils.list_azure_clusters()
    
    for key in gcp_keys:
        await gcp_utils.set_gcp_env(id=key["project_id"])
        gke_clusters += gcp_utils.list_gke_clusters()


    return {"clusters": gke_clusters + azure_clusters}


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
        final_data.append(
            {
                "log_id": data["log_id"],
                "provider": data["provider"],
                "stream_status": data["stream_status"],
                "stream_url": f"/api/common/stream-logs/{data['log_id']}",
                "action": data["action"],
                "cluster_name": data["cluster_name"],
                "location": data["location"],
            }
        )

    return {"logs_streams": final_data}
