import ClusterTable from "../../components/tables/BasicTables/ClusterTable";
import { useState, useEffect, useRef } from "react"
import Button from "../../components/ui/button/Button";
import { Link } from "react-router";
import { Modal } from "../../components/ui/modal";
import {LogStream} from "../../components/stream";
import LogList from "../../components/loglist";
import { getRunningLogTasks, RunningTask, deleteCluster, getClustersList } from "../../services";
import Loader from "../../components/loader";
import ConfirmDialog from "../../components/confirmation";

export default function ClusterList(){

    let [tableData, setTableData] = useState([]);
    let [tableDataMapper, setTableDataMapper] = useState<Object>({});
    let [streamUrl, setStreamUrl] = useState("");
    let [isModalOpen, setIsModalOpen] = useState(false);
    let [logStreamModal, setLogStreamModal] = useState(false);
    let [showConfirmationPopup, setConfirmationPopup] = useState(false);
    let [deleteIndex, setDeleteIndex] = useState(0);
    let [disabledRows, setDisabledRows] = useState([])

    let [enableModal, setEnableModal] = useState(true)
    let [showLoader, setShowLoader] = useState(true)
    let [runningTasks, setRunningTasks] = useState<RunningTask[]>([])

    const hasFetched = useRef(false);

    const getClusters = async()=>{
       let data = await getClustersList();
       let runningTasks = await getRunningTasks();
       setTableData(data);
       let mapper = {}
       for(let i = 0; i < data.length; i++){
            const key =`${data[i].name}__${data[i].cloud}`;
            console.log(key);
            mapper[key] = i;
       }
       setTableDataMapper(mapper);
       disableDelete(runningTasks, mapper);
       if(data){
        setShowLoader(false);
       }
    }

    useEffect(()=>{
        if (!hasFetched.current) {
            hasFetched.current = true;
            getClusters();
            setShowLoader(false);
        }
        if(tableData.length === 0){
            setShowLoader(true);
        }
    }, []);



    const handleDeleteConfirm = async()=>{
        await deleteCluster(tableData[deleteIndex]["name"], tableData[deleteIndex]["cloud"]);
        // openModal();
        setDisabledRows([...disabledRows, deleteIndex])
        setEnableModal(true);
        setConfirmationPopup(false);
        getRunningTasks();
    }
    
    
    const handleDeleteClick = async(i: number)=>{
        setConfirmationPopup(true);
        setDeleteIndex(i);
    }

    const openModal = ()=>{
        setIsModalOpen(true);
        getRunningTasks();
    }

    const closeModal = ()=>{
        setIsModalOpen(false);
    }

    const disableDelete = (runningTasks, tableDataMapper)=>{
        console.log(runningTasks);
        console.log(tableDataMapper);
        for(let i = 0; i < runningTasks.length; i++){
            const key =`${runningTasks[i].cluster_name}_${runningTasks[i].location}_${runningTasks[i].cloud}`;
            console.log(key);
            if(key in tableDataMapper){
                setDisabledRows([...disabledRows, tableDataMapper[key]])
            }
        }
    }

    const getRunningTasks = async()=>{
        let runningTasks = await getRunningLogTasks();
        setRunningTasks(runningTasks);
        return runningTasks
    }
    const openLogStreamModal = (i: number)=>{
        setLogStreamModal(true);
        setStreamUrl(`${runningTasks[i]["stream_url"]}`);
        setIsModalOpen(false);

    }
    const closeLogStreamModal = ()=>{
        setLogStreamModal(false)
    }
    // let tableData: GCPKeys[] = []
    return (showLoader ? <Loader/> :
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
            {showConfirmationPopup ? <ConfirmDialog message={"Are you sure you want to delete this cluster?"} onConfirm={handleDeleteConfirm} onCancel={()=>{setConfirmationPopup(false);}}/>: null}
            <ClusterTable tableData={tableData} onDelete={handleDeleteClick} disabledRows={disabledRows}/>
        </div>
    )
}