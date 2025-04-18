import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getKeys, getRegions, Item } from "../../services";
import GCPKeysTable from "../../components/tables/BasicTables/GCPKeysTable";
import AzureKeysTable from "../../components/tables/BasicTables/AzureKeysTable";
import Button from "../../components/ui/button/Button";
import { Modal } from "../../components/ui/modal";
import Label from "../../components/form/Label";
import Input from "../../components/form/input/InputField";
import GCPRemoteBackend from "../../components/tables/BasicTables/GCPRemoteBackend";
import { addKeys, deleteKey, setActiveKey, addRemoteBackend, getRemoteBackend} from "../../services";
import SelectInputs from "../../components/form/form-elements/SelectInputs";
import Loader from "../../components/loader";


export default function KeysPage(){

    let [tableData, setTableData] = useState([]);
    let [remoteBackends, setRemoteBackends] = useState([]);

    let [openGCPKeyModal, setGCPKeyModal] = useState(false);
    let [showError, setShowError] = useState(false);
    let [showAddRemoteBackend, setAddRemoteBackend] = useState(true);
    let [showLoader, setShowLoader] = useState(true);
    let [showDataLoader, setDataLoader] = useState(false);




    const [privateKey, setPrivateKey] = useState("");
    const [privateKeyId, setPrivateKeyId] = useState("");
    const [clientId, setClientId] = useState("");
    const [clientEmail, setClientEmail] = useState("");
    const [projectId, setProjectId] = useState("");
    const [type, setType] = useState("");
    const [projectIds, setProjectIds] = useState<{value: string, label: string}[]>([]);
    const [regions, setRegions] = useState<Item[]>([]);
    const [bucketModal, setBucketModal] = useState(false)
    const [bucketName, setBucketName] = useState("");
    const [bucketProjectId, setBucketProjectId] = useState("");
    const [bucketRegion, setBucketRegion] = useState("");


    const { provider } = useParams(); 

    useEffect(()=>{
        const fetchKeys = async () => {
            const data = await getKeys(provider?provider:"");
            const regionData = await getRegions(provider?provider:"");
            const remoteBackends = await getRemoteBackend(provider?provider:"")
            setTableData(data);
            let projectIdList = [];

            for(let i = 0; i < data.length; i++){
                projectIdList.push({
                    value: data[i]["project_id"],
                    label: data[i]["project_id"]
                })
            }
            setProjectIds(projectIdList);
            setRegions(regionData);
            setRemoteBackends(remoteBackends);
            setDataLoader(true);
          };
        fetchKeys();
    }, []);

    const openGCPModal = ()=>{
        setGCPKeyModal(true);
    }

    const closeGCPModal = ()=>{
        setGCPKeyModal(false);
        setPrivateKey("");
    }

    
    const addKeysFunction = async()=>{
        let response = await addKeys({
            client_id: clientId,
            client_email: clientEmail,
            private_key: privateKey,
            private_key_id: privateKeyId,
            project_id: projectId,
            type: type

        }, 
        provider?provider:"");
        if(response.status == 200){
            setGCPKeyModal(false);
            const data = await getKeys(provider?provider:"");
            setTableData(data);
        }else{

        }
    }

    const deleteKeyFunction = async(id: number)=>{
        let response = await deleteKey(id, provider?provider:"");
        if(response.status == 200){
            const data = await getKeys(provider?provider:"");
            setTableData(data);
        }else{

        }
    }

    const setActiveKeyFunction = async(id: number)=>{
        let response = await setActiveKey(id, provider?provider: "");
        if(response.status == 200){
            const data = await getKeys(provider?provider:"");
            setTableData(data);
            setPrivateKey("");
        }else{

        }
    }

    const addRemoteBackendFunc = async()=>{
        setShowError(false);
        setAddRemoteBackend(false);
        let response = await addRemoteBackend({
            bucket_name: bucketName,
            project_id: bucketProjectId,
            location: bucketRegion,
        }, provider?provider:"");
        

        if(response.status === 400){
            setShowError(true);
        }else{
            setBucketModal(false);
        }
        const remoteBackends = await getRemoteBackend(provider?provider:"");
        setRemoteBackends(remoteBackends);
        setAddRemoteBackend(true);
    }

    const openBucketModal = ()=>{
        setBucketModal(true)
    }

    const closeBucketModal = ()=>{
        setBucketModal(false);
    }

     return (
            <div >
                <Modal isOpen={openGCPKeyModal} onClose={()=>{closeGCPModal()}} className="h-200 w-lvh px-10 pt-10 overflow-y-scroll">
                <div className="space-y-6">
                    <Label htmlFor="input">Project Id</Label>
                    <Input type="text" id="input" onChange={(e)=>setProjectId(e.target.value)} />
                </div>
                <div className="space-y-6 pt-10">
                    <Label htmlFor="input">Client Id</Label>
                    <Input type="text" id="input" onChange={(e)=>setClientId(e.target.value)} />
                </div>
                <div className="space-y-6 pt-10">
                    <Label htmlFor="input">Client Email</Label>
                    <Input type="text" id="input" onChange={(e)=>setClientEmail(e.target.value)} />
                </div>
                <div className="space-y-6 pt-10">
                    <Label htmlFor="input">Private Key Id</Label>
                    <Input type="text" id="input" onChange={(e)=>setPrivateKeyId(e.target.value)} />
                </div>
                <div className="space-y-6 pt-10">
                    <Label htmlFor="input">Private Key</Label>
                    <Input onChange={(e)=>{setPrivateKey(e.target.value)}} value={privateKey}/>
                </div>
                <div className="space-y-6 pt-10">
                    <Label htmlFor="input">Type</Label>
                    <Input type="text" onChange={(e)=>setType(e.target.value)}/>
                </div>
               
                <div className="space-y-6 pt-10">
                    <Button  onClick={()=>addKeysFunction()} >Add Keys</Button>
                </div>
                </Modal>
                 {showDataLoader ?
                 <div>
                    {`${provider === "gcp" ? "GCP": "Azure"} Service Account Keys`}
                    <div className="flex justify-end space-x-4 pb-10">

                        <Button onClick={openGCPModal}>
                            Add Key
                        </Button>
                    </div>
                    {provider === "gcp" ? <GCPKeysTable tableData={tableData} onDelete={deleteKeyFunction} setActive={setActiveKeyFunction}/>:<AzureKeysTable tableData={tableData} />}
                </div>: null
                }
                <Modal isOpen={bucketModal}  onClose={closeBucketModal} className="h-200 w-lvh px-10 pt-10 overflow-y-scroll">
                    <div className="space-y-6">
                        <Label htmlFor="input">Bucket Name</Label>
                        <Input type="text" id="input" onChange={(e)=>setBucketName(e.target.value)} />
                    </div>
                    <div className="space-y-6 pt-10">
                        <SelectInputs options={projectIds} handleSelectChange={setBucketProjectId} label={"Select Project"}/>
                    </div>
                    <div className="space-y-6 pt-10">
                        <SelectInputs options={regions} handleSelectChange={setBucketRegion} label={"Select Region"} />
                    </div>
                    <div className="pt-10">
                        {showAddRemoteBackend ? <Button onClick={addRemoteBackendFunc}> Add Remote Backend</Button>: <Loader/>}
                    </div>
                    <div className="text-red-500 pt-10">{showError? "Bucket with same name exists": null}<div/>
                    </div>
                </Modal>
                {showDataLoader ?<div className="pt-10">
                    {`${provider === "gcp" ? "GCP": "Azure"} Remote Backend`}
                    <div className="flex justify-end space-x-4 pb-10">
                        <Button onClick={openBucketModal}>
                            Add Remote Backend
                        </Button>
                    </div>
                    {provider === "gcp" ? <GCPRemoteBackend tableData={remoteBackends}/>:<AzureKeysTable tableData={tableData} />}  
                </div>: <Loader/>
                }
            </div>
    );
}




