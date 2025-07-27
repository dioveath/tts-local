import { AudioGenerationRequest, TaskStatusResponse, TaskSubmissionResponse } from '@/types/global.types'
import axios, { AxiosError } from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4100'

console.log('Were using api here:', API_URL)

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Define a type for API error responses from FastAPI (optional but helpful)
interface ApiErrorDetail {
  detail: string
}

// --- API Functions with Types ---
export const generateAudio = async (request: AudioGenerationRequest): Promise<TaskSubmissionResponse> => {
  const response = await apiClient.post<TaskSubmissionResponse>('/generate/audio', request)
  return response.data
}

export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await apiClient.get<TaskStatusResponse>(`/tasks/${taskId}`)
  return response.data
}

export const abortTask = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await apiClient.delete<TaskStatusResponse>(`tasks/${taskId}`)
  return response.data
}

export const getDownloadAudioUrl = (taskId: string) => {
  return `${API_URL}/audio/${taskId}`
}

// --- Error Handling ---
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorDetail | any>) => {
    let errorMessage = 'An unexpected error occurred.'
    if (error.response) {
      // Error response from server
      console.error('API Error Response:', error.response.data)
      // Try to get FastAPI's detail message
      errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`
    } else if (error.request) {
      // Request made but no response received
      console.error('API Error Request:', error.request)
      errorMessage = 'Network error: No response received from server.'
    } else {
      // Error setting up the request
      console.error('API Error Message:', error.message)
      errorMessage = `Request setup error: ${error.message}`
    }

    return Promise.reject(new Error(errorMessage))
  }
)

export default apiClient
