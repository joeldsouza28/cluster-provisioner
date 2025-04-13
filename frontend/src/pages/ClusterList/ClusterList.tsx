import ClusterTable from "../../components/tables/BasicTables/ClusterTable";
import { useState, useEffect, useRef } from "react"
import Button from "../../components/ui/button/Button";
import { Link } from "react-router";
import { Modal } from "../../components/ui/modal";
import {LogStream} from "../../components/stream";
import LogList from "../../components/loglist";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "../../components/ui/table";



export default function GCPKeysPage(){

    let [tableData, setTableData] = useState([])
    let [streamUrl, setStreamUrl] = useState("")
    let [isModalOpen, setIsModalOpen] = useState(false)
    let [logStreamModal, setLogStreamModal] = useState(false)

    let [enableModal, setEnableModal] = useState(true)
    let [runningTasks, setRunningTasks] = useState([])

    const hasFetched = useRef(false);

    const getClusters = ()=>{
        fetch(`http://localhost:8000/api/list-clusters`).then(rsp=>{
            rsp.json().then(data=>{
                setTableData(data["clusters"]);
            })
        })
    }

    useEffect(()=>{
        if (!hasFetched.current) {
            hasFetched.current = true;
            getClusters();
        }
    }, [])

    const deleteGCPCluster = (clusteName: string)=>{
        console.log(clusteName);
        fetch(
            `http://localhost:8000/api/delete-gke-cluster/${clusteName}`, 
            {
            method: "DELETE"
            }
        )
        .then(resp=>resp.json())
        .then(data => {
            setStreamUrl(`http://localhost:8000${data["stream_url"]}`);
            console.log("Success:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    const deleteAzureCluster = (clusteName: string)=>{
        console.log(clusteName);
        fetch(
            `http://localhost:8000/api/delete-azure-cluster/${clusteName}`, 
            {
            method: "DELETE"
            }
        )
        .then(resp=>resp.json())
        .then(data => {
            setStreamUrl(`http://localhost:8000${data["stream_url"]}`);
            console.log("Success:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    const handleDeleteClick = (i: number)=>{
        openModal();
        setEnableModal(true);
        getRunningTasks();
        if(tableData[i]["cloud"]==="GCP"){
            deleteGCPCluster(tableData[i]["name"])
        }
        else if(tableData[i]["cloud"] === "Azure"){
            deleteAzureCluster(tableData[i]["name"])
        }
    }

    const openModal = ()=>{
        setIsModalOpen(true);
        getRunningTasks();
    }

    const closeModal = ()=>{
        setIsModalOpen(false);
    }

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
    const openLogStreamModal = (i: number)=>{
        setLogStreamModal(true);
        setStreamUrl(`http://localhost:8000${runningTasks[i]["stream_url"]}`);
        setIsModalOpen(false);

    }
    const closeLogStreamModal = ()=>{
        setLogStreamModal(false)
    }
    // let tableData: GCPKeys[] = []
    return (
        <div className="space-y-6">
            <Modal isOpen={logStreamModal} onClose={()=>closeLogStreamModal()} className="h-200 w-lvh px-10 pt-10" >
                <LogStream streamUrl={streamUrl}/>
            </Modal>
            <Modal isOpen={isModalOpen} isFullscreen={false} onClose={closeModal} className="h-200 w-lvh px-10 pt-10" >
                <div>
                    <LogList runningTasks={runningTasks} openLogStreamModal={openLogStreamModal}/>
                </div>
                {/* <LogStream streamUrl={streamUrl} postLogAction={getClusters}/> */}
            </Modal>
            <div className="flex justify-end space-x-4">
                {
                enableModal? 
                        <Button className="" onClick={openModal}>
                            Show Running Tasks
                        </Button>: null
                }
                <Button>
                    <Link to="/add-cluster">
                        Add Cluster
                    </Link>
                </Button>
            </div>
            <ClusterTable tableData={tableData} onDelete={handleDeleteClick}/>
        </div>
    )
}