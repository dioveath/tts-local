import React, { useEffect, useState } from 'react'
import { ApiService } from '@/services/api-service'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'
import { StorageService } from '@/services/storage-service'

interface GenerationCardItemProps {
  generationId: string
  taskId: string
}

type TaskStatus = 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | string

const GenerationCardItem: React.FC<GenerationCardItemProps> = ({ generationId, taskId }) => {
  const [status, setStatus] = useState<TaskStatus>('PENDING')
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout
    let cancelled = false
    setLoading(true)
    setError(null)

    const fetchStatus = async () => {
      try {
        const response = await ApiService.getTaskStatus(taskId)
        if (!cancelled) {
          setStatus(response.status)
          if (response.status === 'SUCCESS') {
            // const url = ApiService.getDownloadAudioUrl(taskId)
            const url = response.result?.output_url
            setAudioUrl(url)
            const currentGeneration = StorageService.getGenerations().find((g) => g.id === generationId)
            if (currentGeneration) {
              StorageService.updateGeneration({
                ...currentGeneration,
                url,
              })
            }
            setLoading(false)
            clearInterval(interval)
          } else if (response.status === 'FAILED') {
            setLoading(false)
            clearInterval(interval)
          }
        }
      } catch (err) {
        setError('Failed to fetch status')
        setLoading(false)
        clearInterval(interval)
      }
    }

    fetchStatus()
    interval = setInterval(fetchStatus, 2000) // Poll every 2 seconds

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [taskId])

  return (
    <Card className="w-full mx-auto my-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>Audio Generation</span>
          {status === 'SUCCESS' && <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">Ready</span>}
          {status === 'FAILURE' && <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-700">Failed</span>}
          {(status === 'PENDING' || status === 'PROCESSING') && (
            <span className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">{status}</span>
          )}
        </CardTitle>
        <CardDescription>Track the status and download your generated audio.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-col gap-1 text-sm">
          <div>
            <span className="font-medium text-muted-foreground">Generation ID:</span> {generationId}
          </div>
          <div>
            <span className="font-medium text-muted-foreground">Task ID:</span> {taskId}
          </div>
          <div>
            <span className="font-medium text-muted-foreground">Status:</span> {status}
          </div>
        </div>
        <div>
          {status === 'SUCCESS' && audioUrl && (
            <>
              <audio controls src={audioUrl} className="w-full rounded shadow" />
              <div className="mt-2 flex gap-2">
                <Button asChild variant="outline" size="sm">
                  <a href={audioUrl} download className="flex items-center gap-1">
                    <Download className="w-4 h-4" /> Download Audio
                  </a>
                </Button>
              </div>
            </>
          )}
          {status !== 'SUCCESS' && <audio controls className="w-full rounded opacity-50" />}
        </div>
        {loading && <div className="text-xs text-muted-foreground">Loading...</div>}
        {error && <div className="text-xs text-red-600">{error}</div>}
      </CardContent>
      <CardFooter className="justify-end">{/* Optionally, add more actions here */}</CardFooter>
    </Card>
  )
}

export default GenerationCardItem
