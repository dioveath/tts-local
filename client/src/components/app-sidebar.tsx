import React from 'react'
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarFooter,
  SidebarMenuButton
} from '@/components/ui/sidebar'
import { ProjectSwitcher } from './project-switcher'
import { AudioWaveform, Command, GalleryVerticalEnd, Home } from 'lucide-react'
import { NavMain } from './nav-main'
import { NavGenerations } from './nav-generations'
import { ModeToggle } from './mode-toggle'

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
    url: '#',
    icon: Home
  }
]

const generations = [
  {
    name: 'Generation 1',
    url: '#',
    emoji: '1'
  },
  {
    name: 'Generation 2',
    url: '#',
    emoji: '2'
  },
  {
    name: 'Generation 3',
    url: '#',
    emoji: '3'
  }
]

const AppSidebar: React.FC<AppSidebarProps> = ({ items = [] }) => {
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
