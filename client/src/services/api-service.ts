import { abortTask, generateAudio, getDownloadAudioUrl, getTaskStatus } from '@/services/api'
import { AudioGenerationRequest, TaskStatusResponse, TaskSubmissionResponse } from '@/types/global.types'

export const ApiService = {
  generateAudio: async (request: AudioGenerationRequest): Promise<TaskSubmissionResponse> => {
    try {
      const response = await generateAudio(request)
      return response
    } catch (error) {
      throw new Error('Failed to generate audio')
    }
  },
  getTaskStatus: async (taskId: string): Promise<TaskStatusResponse> => {
    try {
      const response = await getTaskStatus(taskId)
      return response
    } catch (error) {
      throw new Error('Failed to get task status')
    }
  },
  abortTask: async (taskId: string): Promise<TaskStatusResponse> => {
    try {
      const response = await abortTask(taskId)
      return response
    } catch (error) {
      throw new Error('Failed to abort task')
    }
  },
  getDownloadAudioUrl: (taskId: string) => {
    return getDownloadAudioUrl(taskId)
  }
}
