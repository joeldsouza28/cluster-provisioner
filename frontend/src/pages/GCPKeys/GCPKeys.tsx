import GCPKeysTable from "../../components/tables/BasicTables/GCPKeysTable";
import { useState, useEffect } from "react"


export default function GCPKeysPage(){

    let [tableData, setTableData] = useState([])

    useEffect(()=>{
        fetch(`http://localhost:8000/api/list-gcp-keys`).then(rsp=>{
            rsp.json().then(data=>{
                setTableData(data["gcp_keys"]);
            })
        })
    }, [])

    // let tableData: GCPKeys[] = []
    return (
        <div className="space-y-6">
            <GCPKeysTable tableData={tableData} />
        </div>
    )
}