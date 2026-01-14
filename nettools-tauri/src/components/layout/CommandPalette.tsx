import React, { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { useStore } from '@/store'
import { TOOLS, type ToolId } from '@/types/tools'
import { 
  Search, Star, ArrowRight,
  LayoutDashboard, Radar, Network, Globe, Route, Table2, Calculator,
  Gauge, ShieldCheck, Fingerprint, Hash, Key, Send, Shield, Settings
} from 'lucide-react'

// Icon map
const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard, Radar, Network, Globe, Route, Table2, Calculator,
  Gauge, Search, ShieldCheck, Fingerprint, Hash, Key, Send, Shield, Settings,
}

// Dynamic icon component
function DynamicIcon({ name, className }: { name: string; className?: string }) {
  const IconComponent = iconMap[name]
  if (!IconComponent) return <Radar className={className} />
  return <IconComponent className={className} />
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const { setActiveTool, favorites, enabledTools } = useStore()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const filteredTools = TOOLS.filter(tool => {
    // Always show dashboard and settings
    if (tool.id !== 'dashboard' && tool.id !== 'settings') {
      if (!enabledTools.includes(tool.id)) return false
    }
    
    if (!query) return true
    
    const searchTerms = query.toLowerCase()
    return (
      tool.name.toLowerCase().includes(searchTerms) ||
      tool.description.toLowerCase().includes(searchTerms)
    )
  })

  // Sort: favorites first, then alphabetically
  const sortedTools = [...filteredTools].sort((a, b) => {
    const aIsFavorite = favorites.includes(a.id)
    const bIsFavorite = favorites.includes(b.id)
    if (aIsFavorite && !bIsFavorite) return -1
    if (!aIsFavorite && bIsFavorite) return 1
    return a.name.localeCompare(b.name)
  })

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus()
      setQuery('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => Math.min(prev + 1, sortedTools.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (sortedTools[selectedIndex]) {
            handleSelect(sortedTools[selectedIndex].id)
          }
          break
        case 'Escape':
          e.preventDefault()
          onClose()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selectedIndex, sortedTools, onClose])

  // Scroll selected item into view
  useEffect(() => {
    const list = listRef.current
    if (!list) return

    const selectedElement = list.children[selectedIndex] as HTMLElement
    if (selectedElement) {
      selectedElement.scrollIntoView({ block: 'nearest' })
    }
  }, [selectedIndex])

  const handleSelect = (toolId: ToolId) => {
    setActiveTool(toolId)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Dialog */}
      <div className="relative w-full max-w-lg bg-bg-card border border-border-default rounded-xl shadow-modal overflow-hidden animate-fade-in">
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border-default">
          <Search className="w-5 h-5 text-text-muted shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tool suchen..."
            className="flex-1 bg-transparent text-text-primary placeholder:text-text-muted text-base focus:outline-none"
          />
          <kbd className="px-2 py-0.5 text-xs text-text-muted bg-bg-tertiary rounded">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div 
          ref={listRef}
          className="max-h-[60vh] overflow-y-auto py-2"
        >
          {sortedTools.length === 0 ? (
            <div className="px-4 py-8 text-center text-text-muted">
              Keine Tools gefunden für "{query}"
            </div>
          ) : (
            sortedTools.map((tool, index) => {
              const isFavorite = favorites.includes(tool.id)
              const isSelected = index === selectedIndex

              return (
                <button
                  key={tool.id}
                  onClick={() => handleSelect(tool.id)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-3 transition-colors',
                    isSelected ? 'bg-bg-hover' : 'hover:bg-bg-hover'
                  )}
                >
                  <div className={cn(
                    'flex items-center justify-center w-10 h-10 rounded-lg',
                    isSelected ? 'bg-accent-blue' : 'bg-bg-tertiary'
                  )}>
                    <DynamicIcon 
                      name={tool.icon} 
                      className={cn(
                        'w-5 h-5',
                        isSelected ? 'text-white' : 'text-text-secondary'
                      )} 
                    />
                  </div>
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'font-medium',
                        isSelected ? 'text-text-primary' : 'text-text-secondary'
                      )}>
                        {tool.name}
                      </span>
                      {isFavorite && (
                        <Star className="w-3.5 h-3.5 text-accent-yellow fill-current" />
                      )}
                    </div>
                    <span className="text-sm text-text-muted">
                      {tool.description}
                    </span>
                  </div>
                  {tool.shortcut && (
                    <kbd className="px-2 py-0.5 text-xs text-text-muted bg-bg-tertiary rounded">
                      {tool.shortcut}
                    </kbd>
                  )}
                  {isSelected && (
                    <ArrowRight className="w-4 h-4 text-text-muted" />
                  )}
                </button>
              )
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2 border-t border-border-default bg-bg-tertiary/50">
          <div className="flex items-center gap-4 text-xs text-text-muted">
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-bg-tertiary rounded">↑</kbd>
              <kbd className="px-1 py-0.5 bg-bg-tertiary rounded">↓</kbd>
              Navigation
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-bg-tertiary rounded">↵</kbd>
              Öffnen
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
