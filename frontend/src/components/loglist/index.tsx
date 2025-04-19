import Button from "../ui/button/Button";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "../ui/table";

interface RunningTask {
    log_id: string;
    cloud: string;
    stream_status: boolean;
}

type LogListProps = {
    runningTasks: RunningTask[];
    openLogStreamModal: (i: number)=>void;
}


export default function LogList({runningTasks, openLogStreamModal}: LogListProps){
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                        Log Id
                    </TableCell>
                    <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                        Cloud
                    </TableCell>
                    <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                        Stream Status
                    </TableCell>
                    <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                        View
                    </TableCell>
                </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-gray-100 dark:divide-white/[0.05]">
                {runningTasks.map((data: RunningTask, i)=>(
                    <TableRow key={i}>
                        <TableCell className="px-5 py-4 sm:px-6 text-start">
                        <div className="flex items-center gap-3">
                            {data.log_id}
                        </div>
                        </TableCell>
                        <TableCell className="px-5 py-4 sm:px-6 text-start">
                        <div className="flex items-center gap-3">
                            {data.cloud}
                        </div>
                        </TableCell>
                        <TableCell className="px-5 py-4 sm:px-6 text-start">
                        <div className="flex items-center gap-3">
                            {!data.stream_status ? "In Progress": "Done"}
                        </div>
                        </TableCell>
                        <TableCell className="px-5 py-4 sm:px-6 text-start">
                        <Button onClick={()=>openLogStreamModal(i)}>
                            View
                        </Button>
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}