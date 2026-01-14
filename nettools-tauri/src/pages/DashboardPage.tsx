import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { useStore } from '@/store'
import { TOOLS, getToolsByCategory } from '@/types/tools'
import { 
  Radar, Network, Globe, Route, Table2, Calculator, 
  Gauge, Search, ShieldCheck, Fingerprint, Hash, Key, Send, Shield,
  ArrowRight, Star, Clock, Activity
} from 'lucide-react'

// Map icon names to components
const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Radar, Network, Globe, Route, Table2, Calculator,
  Gauge, Search, ShieldCheck, Fingerprint, Hash, Key, Send, Shield,
}

export function DashboardPage() {
  const { setActiveTool, favorites, enabledTools } = useStore()
  
  const quickAccessTools = TOOLS.filter(
    tool => favorites.includes(tool.id) || ['scanner', 'portscan', 'dns', 'traceroute'].includes(tool.id)
  ).slice(0, 6)

  const scanningTools = getToolsByCategory('scanning').filter(t => enabledTools.includes(t.id))
  const networkTools = getToolsByCategory('network').filter(t => enabledTools.includes(t.id))

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary mb-2">
          Willkommen bei NetTools
        </h1>
        <p className="text-text-secondary">
          Professionelle Netzwerk-Utilities für Windows
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-accent-blue/20">
                <Radar className="w-6 h-6 text-accent-blue" />
              </div>
              <div>
                <p className="text-sm text-text-muted">Scanning Tools</p>
                <p className="text-2xl font-bold text-text-primary">{scanningTools.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-accent-green/20">
                <Network className="w-6 h-6 text-accent-green" />
              </div>
              <div>
                <p className="text-sm text-text-muted">Netzwerk Tools</p>
                <p className="text-2xl font-bold text-text-primary">{networkTools.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-accent-yellow/20">
                <Star className="w-6 h-6 text-accent-yellow" />
              </div>
              <div>
                <p className="text-sm text-text-muted">Favoriten</p>
                <p className="text-2xl font-bold text-text-primary">{favorites.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-accent-purple/20">
                <Activity className="w-6 h-6 text-accent-purple" />
              </div>
              <div>
                <p className="text-sm text-text-muted">Aktive Tools</p>
                <p className="text-2xl font-bold text-text-primary">{enabledTools.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Access */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-accent-blue" />
            Schnellzugriff
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {quickAccessTools.map((tool) => {
              const Icon = iconMap[tool.icon] || Radar
              return (
                <button
                  key={tool.id}
                  onClick={() => setActiveTool(tool.id)}
                  className="flex flex-col items-center gap-2 p-4 rounded-lg bg-bg-tertiary hover:bg-bg-hover border border-border-default hover:border-accent-blue transition-all group"
                >
                  <div className="p-3 rounded-lg bg-bg-hover group-hover:bg-accent-blue/20 transition-colors">
                    <Icon className="w-6 h-6 text-text-secondary group-hover:text-accent-blue transition-colors" />
                  </div>
                  <span className="text-sm font-medium text-text-primary text-center">
                    {tool.name}
                  </span>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Tool Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scanning Tools */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Radar className="w-5 h-5 text-accent-blue" />
              Scanning
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {scanningTools.map((tool) => {
                const Icon = iconMap[tool.icon] || Radar
                return (
                  <button
                    key={tool.id}
                    onClick={() => setActiveTool(tool.id)}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-bg-hover transition-colors group"
                  >
                    <Icon className="w-5 h-5 text-text-muted group-hover:text-accent-blue transition-colors" />
                    <div className="flex-1 text-left">
                      <p className="font-medium text-text-primary">{tool.name}</p>
                      <p className="text-sm text-text-muted">{tool.description}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Network Tools */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="w-5 h-5 text-accent-green" />
              Netzwerk-Tools
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {networkTools.map((tool) => {
                const Icon = iconMap[tool.icon] || Network
                return (
                  <button
                    key={tool.id}
                    onClick={() => setActiveTool(tool.id)}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-bg-hover transition-colors group"
                  >
                    <Icon className="w-5 h-5 text-text-muted group-hover:text-accent-green transition-colors" />
                    <div className="flex-1 text-left">
                      <p className="font-medium text-text-primary">{tool.name}</p>
                      <p className="text-sm text-text-muted">{tool.description}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer Info */}
      <div className="text-center py-4 border-t border-border-default">
        <p className="text-sm text-text-muted">
          NetTools Professional Suite v1.0.0 • © 2024 frekms
        </p>
        <p className="text-xs text-text-muted mt-1">
          Drücken Sie <kbd className="px-1.5 py-0.5 bg-bg-tertiary rounded">Ctrl+K</kbd> für die Schnellsuche
        </p>
      </div>
    </div>
  )
}
