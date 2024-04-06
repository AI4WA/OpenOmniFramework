'use client'
import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    Grid,
    Typography,
    Button,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
} from '@mui/material';
import {useSubscription, useMutation, gql} from "@apollo/client";
import {useAppSelector} from "@/store";

interface AuthenticateUser {
    username: string;
}

interface Task {
    id: string;
    description: string;
    result_status: string;
    parameters: {
        prompt?: string; // Assuming parameters might have a prompt. Adjust according to your actual structure.
    };
    created_at: string;
    name: string;
    user_id: string;
    updated_at: string;
    work_type: string;
    authenticate_user: AuthenticateUser;
}

interface TaskWrongProps {
    status: string;
    open: boolean;
    onClose: () => void;
}

const TASK_PROBLEM_SUB = gql`
subscription TaskList($userId: bigint!, $status: String!) {
  worker_task(where: {
    user_id: {_eq: $userId},
    work_type: {_in: ["gpu", "cpu"]},
    result_status: {_eq: $status}
  }) {
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


const MUTATION_REPROCESS_TASK = gql`
mutation ReprocessTask($taskId: bigint!) {
  update_worker_task_by_pk(pk_columns: {id: $taskId}, _set: {result_status: "pending"}) {
    id
    result_status
  }
}
`;

const TaskWrong: React.FC<TaskWrongProps> = ({status, open, onClose}) => {
    const userId = useAppSelector(state => state.auth.authState.userId);
    const {data, loading, error} = useSubscription<{ worker_task: Task[] }>(TASK_PROBLEM_SUB, {
        variables: {
            userId,
            status
        }
    });

    const [reprocessTask] = useMutation(MUTATION_REPROCESS_TASK);

    const handleReprocessTask = async (taskId: string) => {
        console.log(`Reprocessing task ${taskId}`); // Implement your reprocess task logic here
        // do the mutation, change the status of the task to pending

        await reprocessTask({
            variables: {
                taskId
            }
        });
    };

    return (
        <Dialog open={open} onClose={onClose} aria-labelledby="task-details-title" maxWidth="md" fullWidth>
            <DialogTitle id="task-details-title">Task Details - {status}</DialogTitle>
            <DialogContent>
                {loading && (
                    <Grid container justifyContent="center" style={{marginTop: 20, marginBottom: 20}}>
                        <CircularProgress/>
                    </Grid>
                )}
                {error && <Typography>Error fetching tasks</Typography>}
                {data && data.worker_task.length > 0 ? (
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Prompt</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.worker_task.map((task) => (
                                <TableRow key={task.id}>
                                    <TableCell>{task.name}</TableCell>
                                    <TableCell>{task.parameters?.prompt || JSON.stringify(task.parameters?.messages) || 'No prompt available'}</TableCell>
                                    <TableCell>
                                        <Button variant="contained" color="primary"
                                                onClick={() => handleReprocessTask(task.id)}>
                                            Reprocess
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                ) : !loading && (
                    <Typography style={{marginTop: 20}}>No tasks found with status {status}</Typography>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default TaskWrong;
