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
  worker_task(order_by: {created_at: desc}, limit:5) {
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
        // <div className="m-4">
        //
        //     <div className="shadow-xs p-4 bg-white">
        //         <table className="min-w-full divide-y divide-gray-200 table-auto">
        //             <thead className="bg-gray-50">
        //             <tr>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
        //                 {/*<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>*/}
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prompt</th>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Task</th>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User
        //                 </th>
        //                 {/*<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created*/}
        //                 {/*    At*/}
        //                 {/*</th>*/}
        //                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Updated
        //                     At
        //                 </th>
        //             </tr>
        //             </thead>
        //             <tbody className="bg-white divide-y divide-gray-200">
        //             {data && data?.worker_task.map((task: Task, index: number) => (
        //                 <tr key={index}>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.id}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.name}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.result_status}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{JSON.stringify(task.parameters?.prompt)}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{JSON.stringify(task.parameters?.llm_task_type)}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.work_type}</td>
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.authenticate_user.username}</td>
        //                     {/*<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.created_at}</td>*/}
        //                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.updated_at}</td>
        //                 </tr>
        //             ))}
        //             </tbody>
        //         </table>
        //     </div>
        // </div>
        <div className="container mx-auto px-4 py-8">
            {/* Cards for task states */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                {/* Pending Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-red-600 hover:bg-red-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">12</p>
                    <p className="text-white text-xl">Pending</p>
                </div>
                {/* Started Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-yellow-600 hover:bg-yellow-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">5</p>
                    <p className="text-white text-xl">Started</p>
                </div>
                {/* Success Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-green-600 hover:bg-green-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">20</p>
                    <p className="text-white text-xl">Success</p>
                </div>
                {/* Failed Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-gray-600 hover:bg-gray-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">3</p>
                    <p className="text-white text-xl">Failed</p>
                </div>
            </div>

            {/* Task Details Table */}
            <div className="overflow-x-auto">
                <table className="w-full whitespace-no-wrap">
                    <thead>
                    <tr className="text-xs font-semibold tracking-wide text-left text-gray-500 uppercase border-b bg-gray-50">
                        <th className="px-4 py-3">Task ID</th>
                        <th className="px-4 py-3">Description</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3">Created At</th>
                        <th className="px-4 py-3">Actions</th>
                    </tr>
                    </thead>
                    <tbody className="bg-white divide-y">
                    {/* Example row */}
                    <tr className="text-gray-700">
                        <td className="px-4 py-3 text-sm">1</td>
                        <td className="px-4 py-3 text-sm">Implement login feature</td>
                        <td className="px-4 py-3 text-sm">Pending</td>
                        <td className="px-4 py-3 text-sm">2024-04-01</td>
                        <td className="px-4 py-3">
                            <div className="flex items-center space-x-4 text-sm">
                                <button
                                    className="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-purple-600 rounded-lg dark:text-gray-400 focus:outline-none focus:shadow-outline-gray"
                                    aria-label="Edit">
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                        <path
                                            d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z"></path>
                                        <path fillRule="evenodd"
                                              d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
                                              clipRule="evenodd"></path>
                                    </svg>
                                </button>
                            </div>
                        </td>
                    </tr>
                    {/* Repeat rows as needed */}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TaskPage;
