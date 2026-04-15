import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Alert, Badge } from '@/components/ui'
import { Table2, RefreshCw, Download, Search } from 'lucide-react'

interface ArpEntry {
  ip: string
  mac: string
  interface: string
  entry_type: string
}

interface ArpResult {
  entries: ArpEntry[]
  count: number
}

export function ArpPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ArpResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')

  const loadArpTable = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await invoke<ArpResult>('get_arp_table')
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadArpTable()
  }, [])

  const filteredEntries = results?.entries.filter(entry => 
    entry.ip.toLowerCase().includes(filter.toLowerCase()) ||
    entry.mac.toLowerCase().includes(filter.toLowerCase()) ||
    entry.interface.toLowerCase().includes(filter.toLowerCase())
  ) || []

  const exportCsv = () => {
    if (!results) return
    const csv = [
      'IP-Adresse,MAC-Adresse,Interface,Typ',
      ...filteredEntries.map(e => `${e.ip},${e.mac},${e.interface},${e.entry_type}`)
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `arp_table_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Table2 className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">ARP Viewer</h1>
          <p className="text-text-secondary">Zeigen Sie die ARP-Tabelle Ihres Systems an</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>ARP-Tabelle</CardTitle>
            <div className="flex gap-2">
              <Button 
                onClick={loadArpTable} 
                disabled={isLoading} 
                loading={isLoading}
                icon={<RefreshCw className="w-4 h-4" />}
              >
                Aktualisieren
              </Button>
              {results && (
                <Button variant="secondary" onClick={exportCsv} icon={<Download className="w-4 h-4" />}>
                  CSV Export
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filter */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filtern nach IP, MAC oder Interface..."
                className="w-full pl-10 pr-4 py-2 bg-bg-tertiary border border-border-default rounded-lg text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
              />
            </div>
          </div>

          {error && <Alert variant="error" title="Fehler">{error}</Alert>}

          {results && (
            <>
              <div className="mb-4 text-sm text-text-secondary">
                {filteredEntries.length} von {results.count} Einträgen
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-default">
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">IP-Adresse</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">MAC-Adresse</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Interface</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Typ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEntries.map((entry, idx) => (
                      <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                        <td className="py-2 px-3 font-mono text-sm">{entry.ip}</td>
                        <td className="py-2 px-3 font-mono text-sm text-accent-blue">{entry.mac}</td>
                        <td className="py-2 px-3 text-sm text-text-secondary">{entry.interface}</td>
                        <td className="py-2 px-3">
                          <Badge variant={entry.entry_type === 'dynamic' ? 'info' : 'default'}>
                            {entry.entry_type}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                    {filteredEntries.length === 0 && (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-text-muted">
                          Keine Einträge gefunden
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
