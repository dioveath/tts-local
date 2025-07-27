'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { Resolver, useForm, useWatch } from 'react-hook-form'
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'

const BaseSchema = z.object({
  text: z
    .string()
    .min(1, {
      message: 'Speak some words, my child!!!'
    })
    .max(20000, {
      message: 'I cant speak longer than 20000 characters.'
    })
})

const FormSchema = z.discriminatedUnion('engine', [
  BaseSchema.extend({
    engine: z.literal('kokoro'),
    engine_options: z.object({
      voice: z.enum(['am_adam', 'am_michael', 'af_bella']).default('am_adam'),
      speed: z.number().min(0.5).max(2).default(1)
    })
  }),
  BaseSchema.extend({
    engine: z.literal('chatterbox'),
    engine_options: z.object({
      voice: z.enum(['arnold', 'edgar', 'elias', 'hero']).default('arnold'),
      exaggeration: z.number().min(0.25).max(2).default(0.5),
      cfg_weight: z.number().min(0.2).max(1).default(0.3),
      temperature: z.number().min(0.05).max(5).default(0.8)
    })
  })
])

export function HomePage() {
  const [isLoading, setLoading] = useState(false)
  const [lastGeneratedId, setLastGeneratedId] = useState<string | null>(null)
  const [open, setOpen] = useState(true)

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema) as Resolver<z.infer<typeof FormSchema>>,
    defaultValues: {
      text: 'Welcome to the TTS Local project',
      engine: 'kokoro',
      engine_options: {
        voice: 'am_adam',
        speed: 1
      }
    }
  })

  const selectedEngine = useWatch({
    control: form.control,
    name: 'engine'
  })

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    try {
      setLoading(true)
      const request: AudioGenerationRequest = {
        text: data.text,
        engine: data.engine,
        engine_options: data.engine_options
      }

      const statusResponse = await ApiService.generateAudio(request)
      StorageService.addGeneration({
        id: statusResponse.task_id,
        name: data.text.substring(0, 20) + '...',
        createdAt: new Date().toISOString(),
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

              <FormField
                control={form.control}
                name='engine'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel> Engine </FormLabel>
                    <FormControl>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an engine" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="kokoro">Kokoro</SelectItem>
                          <SelectItem value="chatterbox">Chatterbox</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormDescription>Select the engine to use</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              { selectedEngine === "kokoro" && (
                <>
                <FormField
                  control={form.control}
                  name="engine_options.voice"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> Voice </FormLabel>
                      <FormControl>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a voice" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="am_adam">Adam</SelectItem>
                            <SelectItem value="am_michael">Michael</SelectItem>
                            <SelectItem value="af_bella">Bella</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormDescription>Select the voice to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="engine_options.speed"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> Speed: {field.value} </FormLabel>
                      <FormControl>
                        <Slider defaultValue={[field.value]} min={0.5} max={2} step={0.1} onValueChange={(value: number[]) => field.onChange(value[0])} />
                      </FormControl>
                      <FormDescription>Select the speed to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                </>
              )}

              { selectedEngine === "chatterbox" && (
                <>
                <FormField
                  control={form.control}
                  name="engine_options.voice"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> Voice </FormLabel>
                      <FormControl>
                        <Select onValueChange={field.onChange} defaultValue={"arnold"}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a voice" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="arnold">Arnold</SelectItem>
                            <SelectItem value="edgar">Edgar</SelectItem>
                            <SelectItem value="elias">Elias</SelectItem>
                            <SelectItem value="hero">Hero</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormDescription>Select the voice to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="engine_options.exaggeration"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> Exaggeration: {field.value} </FormLabel>
                      <FormControl>
                        <Slider defaultValue={[0.5]} min={0.25} max={2} step={0.1} onValueChange={(value: number[]) => field.onChange(value[0])} />
                      </FormControl>
                      <FormDescription>Select the exaggeration to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="engine_options.cfg_weight"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> CFG Weight: {field.value} </FormLabel>
                      <FormControl>
                        <Slider defaultValue={[0.3]} min={0.2} max={1} step={0.05} onValueChange={(value: number[]) => field.onChange(value[0])} />
                      </FormControl>
                      <FormDescription>Select the cfg weight to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="engine_options.temperature"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel> Temperature: {field.value} </FormLabel>
                      <FormControl>
                        <Slider defaultValue={[0.8]} min={0.05} max={5} step={0.1} onValueChange={(value: number[]) => field.onChange(value[0])} />
                      </FormControl>
                      <FormDescription>Select the temperature to use</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                </>
              )}

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
