'use client'
import {useSubscription, gql} from "@apollo/client";

const TASK_SUB = gql`
subscription TaskList {
  worker_task(order_by: {created_at: desc}) {
    id
    description
    result_status
    parameters
    created_at
    name
    user_id
    updated_at
    work_type
  }
}
`;

const TaskPage = () => {
    const {data, loading, error} = useSubscription(TASK_SUB);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error :(</p>;

    return (
        <div>
            <h2>Task List</h2>
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Parameters</th>
                    <th>Created At</th>
                    <th>Updated At</th>
                    <th>Work Type</th>
                    <th>User ID</th>
                </tr>
                </thead>
                <tbody>
                {data && data.worker_task.map(task => (
                    <tr key={task.id}>
                        <td>{task.id}</td>
                        <td>{task.name}</td>
                        <td>{task.description}</td>
                        <td>{task.result_status}</td>
                        <td>{JSON.stringify(task.parameters)}</td>
                        {/* Assuming parameters is an object or array */}
                        <td>{new Date(task.created_at).toLocaleString()}</td>
                        <td>{new Date(task.updated_at).toLocaleString()}</td>
                        <td>{task.work_type}</td>
                        <td>{task.user_id}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default TaskPage;