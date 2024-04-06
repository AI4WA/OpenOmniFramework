'use client'
import {useSubscription, gql} from "@apollo/client";
import React, {useState} from 'react';
import {useAppSelector} from "@/store"; // Make sure to import React when using JSX
import LLMTaskAdd from "@/components/LLMTaskAdd";
import LLMTaskUniqueName from "@/components/LLMTaskUniqueName";
import LLMTaskTable from "@/components/LLMTaskTable";


const TASK_PENDING = gql`
subscription OnPending($userId:bigint!){
    pending: worker_task_aggregate(where: {result_status: {_eq: "pending"}, user_id: {_eq: $userId}, work_type: {_in: ["gpu", "cpu"]} }) {
        aggregate {
            count
        }
    }
}
`

const TASK_TOTAL_PENDING = gql`
subscription TotalOnPending{
    totalPending: worker_task_aggregate(where: {result_status: {_eq: "pending"}, work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_TOTAL_SUCCESS = gql`
subscription TotalOnSuccess{
    totalSuccess: worker_task_aggregate(where: {result_status: {_eq: "completed"}, work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_STARTED = gql`
subscription OnStarted($userId:bigint!) {
    started: worker_task_aggregate(where: {result_status: {_eq: "started"}, user_id: {_eq: $userId}, work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_SUCCESS = gql`
subscription OnSuccess($userId:bigint!){
    success: worker_task_aggregate(where: {result_status: {_eq: "completed"},
                                           user_id: {_eq: $userId},
                                           work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_FAILED = gql`
subscription OnFailed($userId:bigint!){
    failed: worker_task_aggregate(where: {result_status: {_eq: "failed"}, 
                                          user_id: {_eq: $userId},
                                          work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_CANCELLED = gql`
subscription OnFailed($userId:bigint!){
    cancelled: worker_task_aggregate(where: {result_status: {_eq: "cancelled"},
                                             user_id: {_eq: $userId},
                                             work_type: {_in: ["gpu", "cpu"]}}) {
        aggregate {
            count
        }
    }
}
`

const TASK_UNIQUE_NAME = gql`
subscription OnUniqueTaskName($userId: bigint!) {
    view_llm_unique_task_name(where: {user_id: {_eq: $userId}}) {
    count
    name
    user_id
    downloadlink(limit: 1, order_by: {created_at: desc}) {
      progress
      download_link
      id
    }
  }
}
`

const GPU_WORKER = gql`
subscription GpuWorker {
  view_live_worker {
    task_type
    recent_update_count
  }
}
`

const TaskPage = () => {
    const [open, setOpen] = useState(false)
    const [uniqueTaskNameOpen, setUniqueTaskOpen] = useState(false)
    const userId = useAppSelector(state => state.auth.authState.userId)


    const {
        data: totalPendingData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_TOTAL_PENDING)
    const {
        data: pendingData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_PENDING, {
        variables: {userId}
    })
    const {
        data: startedData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_STARTED, {
        variables: {userId}
    })

    const {
        data: successData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_SUCCESS, {
        variables: {userId}
    })
    const {
        data: failedData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_FAILED, {
        variables: {userId}
    })

    const {
        data: cancelledData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_CANCELLED, {
        variables: {userId}
    })

    const {
        data: totalSuccessData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_TOTAL_SUCCESS)


    const {
        data: gpuWorkerData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(GPU_WORKER)


    const {
        data: uniqueTaskNameData,
        // loading: pendingLoading,
        // error: errorLoading
    } = useSubscription(TASK_UNIQUE_NAME, {
        variables: {userId}
    })


    return (
        <div className="container mx-auto px-4 py-8 w-screen h-screen ">
            {/* Cards for task states */}
            <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {/* GPU vs CPU Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-purple-600 hover:bg-purple-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{gpuWorkerData?.view_live_worker?.filter((worker: {
                        task_type: string,
                        recent_update_count: number;
                    }) => worker.task_type === 'gpu')?.[0]?.recent_update_count || 0} vs {gpuWorkerData?.view_live_worker?.filter((worker: {
                        task_type: string,
                        recent_update_count: number;
                    }) => worker.task_type === 'cpu')?.[0]?.recent_update_count || 0}</p>
                    <p className="text-white text-xl">Live Worker (GPU vs CPU)</p>
                </div>
                {/* Total Pending Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-yellow-600 hover:bg-yellow-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{totalPendingData?.totalPending?.aggregate?.count}</p>
                    <p className="text-white text-xl">Total Pending</p>
                </div>
                {/* Your Pending Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-blue-600 hover:bg-blue-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{pendingData?.pending?.aggregate?.count}</p>
                    <p className="text-white text-xl">Your Pending</p>
                </div>
                {/* Started Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-blue-600 hover:bg-blue-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{startedData?.started?.aggregate?.count}</p>
                    <p className="text-white text-xl">Started</p>
                </div>
                {/* Total Success Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-green-600 hover:bg-green-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{totalSuccessData?.totalSuccess?.aggregate?.count}</p>
                    <p className="text-white text-xl">Total Success</p>
                </div>
                {/* Success Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-green-600 hover:bg-green-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{successData?.success?.aggregate?.count}</p>
                    <p className="text-white text-xl">Success</p>
                </div>
                {/* Failed Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-gray-600 hover:bg-gray-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{failedData?.failed?.aggregate?.count}</p>
                    <p className="text-white text-xl">Failed</p>
                </div>
                {/* Cancelled Tasks Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-gray-600 hover:bg-gray-700 transition-colors">
                    <p className="text-white text-3xl font-semibold">{cancelledData?.cancelled?.aggregate?.count}</p>
                    <p className="text-white text-xl">Cancelled</p>
                </div>
                {/* Add Task Card */}
                <div
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-teal-500 hover:bg-teal-600 transition-colors">
                    <p className="text-white text-xl">Add task</p>
                    <button
                        className="mt-4 flex items-center justify-center bg-white text-teal-600 hover:text-teal-700 font-bold py-2 px-4 rounded-full transition-colors"
                        onClick={() => setOpen(true)}
                        aria-label="Add task">
                        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="2"
                             fill="none" strokeLinecap="round" strokeLinejoin="round"
                             className="text-teal-600 hover:text-teal-700">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
                </div>
                {/* Add Task Card */}
                <div
                    onClick={() => setUniqueTaskOpen(true)}
                    className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-teal-500 hover:bg-teal-600 transition-colors">
                    <p className="text-white text-3xl font-semibold">{uniqueTaskNameData?.view_llm_unique_task_name.length}</p>
                    <p className="text-white text-xl">Unique Task Names</p>
                </div>
            </div>
            <LLMTaskAdd open={open} onClose={() => setOpen(false)}/>
            <LLMTaskUniqueName open={uniqueTaskNameOpen}
                               onClose={() => setUniqueTaskOpen(false)}
                               tasks={uniqueTaskNameData?.view_llm_unique_task_name || []}/>

            <LLMTaskTable/>
        </div>
    );
};

export default TaskPage;
