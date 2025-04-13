import SelectInputs from "../../components/form/form-elements/SelectInputs";
import Input from "../../components/form/input/InputField";
import Label from "../../components/form/Label";
import { useEffect, useState } from "react";
import Button from "../../components/ui/button/Button";
import { Modal } from "../../components/ui/modal";
import {LogStream} from "../../components/stream";
import LogList from "../../components/loglist";

export default function AddCluster(){
    type Item = {
        value: number;
        label: string;
    };

    let cloud_options = [
        {value: "gcp", label: "GCP"},
        {value: "azure", label: "Azure"},
    ]

    let [cloud, setCloud] = useState("")
    let [regions, setRegion] = useState<Item[]>([])
    let [machineTypes, setMachineTypes] = useState<Item[]>([])
    let [errorText, setErrorText] = useState("")
    let [nodeCountErrorText, setNodeCountErrorText] = useState("")
    let [nodeCountError, setNodeCountError] = useState(false)
    let [isModalOpen, setIsModalOpen] = useState(false)
    let [enableModal, setEnableModal] = useState(true)

    let [streamUrl, setStreamUrl] = useState("")
    let [logStreamModal, setLogStreamModal] = useState(false)
    let [runningTasks, setRunningTasks] = useState([])


    let [clusterName, setClusterName] = useState("")
    let [resourceGroupName, setResourecGroupName] = useState("")
    let [resourceGroupNameError, setResourecGroupNameError] = useState(false);
    let [resourceGroupNameErrorText, setResourecGroupNameErrorText] = useState("");


    let [dnsPrefix, setDnsPrefix] = useState("");
    let [dnsPrefixError, setDnsPrefixError] = useState(false);
    let [dnsPrefixErrorText, setDnsPrefixErrorText] = useState("");
    let [nodeCount, setNodeCount] = useState(0)
    let [machineType, setMachineType] = useState("")
    let [location, setLocation] = useState("")



    let [error, setError] = useState(false)

    const getRunningTasks = ()=>{
        fetch("http://localhost:8000/api/get-running-tasks")
        .then(resp=>resp.json())
        .then((data)=>{
            data = data["logs_streams"]
            let log_stream_final = []
            for(let i = 0; i < data.length; i++){
                console.log(data)
                log_stream_final.push({
                    "log_id": data["log_id"],
                    "cloud": data["provider"],
                    "stream_status": data["stream_status"],
                    "stream_url": `http://localhost:8000${data[i]["stream_url"]}`
                })
            }
            console.log(log_stream_final)
            setRunningTasks(data);

        })
    }

    const getGcpRegions = ()=>{
        fetch(`http://localhost:8000/api/get-gcp-regions`).then(resp=>{
            resp.json().then(data=>{
                let regions = data["regions"];
                let regionFormatted = []
                for(let i = 0; i < regions.length; i++){
                    regionFormatted.push({
                        value: regions[i],
                        label: regions[i],
                    })
                }
                setRegion(regionFormatted);
            })
        })
    }

    const getAzureRegions = ()=>{
        fetch(`http://localhost:8000/api/get-azure-regions`).then(resp=>{
            resp.json().then(data=>{
                let regions = data["regions"];
                let regionFormatted = []
                for(let i = 0; i < regions.length; i++){
                    regionFormatted.push({
                        value: regions[i],
                        label: regions[i],
                    })
                }
                setRegion(regionFormatted);
            })
        })
    }

    const getGcpMachineTypes = (region: string)=>{
        fetch(`http://localhost:8000/api/get-gcp-machine-types?region=${region}`).then(resp=>{
            resp.json().then(data=>{
                let machine_types = data["machine_types"];
                let machineTypesFormatted = []
                for(let i = 0; i < machine_types.length; i++){
                    machineTypesFormatted.push({
                        value: machine_types[i],
                        label: machine_types[i],
                    })
                }
                setMachineTypes(machineTypesFormatted);
            })
        });
    }

    const getAzureMachineTypes = (region: string)=>{
        fetch(`http://localhost:8000/api/get-azure-machine-types?region=${region}`).then(resp=>{
            resp.json().then(data=>{
                let machine_types = data["machine_types"];
                let machineTypesFormatted = []
                for(let i = 0; i < machine_types.length; i++){
                    machineTypesFormatted.push({
                        value: machine_types[i],
                        label: machine_types[i],
                    })
                }
                setMachineTypes(machineTypesFormatted);
            })
        });
    }

    const handleCloudChange = (value: string) => {
        setCloud(value);
        setRegion([]);
        setMachineTypes([]);
        if(value == "gcp"){
            getGcpRegions();
        }else if(value == "azure"){
            getAzureRegions();
        }
    };

    const handleRegionChange=(value: string) =>{
        setLocation(value);

        if(cloud == "gcp"){
            getGcpMachineTypes(value);
        }
        else if(cloud == "azure"){

            getAzureMachineTypes(value)
        }
    }

    const handleMachineTypeChange=(value: string) =>{
        setMachineType(value)
    }
    const isValid = (input: string)=> {
        return input === '' || /^[a-z][a-z-]*$/.test(input);
    }

    const handleResourceGroupNameChange = (value: string)=>{
        if(!isValid(value)){
            setResourecGroupNameError(true)
            setResourecGroupNameErrorText("Can only use combination of lower case alphabet and hyphens. Name cannot begin with hyphens")
        }else{
            setResourecGroupNameError(false);
            setResourecGroupNameErrorText("");
            if(value !== ""){
                setResourecGroupName(value);
            }
        }
    }
    const handleDnsPrefixChange = (value: string)=>{
        if(!isValid(value)){
            setDnsPrefixError(true)
            setDnsPrefixErrorText("Can only use combination of lower case alphabet and hyphens. Name cannot begin with hyphens")
        }else{
            setDnsPrefixError(false);
            setDnsPrefixErrorText("");
            if(value !== ""){
                setDnsPrefix(value);
            }
        }
    }
    const handleClusterNameChange = (value: string)=>{
        if(!isValid(value)){
            setError(true);
            setErrorText("Can only use combination of lower case alphabet and hyphens. Name cannot begin with hyphens");
        }else{
            setError(false);
            setErrorText("");
            if(value !== ""){
                setClusterName(value);
            }
        }        
    }

    const handleNodeCountChange = (value: string)=>{
        let nodeCount = parseInt(value);
        if(nodeCount<=0){
            setNodeCountError(true);
            setNodeCountErrorText("Node count cannot be less than zero");
        }else{
            setNodeCountError(false);
            setNodeCountErrorText("");
            setNodeCount(nodeCount);
        }
    }

    const openLogStreamModal = (i: number)=>{
        setLogStreamModal(true);
        setStreamUrl(`http://localhost:8000${runningTasks[i]["stream_url"]}`);
        setIsModalOpen(false);

    }
    const closeLogStreamModal = ()=>{
        setLogStreamModal(false)
    }


    const createGCPCluster = ()=>{
        fetch("http://localhost:8000/api/add-gke-cluster/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: clusterName,
                location: location,
                node_count: nodeCount,
                machine_type: machineType,
            }),
        })
        .then(response => response.json())
        .then(data => {
            setStreamUrl(`http://localhost:8000${data["stream_url"]}`);
            console.log("Success:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    const createAzureCluster = ()=>{
        fetch("http://localhost:8000/api/add-azure-cluster/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: clusterName,
                location: location,
                node_count: nodeCount,
                vm_size: machineType,
                resource_group_name: resourceGroupName,
                dns_prefix: dnsPrefix
            }),
        })
        .then(response => response.json())
        .then(data => {
            setStreamUrl(`http://localhost:8000${data["stream_url"]}`);
            console.log("Success:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    const openModal = ()=>{
        setIsModalOpen(true);
        getRunningTasks();
    }

    const closeModal = ()=>{
        setIsModalOpen(false);
    }

    const createCluster = ()=>{
        openModal();
        setEnableModal(true);
       if(cloud === "gcp"){
            createGCPCluster();
       }
       else if(cloud === "azure"){
            createAzureCluster();
       }
    }

    useEffect(()=>{
        console.log("here")
    }, [])
    

    return (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-1">
            {
               enableModal? 
               <div className="flex justify-end">
                    <Button className="w-50" onClick={openModal}>
                        Show Running Tasks
                    </Button>
                </div>: null
            }
            <Modal isOpen={logStreamModal} isFullscreen={false} onClose={closeLogStreamModal} className="h-200 w-lvh px-10 pt-10" >
                <LogStream streamUrl={streamUrl}/>
            </Modal>
            {
            <Modal isOpen={isModalOpen} isFullscreen={false} onClose={closeModal} className="h-200 w-lvh px-10 pt-10" >
                <LogList runningTasks={runningTasks} openLogStreamModal={openLogStreamModal}/>
            </Modal>
            }
            <div className="space-y-6">
                <Label htmlFor="input">Cluster Name</Label>
                <Input type="text" id="input" onChange={(e)=>handleClusterNameChange(e.target.value)} error={error} hint={errorText} />
            </div>
            <div className="space-y-6">
                <Label htmlFor="input">Node Count</Label>
                <Input type="number" id="input" onChange={(e)=>handleNodeCountChange(e.target.value)} error={nodeCountError} hint={nodeCountErrorText}/>
            </div>

            
            <div className="space-y-6">
                <SelectInputs  options={cloud_options} label={"Select Cloud"} handleSelectChange={handleCloudChange}/>
            </div>
            {
                cloud == "azure" ? (
                    <div className="space-y-6">
                        <Label htmlFor="input">Resource Group Name</Label>
                        <Input type="text" id="input" onChange={(e)=>handleResourceGroupNameChange(e.target.value)} error={resourceGroupNameError} hint={resourceGroupNameErrorText} />
                    </div>): null
            }
            {
                cloud == "azure" ? (
                    <div className="space-y-6">
                        <Label htmlFor="input">DNS Prefix</Label>
                        <Input type="text" id="input" onChange={(e)=>handleDnsPrefixChange(e.target.value)} error={dnsPrefixError} hint={dnsPrefixErrorText} />
                    </div>): null
            }
            {
                regions.length > 0  ? <div className="space-y-6">
                    <SelectInputs  options={regions} label={"Select Region"} handleSelectChange={handleRegionChange}/>
                </div>: null
            }
            {
                machineTypes.length > 0  ? <div className="space-y-6">
                    <SelectInputs  options={machineTypes} label={"Select Machine Type"} handleSelectChange={handleMachineTypeChange}/>
                </div>: null
            }
            {
                clusterName !== "" && nodeCount > 0 && machineType != "" && location != "" ? (
                    <div>
                        <Button onClick={createCluster}>
                            Create Cluster
                        </Button>
                    </div>
                ): null
            }
        </div>
    )
}