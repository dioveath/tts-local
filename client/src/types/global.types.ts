export interface AudioGenerationRequest {
  engine: 'pyttsx3' | 'kokoro'
  text: string
  engine_options?: Record<string, any> | null
  output_format?: 'mp3' | 'wav'
}

export interface ValidationError {
  loc: (string | number)[]
  msg: string
  type: string
}

export interface TaskSubmissionResponse {
  task_id: string
  status_url: string
}

export interface TaskStatusResponse {
  task_id: string
  status: string
  result?: Record<string, any> | string | null
  error?: string | null
}
