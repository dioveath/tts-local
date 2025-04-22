import React from 'react'
import { Sidebar, SidebarHeader, SidebarContent, SidebarFooter } from '@/components/ui/sidebar'
import { ProjectSwitcher } from './project-switcher'
import { AudioWaveform, Command, GalleryVerticalEnd, Home } from 'lucide-react'
import { NavMain } from './nav-main'
import { NavGenerations } from './nav-generations'
import { ModeToggle } from './mode-toggle'
import { StorageService } from '@/services/storage-service'

interface AppSidebarProps {
  items?: string[]
}

const projects = [
  {
    name: 'Project 1',
    logo: GalleryVerticalEnd,
    plan: 'Free'
  },
  {
    name: 'Project 2',
    logo: AudioWaveform,
    plan: 'Free'
  },
  {
    name: 'Project 3',
    logo: Command,
    plan: 'Free'
  }
]

const pages = [
  {
    title: 'Home',
    url: '/',
    icon: Home
  }
]

const AppSidebar: React.FC<AppSidebarProps> = () => {
  const generations = StorageService.getGenerations()

  return (
    <Sidebar variant="inset" collapsible="icon">
      <SidebarHeader>
        <ProjectSwitcher projects={projects} />
        <NavMain items={pages} />
      </SidebarHeader>
      <SidebarContent className="overflow-y-auto flex-1">
        <NavGenerations generations={generations} />
      </SidebarContent>
      <SidebarFooter>
        <div className="w-full flex justify-end">
          <ModeToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
