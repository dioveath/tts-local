export interface AudioGenerationRequest {
  engine: 'kokoro' | 'chatterbox'
  text: string
  engine_options?: Record<string, any> | null
  output_format?: 'wav'
  caption_settings?: CaptionSettings
  webhook_url?: string
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
  result?: any
  error?: string | null
}


export interface CaptionSettings {
    max_line_count: number
    max_line_length: number
    font_name: string
    font_size: number
    primary_colour: string
    secondary_colour: string
    outline_colour: string
    back_colour: string
    bold: number
    italic: number
    underline: number
    strikeout: number
    outline: number
    border_style: number
    alignment: number
    playres_x: number
    playres_y: number
    timer: number  
}