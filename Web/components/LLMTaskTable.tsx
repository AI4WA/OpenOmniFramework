'use client'
import {useSubscription, gql} from "@apollo/client";
import React, {useState} from 'react';
import moment from 'moment';
import {useAppSelector} from "@/store"; // Make sure to import React when using JSX
import useMediaQuery from '@mui/material/useMediaQuery';
import {useTheme} from '@mui/material/styles';
import TaskDetailsDialog from "@/components/LLMDetailsDialog";
import {Task} from "@/types"; // Make sure to import React when using JSX

import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TablePagination,
    TableSortLabel,
    Dialog,
    DialogTitle,
    DialogContent,
    Grid,
    Typography,
    Accordion,
    AccordionSummary,
    ListItem,
    ListItemText,
    List,
    AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';


const TASK_SUB = gql`
subscription TaskList($userId: bigint!, $limit: Int, $offset: Int, $orderBy: [worker_task_order_by!]) {
  worker_task(where:
    {
        user_id: {_eq: $userId},
        work_type: {_in: ["gpu", "cpu"]}},
        limit: $limit,
        offset: $offset,
        order_by: $orderBy
    ) {
    id
    description
    result_status
    parameters
    created_at
    name
    user_id
    authenticate_user {
      username
    }
    updated_at
    work_type
  }
}

`;


const TaskCount = gql`
subscription TaskCount($userId: bigint!) {
  worker_task_aggregate(where: {
                                user_id: {_eq: $userId},        
                                work_type: {_in: ["gpu", "cpu"]}}
  ) {
    aggregate {
      count
    }
  }
}
`;


interface OrderBy {
    [key: string]: 'asc' | 'desc';
}

const TaskPage = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const [currentPage, setCurrentPage] = useState<number>(0);
    const [pageSize, setPageSize] = useState<number>(10);
    const [orderBy, setOrderBy] = useState<OrderBy>({created_at: 'desc'});
    const userId = useAppSelector(state => state.auth.authState.userId)
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);

    const handleRowClick = (task: Task) => {
        setSelectedTask(task);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
    };


    const handleChangePage = (event: unknown, newPage: number) => {
        setCurrentPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPageSize(+event.target.value);
        setCurrentPage(0);
    };

    const handleSort = (property: string) => {
        // Assuming orderBy can be an array of objects for multi-field sorting
        // Check if we're currently ordering by this property
        const isCurrentlySortedByThisProperty = orderBy[property] !== undefined;
        const currentOrder = isCurrentlySortedByThisProperty ? orderBy[property] : 'asc';

        // Toggle the order if currently sorted by this property; default to 'asc' otherwise
        const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

        // Set the new order for the property
        setOrderBy({[property]: newOrder});
    };
    const createSortHandler = (property: string) => (event: React.MouseEvent<unknown>) => {
        handleSort(property);
    };

    const {data, loading, error} = useSubscription(TASK_SUB, {
            variables: {
                userId: userId,
                limit: pageSize,
                offset: (currentPage + 1) * pageSize - pageSize,
                orderBy: [orderBy],
            }
        }
    )

    const {data: countData} = useSubscription(TaskCount, {
        variables: {
            userId: userId
        }
    })

    // Display loading overlay while loading
    if (loading) return (
        <div className="fixed top-0 left-0 z-50 w-screen h-screen flex items-center justify-center"
             style={{backgroundColor: 'rgba(255, 255, 255, 0.5)'}}>
            <div className="loader">Loading...</div>
        </div>
    );

    // Display error message if an error occurs
    if (error) {
        return (<div className="text-red-500">Error: <h3>Error:</h3>
            <p>{error.message}</p>
            {error && (
                <div>
                    <h4>Details:</h4>
                    <pre>{JSON.stringify(error, null, 2)}</pre>
                </div>
            )}(</div>)
    }

    return (
        <div>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>
                                <TableSortLabel
                                    active={orderBy['name'] !== undefined}
                                    direction={orderBy['name']}
                                    onClick={createSortHandler('name')}
                                >
                                    Task Name
                                </TableSortLabel>
                            </TableCell>

                            <TableCell>
                                <TableSortLabel
                                    active={orderBy['result_status'] !== undefined}
                                    direction={orderBy['result_status']}
                                    onClick={createSortHandler('result_status')}
                                >
                                    Status
                                </TableSortLabel>
                            </TableCell>
                            {!isMobile && <TableCell>
                                Task Type
                            </TableCell>}
                            <TableCell>
                                Prompt/Messages
                            </TableCell>
                            {!isMobile && <TableCell>
                                <TableSortLabel
                                    active={orderBy['work_type'] !== undefined}
                                    direction={orderBy['work_type']}
                                    onClick={createSortHandler('work_type')}
                                >
                                    GPU/CPU
                                </TableSortLabel>
                            </TableCell>}
                            {!isMobile && <TableCell>
                                <TableSortLabel
                                    active={orderBy["updated_at"] !== undefined}
                                    direction={orderBy["updated_at"]}
                                    onClick={createSortHandler('updated_at')}
                                >
                                    Updated At
                                </TableSortLabel>
                            </TableCell>
                            }
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data?.worker_task.map((task: Task) => (
                            <TableRow key={task.id} hover onClick={() => handleRowClick(task)}>
                                <TableCell>{task.name}</TableCell>
                                <TableCell>{task.result_status}</TableCell>
                                {!isMobile && <TableCell>{task.parameters?.llm_task_type}</TableCell>}
                                <TableCell>
                                    {task.parameters?.prompt ?
                                        `${task.parameters.prompt.substring(0, 30)}${task.parameters.prompt.length > 30 ? "..." : ""}` :
                                        `${JSON.stringify(task.messages)?.substring(0, 30)}${JSON.stringify(task.messages)?.length > 30 ? "..." : ""}`
                                    }
                                </TableCell>
                                {!isMobile && <TableCell>{task.work_type}</TableCell>}
                                {!isMobile &&
                                    <TableCell>{moment(task.created_at).format('YYYY-MM-DD HH:mm:ss')}</TableCell>}
                                {/* Repeat for other cells */}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                component="div"
                count={countData?.worker_task_aggregate?.aggregate?.count || -1}
                rowsPerPage={pageSize}
                page={currentPage}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />
            {selectedTask && (
                <TaskDetailsDialog
                    task={selectedTask}
                    open={openDialog}
                    onClose={handleCloseDialog}
                />
            )}
        </div>

    );
};

export default TaskPage;
