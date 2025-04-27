

type Item = {
    value: string;
    label: string;
};

type RunningTask = {
    log_id: string;
    cloud: string;
    cluster_name: string;
    location: string;
    stream_status: boolean;
    stream_url: string;
}

const baseUrl = ""


const getRegions = async (cloud: string) => {
    let regionFormatted: Item[] = [];
    let response = await fetch(`${baseUrl}/api/${cloud}/get-regions`);
    let data = await response.json();
    let regions = data["regions"];
    for (let i = 0; i < regions.length; i++) {
        regionFormatted.push({
            value: regions[i],
            label: regions[i],
        })
    }
    return regionFormatted;
};

const getMachineTypes = async (cloud: string, region: string) => {
    let machineTypes: Item[] = [];
    let response = await fetch(`${baseUrl}/api/${cloud}/get-machine-types?region=${region}`);
    let data = await response.json();
    let machine_types = data["machine_types"];
    for (let i = 0; i < machine_types.length; i++) {
        machineTypes.push({
            value: machine_types[i],
            label: machine_types[i],
        })
    }

    return machineTypes;
};

const getRunningLogTasks = async () => {
    let logStreamFinal = [];
    let response = await fetch(`${baseUrl}/api/common/get-running-tasks`);
    let data = await response.json();
    let runningTasks = data["logs_streams"];
    for (let i = 0; i < runningTasks.length; i++) {
        logStreamFinal.push({
            "log_id": runningTasks[i]["log_id"],
            "cloud": runningTasks[i]["provider"],
            "stream_status": runningTasks[i]["stream_status"],
            "stream_url": `${baseUrl}${runningTasks[i]["stream_url"]}`,
            "cluster_name": runningTasks[i]["cluster_name"],
            "location": runningTasks[i]["location"]
        });
    }


    return logStreamFinal;
};

const addCluster = async (body: Object, cloud: string) => {
    let response = await fetch(`http://localhost:8000/api/${cloud}/add-cluster`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    let data = await response.json()
    return data
};

const deleteCluster = async (clusterName: string, cloud: string, key_id: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud.toLowerCase()}/delete-cluster/${clusterName}/${key_id}`,
        {
            method: "DELETE"
        }
    );
    let data = await response.json();
    return data;
};

const getClustersList = async () => {
    let response = await fetch(`${baseUrl}/api/common/list-clusters`);
    let data = await response.json();
    return data["clusters"]

}

const getKeys = async (cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/list-keys`);
    let data = await response.json();
    return data["keys"];
}

const addKeys = async (body: Object, cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/add-keys/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    return response
}

const deleteKey = async (id: number, cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/delete-keys/${id}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
    });

    return response;
}

const setActiveKey = async (id: number, cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/set-active`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "id": id
        })
    });

    return response;
}

const addRemoteBackend = async (body: Object, cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/add-remote-backend`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(body)
    })
    return response
}

const getRemoteBackend = async (cloud: string) => {
    let response = await fetch(`${baseUrl}/api/${cloud}/get-remote-backend`);
    let data = await response.json()
    return data["remote_backends"]
}


const logout = async () => {
    await fetch(`${baseUrl}/api/common/logout`);
}

const checkSession = async () => {
    let response = await fetch(`/api/common/check-session`);
    console.log(response);
    return response
}

const getAuthUrl = () => {
    return `${baseUrl}/api/common/oauth`
}


export {
    getRegions,
    getMachineTypes,
    getRunningLogTasks,
    addCluster,
    deleteCluster,
    getClustersList,
    getKeys,
    addKeys,
    deleteKey,
    setActiveKey,
    addRemoteBackend,
    getRemoteBackend,
    logout,
    checkSession,
    getAuthUrl,
    baseUrl
};
export type { Item, RunningTask };
