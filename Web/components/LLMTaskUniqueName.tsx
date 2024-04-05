import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
} from '@mui/material';

interface LLMTaskUniqueNameProps {
    open: boolean;
    onClose: () => void;
    tasks: { name: string; count: number }[];
}

const LLMTaskUniqueName: React.FC<LLMTaskUniqueNameProps> = ({open, onClose, tasks}) => {
    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle>Unique Task Names</DialogTitle>
            <DialogContent>
                <TableContainer component={Paper}>
                    <Table aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <TableCell>Task Name</TableCell>
                                <TableCell align="center">Task Number</TableCell>
                                <TableCell align="center">Download Link</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {tasks.map((task) => (
                                <TableRow
                                    key={task.name}
                                    sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                >
                                    <TableCell component="th" scope="row">
                                        {task.name}
                                    </TableCell>
                                    <TableCell align="center">{task.count}</TableCell>
                                    <TableCell align="center">
                                        TODO
                                        {/*<Link href={task.downloadLink} target="_blank" rel="noopener noreferrer">*/}
                                        {/*    Download*/}
                                        {/*</Link>*/}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </DialogContent>
        </Dialog>
    );
};

export default LLMTaskUniqueName;
