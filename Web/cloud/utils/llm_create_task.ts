'use client'
import apiClient from "@/cloud/apiClient";

interface LLMTaskFormData {
    name: string;
    task_type: string;
    prompt: string;
    model_name: string;
    llm_task_type: string;
}

export const llmCreateTask = async (formData: LLMTaskFormData) => {
    const response = await apiClient.post('/queue_task/llm/', formData);
    return response.status === 200;
}

export const llmCustomCreateTask = async (formData: LLMTaskFormData) => {
    const response = await apiClient.post('/queue_task/custom_llm/', formData);
    return response.status === 200;
}