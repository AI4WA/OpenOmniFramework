'use client'
import {useSubscription, gql} from "@apollo/client";
import React from 'react'; // Make sure to import React when using JSX
interface Task {
    id: string;
    description: string;
    result_status: string;
    parameters: any; // Use the appropriate type based on your actual data structure
    created_at: string;
    name: string;
    user_id: string;
    updated_at: string;
    work_type: string;
    authenticate_user: {
        username: string;
    }
}

const TASK_SUB = gql`
subscription TaskList {
  worker_task(order_by: {created_at: desc}, limit:100) {
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

const TaskPage = () => {
    const {data, loading, error} = useSubscription(TASK_SUB);

    // Display loading overlay while loading
    if (loading) return (
        <div className="fixed top-0 left-0 z-50 w-screen h-screen flex items-center justify-center"
             style={{backgroundColor: 'rgba(255, 255, 255, 0.5)'}}>
            <div className="loader">Loading...</div>
            {/* Consider using a Tailwind-styled spinner */}
        </div>
    );

    // Display error message if an error occurs
    if (error) return <div className="text-red-500">Error :(</div>;

    return (
        <div className="m-4">

            <div className="shadow-xs p-4 bg-white">
                <table className="min-w-full divide-y divide-gray-200 table-auto">
                    <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        {/*<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>*/}
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prompt</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Task</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User
                        </th>
                        {/*<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created*/}
                        {/*    At*/}
                        {/*</th>*/}
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Updated
                            At
                        </th>
                    </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                    {data && data?.worker_task.map((task: Task, index: number) => (
                        <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.id}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.name}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.result_status}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{JSON.stringify(task.parameters?.prompt)}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{JSON.stringify(task.parameters?.llm_task_type)}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.work_type}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.authenticate_user.username}</td>
                            {/*<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.created_at}</td>*/}
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.updated_at}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TaskPage;
