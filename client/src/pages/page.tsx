'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { useState } from 'react'
import { RotateCw } from 'lucide-react'
import { ApiService } from '@/services/api-service'
import { AudioGenerationRequest } from '@/types/global.types'
import GenerationCardItem from '@/components/GenerationCardItem'
import AppSidebar from '@/components/app-sidebar'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@radix-ui/react-separator'
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage
} from '@/components/ui/breadcrumb'
import { StorageService } from '@/services/storage-service'

const FormSchema = z.object({
  text: z
    .string()
    .min(1, {
      message: 'Speak some words, my child!!!'
    })
    .max(20000, {
      message: 'I cant speak longer than 20000 characters.'
    })
})

export function HomePage() {
  const [isLoading, setLoading] = useState(false)
  const [lastGeneratedId, setLastGeneratedId] = useState<string | null>(null)
  const [open, setOpen] = useState(true)

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema)
  })

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    try {
      setLoading(true)
      const request: AudioGenerationRequest = {
        text: data.text,
        engine: 'kokoro'
      }

      const statusResponse = await ApiService.generateAudio(request)
      StorageService.addGeneration({
        id: statusResponse.task_id,
        name: data.text.substring(0, 20) + '...',
        createdAt: new Date().toISOString(),
        url: ApiService.getDownloadAudioUrl(statusResponse.task_id)
      })
      toast.success(`You submitted the following values: ${JSON.stringify(data)}`)
      setLastGeneratedId(statusResponse.task_id)
    } catch (error: any) {
      toast.error('Error: ' + error?.message || "Couldn't generate audio!")
    } finally {
      setLoading(false)
    }
  }

  return (
    <SidebarProvider open={open} onOpenChange={setOpen}>
      <AppSidebar items={[]} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">Building Your Application</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Data Fetching</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="container mx-auto mt-10 flex flex-col space-y-8 justify-center items-center">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
              <FormField
                control={form.control}
                name="text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel> Narration/Script </FormLabel>
                    <FormControl>
                      <Textarea placeholder="Once upon a time" className="resize-none h-40" {...field} />
                    </FormControl>
                    <FormDescription>Provide the narration to generate an audio</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">
                {isLoading ? <RotateCw className="mr-2 h-4 w-4 animate-spin" /> : 'Generate Audio'}
              </Button>
            </form>
          </Form>
          {lastGeneratedId && (
            <div className="w-2/3">
              <GenerationCardItem generationId={lastGeneratedId} taskId={lastGeneratedId} />
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
