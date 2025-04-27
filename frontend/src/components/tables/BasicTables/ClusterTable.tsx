import Button from "../../ui/button/Button";
import {
    Table,
    TableBody,
    TableCell,
    TableHeader,
    TableRow,
} from "../../ui/table";


export interface ClusterData {
    name: string;
    location: string;
    status: string;
    cloud: string;
    key_id: string;
    display_name: string;
}

type ClusterTableProps = {
    tableData: ClusterData[];
    onDelete: (i: number) => void;
    disabledRows: number[]
}

export default function ClusterTable({ tableData, onDelete, disabledRows }: ClusterTableProps) {



    return (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/[0.05] dark:bg-white/[0.03]">
            <div className="max-w-full overflow-x-auto">
                <Table>
                    <TableHeader className="border-b border-gray-100 dark:border-white/[0.05]">
                        <TableRow>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Name
                            </TableCell>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Location
                            </TableCell>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Status
                            </TableCell>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Cloud
                            </TableCell>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Project Id/Subscription Name
                            </TableCell>
                            <TableCell
                                isHeader
                                className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
                            >
                                Delete
                            </TableCell>
                        </TableRow>
                    </TableHeader>
                    {/* Table Body */}
                    <TableBody className="divide-y divide-gray-100 dark:divide-white/[0.05]">
                        {tableData.map((cluster_data: ClusterData, i: number) => {
                            let isDisabled = disabledRows.includes(i);
                            console.log(disabledRows)
                            return (
                                <TableRow key={cluster_data.name}>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <div className="flex items-center gap-3">
                                            {cluster_data.name}
                                        </div>
                                    </TableCell>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <div className="flex items-center gap-3">
                                            {cluster_data.location}
                                        </div>
                                    </TableCell>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <div className="flex items-center gap-3">
                                            {cluster_data.status}
                                        </div>
                                    </TableCell>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <div className="flex items-center gap-3">
                                            {cluster_data.cloud}
                                        </div>
                                    </TableCell>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <div className="flex items-center gap-3">
                                            {cluster_data.display_name}
                                        </div>
                                    </TableCell>
                                    <TableCell className="px-5 py-4 sm:px-6 text-start">
                                        <Button className="bg-red-500 hover:bg-red-800" onClick={() => onDelete(i)} disabled={isDisabled}>
                                            Delete
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            )
                        })
                        }
                    </TableBody>
                </Table>
            </div>
        </div>
    )

}