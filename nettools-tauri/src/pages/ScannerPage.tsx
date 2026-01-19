import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Radar, Play, Square, Download, History, GitCompare, Trash2, Clock, Plus, Minus } from 'lucide-react'

interface PingResult {
  ip: string
  hostname: string | null
  mac: string | null
  vendor: string | null
  status: string
  rtt: number | null
  ttl: number | null
}

interface ScanResult {
  results: PingResult[]
  total_hosts: number
  responding_hosts: number
  duration_ms: number
}

interface SavedScan {
  id: string
  timestamp: string
  target: string
  results: PingResult[]
  total_hosts: number
  responding_hosts: number
}

interface ComparisonResult {
  added: PingResult[]
  removed: PingResult[]
  unchanged: PingResult[]
  changed: { ip: string; old: PingResult; new: PingResult }[]
}

const STORAGE_KEY = 'nettools-scan-history'

export function ScannerPage() {
  const [target, setTarget] = useState('192.168.1.1-254')
  const [timeout, setTimeout] = useState('1000')
  const [onlyResponding, setOnlyResponding] = useState(true)
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // History & Comparison state
  const [history, setHistory] = useState<SavedScan[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [showComparison, setShowComparison] = useState(false)
  const [selectedScans, setSelectedScans] = useState<string[]>([])
  const [comparison, setComparison] = useState<ComparisonResult | null>(null)

  // Load history on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load scan history:', e)
      }
    }
  }, [])

  // Save history when it changes
  const saveHistory = (newHistory: SavedScan[]) => {
    setHistory(newHistory)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory))
  }

  const startScan = async () => {
    setIsScanning(true)
    setError(null)
    setResults(null)
    setComparison(null)

    try {
      const result = await invoke<ScanResult>('scan_network', {
        target,
        timeoutMs: parseInt(timeout),
        onlyResponding,
      })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsScanning(false)
    }
  }

  const saveScan = () => {
    if (!results) return

    const newScan: SavedScan = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      target,
      results: results.results,
      total_hosts: results.total_hosts,
      responding_hosts: results.responding_hosts,
    }

    // Keep only last 20 scans
    const newHistory = [newScan, ...history].slice(0, 20)
    saveHistory(newHistory)
  }

  const deleteScan = (id: string) => {
    const newHistory = history.filter(h => h.id !== id)
    saveHistory(newHistory)
    setSelectedScans(prev => prev.filter(s => s !== id))
  }

  const clearHistory = () => {
    saveHistory([])
    setSelectedScans([])
    setComparison(null)
  }

  const toggleScanSelection = (id: string) => {
    setSelectedScans(prev => {
      if (prev.includes(id)) {
        return prev.filter(s => s !== id)
      }
      if (prev.length >= 2) {
        return [prev[1], id]
      }
      return [...prev, id]
    })
  }

  const compareScans = () => {
    if (selectedScans.length !== 2) return

    const scan1 = history.find(h => h.id === selectedScans[0])
    const scan2 = history.find(h => h.id === selectedScans[1])

    if (!scan1 || !scan2) return

    // Get IPs from each scan
    const ips1 = new Set(scan1.results.filter(r => r.status === 'online').map(r => r.ip))
    const ips2 = new Set(scan2.results.filter(r => r.status === 'online').map(r => r.ip))

    const added: PingResult[] = []
    const removed: PingResult[] = []
    const unchanged: PingResult[] = []
    const changed: { ip: string; old: PingResult; new: PingResult }[] = []

    // Find added (in scan2 but not in scan1)
    scan2.results.forEach(r => {
      if (r.status === 'online' && !ips1.has(r.ip)) {
        added.push(r)
      }
    })

    // Find removed (in scan1 but not in scan2)
    scan1.results.forEach(r => {
      if (r.status === 'online' && !ips2.has(r.ip)) {
        removed.push(r)
      }
    })

    // Find unchanged and changed
    scan1.results.forEach(r1 => {
      if (r1.status === 'online' && ips2.has(r1.ip)) {
        const r2 = scan2.results.find(r => r.ip === r1.ip)
        if (r2) {
          if (r1.hostname !== r2.hostname || r1.rtt !== r2.rtt) {
            changed.push({ ip: r1.ip, old: r1, new: r2 })
          } else {
            unchanged.push(r2)
          }
        }
      }
    })

    setComparison({ added, removed, unchanged, changed })
    setShowComparison(true)
    setShowHistory(false)
  }

  const loadScan = (scan: SavedScan) => {
    setResults({
      results: scan.results,
      total_hosts: scan.total_hosts,
      responding_hosts: scan.responding_hosts,
      duration_ms: 0,
    })
    setTarget(scan.target)
    setShowHistory(false)
  }

  const exportCsv = () => {
    if (!results) return
    
    const csv = [
      'IP,Hostname,Status,RTT (ms),TTL',
      ...results.results.map(r => 
        `${r.ip},${r.hostname || ''},${r.status},${r.rtt || ''},${r.ttl || ''}`
      )
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scan_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
  }

  const formatDate = (iso: string) => {
    const date = new Date(iso)
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Radar className="w-8 h-8 text-accent-blue" />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">IPv4 Scanner</h1>
            <p className="text-text-secondary">Scannen Sie Ihr Netzwerk nach aktiven Hosts</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant={showHistory ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => { setShowHistory(!showHistory); setShowComparison(false) }}
            icon={<History className="w-4 h-4" />}
          >
            History ({history.length})
          </Button>
        </div>
      </div>

      {/* History Panel */}
      {showHistory && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Scan-History</CardTitle>
              <div className="flex gap-2">
                {selectedScans.length === 2 && (
                  <Button size="sm" onClick={compareScans} icon={<GitCompare className="w-4 h-4" />}>
                    Vergleichen
                  </Button>
                )}
                {history.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearHistory} icon={<Trash2 className="w-4 h-4" />}>
                    Alle löschen
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <p className="text-text-muted text-center py-8">
                Keine gespeicherten Scans. Führen Sie einen Scan durch und klicken Sie auf "Speichern".
              </p>
            ) : (
              <>
                <p className="text-sm text-text-muted mb-3">
                  Wählen Sie 2 Scans zum Vergleichen aus:
                </p>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {history.map((scan) => (
                    <div
                      key={scan.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                        selectedScans.includes(scan.id)
                          ? 'border-accent-blue bg-accent-blue/10'
                          : 'border-border-default hover:bg-bg-hover'
                      }`}
                      onClick={() => toggleScanSelection(scan.id)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedScans.includes(scan.id)}
                        onChange={() => toggleScanSelection(scan.id)}
                        className="rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-text-muted" />
                          <span className="text-sm font-medium">{formatDate(scan.timestamp)}</span>
                        </div>
                        <p className="text-xs text-text-muted truncate">
                          {scan.target} • {scan.responding_hosts}/{scan.total_hosts} aktiv
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); loadScan(scan) }}
                        >
                          Laden
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); deleteScan(scan.id) }}
                          icon={<Trash2 className="w-4 h-4" />}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Comparison Results */}
      {showComparison && comparison && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Scan-Vergleich</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setShowComparison(false)}>
                Schließen
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-accent-green/10 rounded-lg border border-accent-green/30">
                <div className="flex items-center gap-2">
                  <Plus className="w-5 h-5 text-accent-green" />
                  <span className="text-2xl font-bold text-accent-green">{comparison.added.length}</span>
                </div>
                <p className="text-sm text-text-secondary">Neue Hosts</p>
              </div>
              <div className="p-4 bg-accent-red/10 rounded-lg border border-accent-red/30">
                <div className="flex items-center gap-2">
                  <Minus className="w-5 h-5 text-accent-red" />
                  <span className="text-2xl font-bold text-accent-red">{comparison.removed.length}</span>
                </div>
                <p className="text-sm text-text-secondary">Entfernte Hosts</p>
              </div>
              <div className="p-4 bg-accent-yellow/10 rounded-lg border border-accent-yellow/30">
                <div className="flex items-center gap-2">
                  <GitCompare className="w-5 h-5 text-accent-yellow" />
                  <span className="text-2xl font-bold text-accent-yellow">{comparison.changed.length}</span>
                </div>
                <p className="text-sm text-text-secondary">Geänderte Hosts</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg border border-border-default">
                <span className="text-2xl font-bold text-text-primary">{comparison.unchanged.length}</span>
                <p className="text-sm text-text-secondary">Unverändert</p>
              </div>
            </div>

            {comparison.added.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-accent-green mb-2 flex items-center gap-2">
                  <Plus className="w-4 h-4" /> Neue Hosts
                </h4>
                <div className="flex flex-wrap gap-2">
                  {comparison.added.map(h => (
                    <Badge key={h.ip} variant="success">{h.ip}</Badge>
                  ))}
                </div>
              </div>
            )}

            {comparison.removed.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-accent-red mb-2 flex items-center gap-2">
                  <Minus className="w-4 h-4" /> Entfernte Hosts
                </h4>
                <div className="flex flex-wrap gap-2">
                  {comparison.removed.map(h => (
                    <Badge key={h.ip} variant="error">{h.ip}</Badge>
                  ))}
                </div>
              </div>
            )}

            {comparison.changed.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-accent-yellow mb-2 flex items-center gap-2">
                  <GitCompare className="w-4 h-4" /> Geänderte Hosts
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border-default">
                        <th className="text-left py-2 px-3">IP</th>
                        <th className="text-left py-2 px-3">Alter Wert</th>
                        <th className="text-left py-2 px-3">Neuer Wert</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparison.changed.map(c => (
                        <tr key={c.ip} className="border-b border-border-default">
                          <td className="py-2 px-3 font-mono">{c.ip}</td>
                          <td className="py-2 px-3 text-text-muted">
                            {c.old.hostname || '-'} / {c.old.rtt ? `${c.old.rtt}ms` : '-'}
                          </td>
                          <td className="py-2 px-3">
                            {c.new.hostname || '-'} / {c.new.rtt ? `${c.new.rtt}ms` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Scan Configuration */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Scan-Konfiguration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Ziel (IP, Range oder CIDR)"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="192.168.1.1-254 oder 192.168.1.0/24"
            />
            <Input
              label="Timeout (ms)"
              type="number"
              value={timeout}
              onChange={(e) => setTimeout(e.target.value)}
            />
            <div className="flex items-end gap-4">
              <label className="flex items-center gap-2 text-sm text-text-secondary">
                <input
                  type="checkbox"
                  checked={onlyResponding}
                  onChange={(e) => setOnlyResponding(e.target.checked)}
                  className="rounded"
                />
                Nur aktive Hosts
              </label>
            </div>
          </div>
          
          <div className="flex gap-3 mt-4">
            <Button
              onClick={startScan}
              disabled={isScanning}
              loading={isScanning}
              icon={isScanning ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            >
              {isScanning ? 'Scannt...' : 'Scan starten'}
            </Button>
            {results && (
              <>
                <Button variant="secondary" onClick={saveScan} icon={<History className="w-4 h-4" />}>
                  Speichern
                </Button>
                <Button variant="secondary" onClick={exportCsv} icon={<Download className="w-4 h-4" />}>
                  CSV Export
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="error" title="Fehler">
          {error}
        </Alert>
      )}

      {/* Results */}
      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Ergebnisse</CardTitle>
              <div className="flex gap-4 text-sm">
                <span className="text-text-secondary">
                  Gesamt: <strong className="text-text-primary">{results.total_hosts}</strong>
                </span>
                <span className="text-text-secondary">
                  Aktiv: <strong className="text-accent-green">{results.responding_hosts}</strong>
                </span>
                {results.duration_ms > 0 && (
                  <span className="text-text-secondary">
                    Dauer: <strong className="text-text-primary">{results.duration_ms}ms</strong>
                  </span>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-default">
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">IP-Adresse</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Hostname</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Status</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">RTT</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">TTL</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((result, idx) => (
                    <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                      <td className="py-2 px-3 font-mono text-sm">{result.ip}</td>
                      <td className="py-2 px-3 text-sm text-text-secondary">{result.hostname || '-'}</td>
                      <td className="py-2 px-3">
                        <Badge variant={result.status === 'online' ? 'success' : result.status === 'timeout' ? 'warning' : 'error'}>
                          {result.status}
                        </Badge>
                      </td>
                      <td className="py-2 px-3 text-sm">{result.rtt ? `${result.rtt}ms` : '-'}</td>
                      <td className="py-2 px-3 text-sm">{result.ttl || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
