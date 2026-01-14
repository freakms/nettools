import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, Checkbox, Button, Alert } from '@/components/ui'
import { useStore } from '@/store'
import { TOOLS, TOOL_CATEGORIES } from '@/types/tools'
import { Settings, Save, RotateCcw, Info } from 'lucide-react'
import * as Icons from 'lucide-react'

// Dynamic icon component
function DynamicIcon({ name, className }: { name: string; className?: string }) {
  const IconComponent = (Icons as Record<string, React.ComponentType<{ className?: string }>>)[name]
  if (!IconComponent) return null
  return <IconComponent className={className} />
}

export function SettingsPage() {
  const { enabledTools, toggleTool, setEnabledTools } = useStore()
  const [hasChanges, setHasChanges] = React.useState(false)

  const toolsByCategory = TOOL_CATEGORIES.filter(
    cat => cat.id !== 'dashboard' && cat.id !== 'settings'
  ).map(category => ({
    ...category,
    tools: TOOLS.filter(tool => tool.category === category.id),
  }))

  const allToolIds = TOOLS.filter(
    t => t.id !== 'dashboard' && t.id !== 'settings'
  ).map(t => t.id)

  const handleToggle = (toolId: string) => {
    toggleTool(toolId as never)
    setHasChanges(true)
  }

  const handleSelectAll = () => {
    setEnabledTools(allToolIds as never)
    setHasChanges(true)
  }

  const handleDeselectAll = () => {
    setEnabledTools([])
    setHasChanges(true)
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
            <Settings className="w-7 h-7 text-accent-blue" />
            Einstellungen
          </h1>
          <p className="text-text-secondary mt-1">
            Konfigurieren Sie die Anwendung nach Ihren Bedürfnissen
          </p>
        </div>
      </div>

      {/* Tool Visibility Settings */}
      <Card variant="bordered">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Sichtbare Tools</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={handleSelectAll}>
                Alle aktivieren
              </Button>
              <Button variant="ghost" size="sm" onClick={handleDeselectAll}>
                Alle deaktivieren
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Alert variant="info" className="mb-6">
            <Info className="w-4 h-4" />
            Deaktivierte Tools werden aus der Sidebar und dem Dashboard ausgeblendet.
            Dashboard und Einstellungen sind immer sichtbar.
          </Alert>

          <div className="space-y-6">
            {toolsByCategory.map(category => (
              <div key={category.id}>
                <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
                  {category.name}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {category.tools.map(tool => {
                    const isEnabled = enabledTools.includes(tool.id)
                    return (
                      <div
                        key={tool.id}
                        className={`
                          flex items-center gap-3 p-3 rounded-lg border transition-colors cursor-pointer
                          ${isEnabled 
                            ? 'bg-bg-tertiary border-accent-blue/50' 
                            : 'bg-bg-card border-border-default opacity-60'
                          }
                        `}
                        onClick={() => handleToggle(tool.id)}
                      >
                        <Checkbox
                          checked={isEnabled}
                          onChange={() => handleToggle(tool.id)}
                        />
                        <DynamicIcon 
                          name={tool.icon} 
                          className={`w-5 h-5 ${isEnabled ? 'text-accent-blue' : 'text-text-muted'}`} 
                        />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary truncate">{tool.name}</p>
                          <p className="text-xs text-text-muted truncate">{tool.description}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* App Info */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Über NetTools</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-text-muted">Version</p>
                <p className="text-text-primary font-medium">1.0.0</p>
              </div>
              <div>
                <p className="text-text-muted">Build</p>
                <p className="text-text-primary font-medium">Tauri + React</p>
              </div>
              <div>
                <p className="text-text-muted">Plattform</p>
                <p className="text-text-primary font-medium">Windows</p>
              </div>
              <div>
                <p className="text-text-muted">Entwickler</p>
                <p className="text-text-primary font-medium">frekms</p>
              </div>
            </div>
            
            <div className="pt-4 border-t border-border-default">
              <p className="text-sm text-text-muted">
                NetTools Professional Suite - Eine umfassende Sammlung von Netzwerk-Utilities
                für IT-Administratoren und Netzwerk-Profis.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Keyboard Shortcuts */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Tastenkürzel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { keys: 'Ctrl + K', action: 'Schnellsuche öffnen' },
              { keys: 'Ctrl + 1', action: 'Dashboard' },
              { keys: 'Ctrl + 2', action: 'IPv4 Scanner' },
              { keys: 'Ctrl + 3', action: 'Port Scanner' },
              { keys: 'Ctrl + 4', action: 'DNS Lookup' },
              { keys: 'Ctrl + 5', action: 'Traceroute' },
              { keys: 'Ctrl + ,', action: 'Einstellungen' },
              { keys: 'Ctrl + Q', action: 'Beenden' },
            ].map(shortcut => (
              <div key={shortcut.keys} className="flex items-center justify-between p-2 rounded bg-bg-tertiary">
                <span className="text-sm text-text-secondary">{shortcut.action}</span>
                <kbd className="px-2 py-1 text-xs bg-bg-hover rounded font-mono">
                  {shortcut.keys}
                </kbd>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
