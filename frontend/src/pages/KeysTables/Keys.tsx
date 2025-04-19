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
import AzureRemoteBackend from "../../components/tables/BasicTables/AzureRemoteBackend";
import { addKeys, deleteKey, setActiveKey, addRemoteBackend, getRemoteBackend} from "../../services";
import SelectInputs from "../../components/form/form-elements/SelectInputs";
import Loader from "../../components/loader";


export default function KeysPage(){

    let [tableData, setTableData] = useState([]);
    let [remoteBackends, setRemoteBackends] = useState([]);

    let [openGCPKeyModal, setGCPKeyModal] = useState(false);
    let [openAzureKeyModal, setAzureKeyModal] = useState(false);

    let [showError, setShowError] = useState(false);
    let [showAddRemoteBackend, setAddRemoteBackend] = useState(true);
    let [showErrorModal, setShowErrorModal] = useState(false);
    let [showErrorText, setShowErrorText] = useState("");

    let [showDataLoader, setDataLoader] = useState(false);




    const [privateKey, setPrivateKey] = useState("");
    const [privateKeyId, setPrivateKeyId] = useState("");
    const [clientId, setClientId] = useState("");
    const [clientEmail, setClientEmail] = useState("");
    const [tenantId, setTenantId] = useState("");
    const [subscriptionId, setSubscriptionId] = useState("");
    const [azureClientId, setAzureClientId] = useState("");
    const [azureClientSecret, setAzureClientSecret] = useState("");
    const [projectId, setProjectId] = useState("");
    const [type, setType] = useState("");
    const [projectIds, setProjectIds] = useState<{value: string, label: string}[]>([]);
    const [regions, setRegions] = useState<Item[]>([]);
    const [gcpBucketModal, setGcpBucketModal] = useState(false)
    const [azureBucketModal, setAzureBucketModal] = useState(false)

    const [bucketName, setBucketName] = useState("");
    const [bucketProjectId, setBucketProjectId] = useState("");
    const [bucketRegion, setBucketRegion] = useState("");
    const [resourceGroupName, setResourceGroupName] = useState("");
    const [storageAccountName, setStorageAccountName] = useState("");
    const [containerName, setContaierName] = useState("");
    const [keyName, setKeyName] = useState("");
    const [storageSubscriptionId, setStorageSubscriptionId] = useState("");
    const [regionSubscriptionId, setRegionSubscriptionId] = useState("");



    // const [resourceGroupName, setResourceGroupName] = useState("");
    // const [resourceGroupName, setResourceGroupName] = useState("");
    // const [resourceGroupName, setResourceGroupName] = useState("");
    // const [resourceGroupName, setResourceGroupName] = useState("");


    const { provider } = useParams(); 
    useEffect(()=>{
        console.log(provider)
        const fetchKeys = async () => {
            const data = await getKeys(provider?provider:"");
            const regionData = await getRegions(provider?provider:"");
            const remoteBackends = await getRemoteBackend(provider?provider:"")
            setTableData(data);
            console.log(data)
            let projectIdList = [];

            for(let i = 0; i < data.length; i++){
                projectIdList.push({
                    value: provider === "gcp"? data[i]["project_id"]: data[i]["subscription_id"],
                    label: provider === "gcp"? data[i]["project_id"]: data[i]["subscription_id"],
                })
            }
            setProjectIds(projectIdList);
            setRegions(regionData);
            setRemoteBackends(remoteBackends);
            setDataLoader(true);
          };
        fetchKeys();
    }, [provider]);

    const openGCPModal = ()=>{
        setGCPKeyModal(true);
    }

    const closeGCPModal = ()=>{
        setGCPKeyModal(false);
        setPrivateKey("");
    }
    const openAzureModal = ()=>{
        setAzureKeyModal(true);
    }

    const closeAzureModal = ()=>{
        setAzureKeyModal(false);
        setPrivateKey("");
    }

    
    const addKeysFunction = async()=>{
        let response = await addKeys(
            provider === "gcp"? 
            {
                client_id: clientId,
                client_email: clientEmail,
                private_key: privateKey,
                private_key_id: privateKeyId,
                project_id: projectId,
                type: type
            }: 
            {
                client_id: azureClientId,
                client_secret: azureClientSecret,
                tenant_id: tenantId,
                subscription_id: subscriptionId
            }, 
        provider?provider:"");
        if(response.status == 200){
            provider === "gcp" ? setGCPKeyModal(false): setAzureKeyModal(false);
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
            let data = await response.json()
            setShowErrorModal(true);
            setShowErrorText(data["detail"])
        }
    }

    const addRemoteBackendFunc = async()=>{
        setShowError(false);
        setAddRemoteBackend(false);
        let response = await addRemoteBackend(
            provider === "gcp" ? 
            {
            bucket_name: bucketName,
            project_id: bucketProjectId,
            location: bucketRegion,
            }:
            {
                resource_group_name: resourceGroupName,
                storage_account_name: storageAccountName,
                container_name: containerName,
                key: keyName,
                subscription_id: storageSubscriptionId,
                location: regionSubscriptionId,
            } , 
        provider?provider:"");
        

        if(response.status === 400){
            setShowError(true);
        }else{
            provider === "gcp" ?setGcpBucketModal(false): setAzureBucketModal(false);
        }
        const remoteBackends = await getRemoteBackend(provider?provider:"");
        setRemoteBackends(remoteBackends);
        setAddRemoteBackend(true);
    }

    const openBucketModal = ()=>{
        provider === "gcp" ?setGcpBucketModal(true): setAzureBucketModal(true);
    }

    const closeBucketModal = ()=>{
        provider === "gcp" ?setGcpBucketModal(false): setAzureBucketModal(false);
    }

    const closeErrorModal = ()=>{
        setShowErrorModal(false);
    }

     return (
            <div >
                <Modal isOpen={showErrorModal} className="h-30 w-lvh px-10 pt-10 overflow-y-scroll" onClose={closeErrorModal} >
                    <div>
                        {showErrorText}
                    </div>
                </Modal>
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

                        <Button onClick={provider === "gcp" ?openGCPModal:openAzureModal}>
                            Add Key
                        </Button>
                    </div>
                    {provider === "gcp" ? <GCPKeysTable tableData={tableData} onDelete={deleteKeyFunction} setActive={setActiveKeyFunction}/>:<AzureKeysTable tableData={tableData} setActive={setActiveKeyFunction} onDelete={deleteKeyFunction}/>}
                </div>: null
                }
                <Modal isOpen={openAzureKeyModal} onClose={closeAzureModal} className="h-150 w-lvh px-10 pt-10 overflow-y-scroll" >
                        <div className="space-y-6">
                            <Label htmlFor="input">Subscription Id</Label>
                            <Input type="text" id="input" onChange={(e)=>setSubscriptionId(e.target.value)} />
                        </div>
                        <div className="space-y-6 pt-10">
                            <Label htmlFor="input">Client Id</Label>
                            <Input type="text" id="input" onChange={(e)=>setAzureClientId(e.target.value)} />
                        </div>
                        <div className="space-y-6 pt-10">
                            <Label htmlFor="input">Client Secret</Label>
                            <Input type="text" id="input" onChange={(e)=>setAzureClientSecret(e.target.value)} />
                        </div>
                        <div className="space-y-6 pt-10">
                            <Label htmlFor="input">Tenant Id</Label>
                            <Input type="text" id="input" onChange={(e)=>setTenantId(e.target.value)} />
                        </div>
                        <div className="space-y-6 pt-10">
                            <Button  onClick={()=>addKeysFunction()} >Add Keys</Button>
                        </div>
                </Modal>
                <Modal isOpen={gcpBucketModal}  onClose={closeBucketModal} className="h-200 w-lvh px-10 pt-10 overflow-y-scroll">
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
                <Modal isOpen={azureBucketModal}  onClose={closeBucketModal} className="h-200 w-lvh px-10 pt-10 overflow-y-scroll">
                    <div className="space-y-6">
                        <Label htmlFor="input">Resource Group Name</Label>
                        <Input type="text" id="input" onChange={(e)=>setResourceGroupName(e.target.value)} />
                    </div>
                    <div className="space-y-6 pt-10">
                        <SelectInputs options={projectIds} handleSelectChange={setStorageSubscriptionId} label={"Select Subscription Id"}/>
                    </div>
                    <div className="space-y-6 pt-10">
                        <SelectInputs options={regions} handleSelectChange={setRegionSubscriptionId} label={"Select Regions"}/>
                    </div>
                    <div className="space-y-6 pt-10">
                        <Label htmlFor="input">Storage Account Name</Label>
                        <Input type="text" id="input" onChange={(e)=>setStorageAccountName(e.target.value)} />
                    </div>
                    <div className="space-y-6 pt-10">
                        <Label htmlFor="input">Container Name</Label>
                        <Input type="text" id="input" onChange={(e)=>setContaierName(e.target.value)} />
                    </div>
                    <div className="space-y-6 pt-10">
                        <Label htmlFor="input">Key</Label>
                        <Input type="text" id="input" onChange={(e)=>setKeyName(e.target.value)} />
                    </div>
                    <div className="space-y-6 pt-10">
                            <Button  onClick={()=>addRemoteBackendFunc()} >Add Remote Backend</Button>
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
                    {provider === "gcp" ? <GCPRemoteBackend tableData={remoteBackends}/>:<AzureRemoteBackend tableData={remoteBackends} />}  
                </div>: <Loader/>
                }
            </div>
    );
}




