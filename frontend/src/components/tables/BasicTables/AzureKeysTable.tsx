import Button from "../../ui/button/Button";
import {
    Table,
    TableBody,
    TableCell,
    TableHeader,
    TableRow,
} from "../../ui/table";
  

export interface AzureKeys {
    id: number;
    client_id: string;
    tenant_id: string;
    subscription_id: string;
    created_at: string;
    active: boolean
}


export default function AzureKeys({tableData, onDelete, setActive}) {
    return (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/[0.05] dark:bg-white/[0.03]">
          <div className="max-w-full overflow-x-auto">
            <Table>
              {/* Table Header */}
              <TableHeader className="border-b border-gray-100 dark:border-white/[0.05]">
                <TableRow>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Id
                  </TableCell>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Client Id
                  </TableCell>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Tenant Id
                  </TableCell>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Subscription Id
                  </TableCell>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Created At
                  </TableCell>
                  <TableCell
                    isHeader
                    className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                  >
                    Active
                  </TableCell>
                  
                </TableRow>
              </TableHeader>
              {/* Table Body */}
                    <TableBody className="divide-y divide-gray-100 dark:divide-white/[0.05]">
                        {tableData.map((azure_key: AzureKeys) => (
                        <TableRow key={azure_key.id}>
                            <TableCell className="px-5 py-4 sm:px-6 text-start">
                            <div className="flex items-center gap-3">
                                {azure_key.id}
            
                            </div>
                            </TableCell>
                            <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                            <div className="flex items-center gap-3">
                                {azure_key.client_id}
                            </div>
                            </TableCell>
                            <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                            <div className="flex -space-x-2">
                                {azure_key.tenant_id}
                            </div>
                            </TableCell>
                            <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                            <div className="flex -space-x-2">
                                {azure_key.subscription_id}
                            </div>
                            </TableCell>
                            <TableCell className="px-4 py-3 text-gray-500 text-theme-sm dark:text-gray-400">
                            <div className="flex -space-x-2">
                                {azure_key.created_at}
                            </div>
                            </TableCell>
                            <TableCell className="px-5 py-4 sm:px-6 text-start">
                              <Button className={azure_key.active ? "bg-green-500 hover:bg-green-800": "bg-blue-500 hover:bg-blue-800"} onClick={()=>setActive(azure_key.id)} disabled={azure_key.active}>
                                  Active
                              </Button>
                          </TableCell>
                          <TableCell className="px-5 py-4 sm:px-6 text-start">
                            <Button className="bg-red-500 hover:bg-red-800" onClick={()=>onDelete(azure_key.id)} disabled={azure_key.active}>
                                Delete
                            </Button>
                        </TableCell>
                        </TableRow>
                        ))}
                    </TableBody>
            </Table>
            </div>
        </div>
    )
}