import React from 'react'
import { cn } from '@/lib/utils'
import { useStore } from '@/store'
import { TOOLS, TOOL_CATEGORIES } from '@/types/tools'
import { 
  Star, ChevronDown, ChevronRight,
  LayoutDashboard, Radar, Network, Globe, Route, Table2, Calculator,
  Gauge, Search, ShieldCheck, Fingerprint, Hash, Key, Send, Shield, Settings
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

interface SidebarProps {
  collapsed?: boolean
  onToggle?: () => void
}

export function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const { activeTool, setActiveTool, favorites, toggleFavorite, enabledTools } = useStore()
  const [expandedCategories, setExpandedCategories] = React.useState<string[]>(['scanning', 'network'])

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const filteredTools = TOOLS.filter(tool => 
    tool.id === 'dashboard' || 
    tool.id === 'settings' || 
    enabledTools.includes(tool.id)
  )

  const favoriteTools = filteredTools.filter(tool => favorites.includes(tool.id))

  const renderToolButton = (tool: typeof TOOLS[0], showFavorite = true) => {
    const isActive = activeTool === tool.id
    const isFavorite = favorites.includes(tool.id)

    return (
      <button
        key={tool.id}
        onClick={() => setActiveTool(tool.id)}
        className={cn(
          'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 group',
          isActive
            ? 'bg-accent-blue text-white'
            : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
        )}
        title={collapsed ? tool.name : undefined}
      >
        <DynamicIcon 
          name={tool.icon} 
          className={cn('w-5 h-5 shrink-0', isActive ? 'text-white' : 'text-text-muted group-hover:text-text-primary')} 
        />
        {!collapsed && (
          <>
            <span className="flex-1 text-left truncate">{tool.name}</span>
            {showFavorite && tool.id !== 'dashboard' && tool.id !== 'settings' && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleFavorite(tool.id)
                }}
                className={cn(
                  'p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity',
                  isFavorite ? 'opacity-100 text-accent-yellow' : 'hover:text-accent-yellow'
                )}
              >
                <Star className={cn('w-3.5 h-3.5', isFavorite && 'fill-current')} />
              </button>
            )}
            {tool.shortcut && (
              <span className="text-xs text-text-muted opacity-0 group-hover:opacity-100 transition-opacity">
                {tool.shortcut}
              </span>
            )}
          </>
        )}
      </button>
    )
  }

  return (
    <aside
      className={cn(
        'flex flex-col bg-bg-secondary border-r border-border-default transition-all duration-300 h-full',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-border-default">
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-bold text-text-primary truncate">NetTools</h1>
            <p className="text-xs text-text-muted truncate">Professional Suite</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-bg-hover text-text-muted hover:text-text-primary transition-colors"
          title={collapsed ? 'Sidebar erweitern' : 'Sidebar einklappen'}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2 px-2">
        {/* Dashboard - always visible */}
        <div className="mb-2">
          {renderToolButton(TOOLS.find(t => t.id === 'dashboard')!, false)}
        </div>

        {/* Favorites Section */}
        {!collapsed && favoriteTools.length > 0 && (
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2">
              <Star className="w-3 h-3" />
              Favoriten
            </div>
            <div className="space-y-0.5">
              {favoriteTools.map(tool => renderToolButton(tool, false))}
            </div>
          </div>
        )}

        {/* Tool Categories */}
        {TOOL_CATEGORIES.filter(cat => cat.id !== 'dashboard' && cat.id !== 'settings').map(category => {
          const categoryTools = filteredTools.filter(
            tool => tool.category === category.id && !favorites.includes(tool.id)
          )
          if (categoryTools.length === 0) return null

          const isExpanded = expandedCategories.includes(category.id)

          return (
            <div key={category.id} className="mb-2">
              {!collapsed && (
                <button
                  onClick={() => toggleCategory(category.id)}
                  className="w-full px-3 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2 hover:text-text-secondary transition-colors"
                >
                  {isExpanded ? (
                    <ChevronDown className="w-3 h-3" />
                  ) : (
                    <ChevronRight className="w-3 h-3" />
                  )}
                  {category.name}
                </button>
              )}
              {(collapsed || isExpanded) && (
                <div className="space-y-0.5">
                  {categoryTools.map(tool => renderToolButton(tool))}
                </div>
              )}
            </div>
          )
        })}
      </nav>

      {/* Footer - Settings */}
      <div className="border-t border-border-default p-2">
        {renderToolButton(TOOLS.find(t => t.id === 'settings')!, false)}
      </div>

      {/* Copyright */}
      {!collapsed && (
        <div className="px-4 py-3 border-t border-border-default">
          <p className="text-xs text-text-muted text-center">
            © 2024 frekms
          </p>
        </div>
      )}
    </aside>
  )
}
