import AzureKeysTable from "../../components/tables/BasicTables/AzureKeysTable";
import { useState, useEffect } from "react"


export default function AzureKeysPage(){

    let [tableData, setTableData] = useState([])

    useEffect(()=>{
        fetch(`http://localhost:8000/api/list-azure-keys`).then(rsp=>{
            rsp.json().then(data=>{
                setTableData(data["azure_keys"]);
            })
        })
    }, [])

    return (
        <div className="space-y-6">
            <AzureKeysTable tableData={tableData} />
        </div>
    )
}