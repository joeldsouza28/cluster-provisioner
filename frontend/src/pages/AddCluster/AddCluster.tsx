import SelectInputs from "../../components/form/form-elements/SelectInputs";
import Input from "../../components/form/input/InputField";
import Label from "../../components/form/Label";
import { useEffect, useState } from "react";
import Button from "../../components/ui/button/Button";
import { Modal } from "../../components/ui/modal";
import {LogStream} from "../../components/stream";
import LogList from "../../components/loglist";
import { getRegions, getMachineTypes, Item, getRunningLogTasks, RunningTask, addCluster} from "../../services";


export default function AddCluster(){
    

    let cloud_options: Item[] = [
        {value: "gcp", label: "GCP"},
        {value: "azure", label: "Azure"},
    ]

    let [cloud, setCloud] = useState("")
    let [regions, setRegion] = useState<Item[]>([]);
    let [machineTypes, setMachineTypes] = useState<Item[]>([]);
    let [errorText, setErrorText] = useState("")
    let [nodeCountErrorText, setNodeCountErrorText] = useState("")
    let [nodeCountError, setNodeCountError] = useState(false)
    let [isModalOpen, setIsModalOpen] = useState(false)
    let [enableModal, setEnableModal] = useState(true)

    let [streamUrl, setStreamUrl] = useState("")
    let [logStreamModal, setLogStreamModal] = useState(false)
    let [runningTasks, setRunningTasks] = useState<RunningTask[]>([]);


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

    const getRunningTasks = async()=>{
        let data = await getRunningLogTasks();
        setRunningTasks(data);
    }

    
    const handleCloudChange = async(value: string) => {
        setCloud(value);
        setRegion([]);
        setMachineTypes([]);
        let regions = await getRegions(value);
        setRegion(regions)
    };

    const handleRegionChange=async(value: string) =>{
        setLocation(value);
        let machineTypes = await getMachineTypes(cloud, value);
        setMachineTypes(machineTypes)
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
        setStreamUrl(`${runningTasks[i]["stream_url"]}`);
        setIsModalOpen(false);

    }
    const closeLogStreamModal = ()=>{
        setLogStreamModal(false)
    }

    const openModal = ()=>{
        setIsModalOpen(true);
        getRunningTasks();
    }

    const closeModal = ()=>{
        setIsModalOpen(false);
    }

    const createCluster = async()=>{
        openModal();
        setEnableModal(true);
        let data = {}
        if(cloud === "gcp"){
            data = {
                name: clusterName,
                location: location,
                node_count: nodeCount,
                machine_type: machineType,
            }
        }
        else if(cloud === "azure"){
            data = {
                name: clusterName,
                location: location,
                node_count: nodeCount,
                vm_size: machineType,
                resource_group_name: resourceGroupName,
                dns_prefix: dnsPrefix
            }
        }
        let response_data = await addCluster(data, cloud)
        setStreamUrl(`http://localhost:8000${response_data["stream_url"]}`);
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