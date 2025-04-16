'use client'

import { ArrowUpRight, Download, Link, MoreHorizontal, StarOff, Trash2 } from 'lucide-react'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar
} from '@/components/ui/sidebar'
import { Generation, StorageService } from '@/services/storage-service'

export function NavGenerations({ generations }: { generations: Generation[] }) {
  const { isMobile } = useSidebar()

  const handleDelete = (id: string) => {
    StorageService.removeGeneration(id)
    // Refresh the page to update the UI
    window.location.reload()
  }

  const handleCopy = (url: string) => {
    navigator.clipboard.writeText(url)
  }

  const handleDownload = (url: string) => {
    window.open(url, '_blank')
  }

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Generations</SidebarGroupLabel>
      <SidebarMenu>
        {generations.map((item: Generation) => (
          <SidebarMenuItem key={item.name}>
            <SidebarMenuButton>
              <span>{item.name}</span>
            </SidebarMenuButton>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuAction showOnHover>
                  <MoreHorizontal />
                  <span className="sr-only">More</span>
                </SidebarMenuAction>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-56 rounded-lg"
                side={isMobile ? 'bottom' : 'right'}
                align={isMobile ? 'end' : 'start'}
              >
                <DropdownMenuItem onClick={() => handleDownload(item.url)}>
                  <Download className="text-muted-foreground" />
                  <span>Download</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleCopy(item.url)}>
                  <Link className="text-muted-foreground" />
                  <span>Copy Link</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleDelete(item.id)}>
                  <Trash2 className="text-muted-foreground" />
                  <span>Delete</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        ))}
        <SidebarMenuItem>
          <SidebarMenuButton className="text-sidebar-foreground/70">
            <MoreHorizontal />
            <span>More</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarGroup>
  )
}
