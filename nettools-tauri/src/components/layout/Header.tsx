import React from 'react'
import { cn } from '@/lib/utils'
import { useStore } from '@/store'
import { getToolById } from '@/types/tools'
import { Search, Command, Bell } from 'lucide-react'

interface HeaderProps {
  onOpenCommandPalette?: () => void
}

export function Header({ onOpenCommandPalette }: HeaderProps) {
  const { activeTool } = useStore()
  const currentTool = getToolById(activeTool)

  return (
    <header className="flex items-center justify-between px-6 py-3 bg-bg-secondary border-b border-border-default">
      {/* Current Tool Info */}
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-semibold text-text-primary">
          {currentTool?.name || 'Dashboard'}
        </h2>
        <span className="text-sm text-text-muted hidden sm:inline">
          {currentTool?.description}
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Quick Search / Command Palette */}
        <button
          onClick={onOpenCommandPalette}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg',
            'bg-bg-tertiary border border-border-default',
            'text-text-muted hover:text-text-primary hover:border-border-light',
            'transition-colors'
          )}
        >
          <Search className="w-4 h-4" />
          <span className="text-sm hidden md:inline">Suchen...</span>
          <kbd className="hidden md:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-xs bg-bg-hover rounded">
            <Command className="w-3 h-3" />
            <span>K</span>
          </kbd>
        </button>

        {/* Notifications (placeholder) */}
        <button
          className={cn(
            'p-2 rounded-lg',
            'text-text-muted hover:text-text-primary hover:bg-bg-hover',
            'transition-colors relative'
          )}
        >
          <Bell className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
