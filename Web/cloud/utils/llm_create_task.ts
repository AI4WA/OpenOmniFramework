'use client'
import apiClient from "@/cloud/apiClient";


export const llmCreateTask = async (formData) => {
    const response = await apiClient.post('/queue_task/llm/', formData);
    return response.status === 200;
}