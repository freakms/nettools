import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Radar, Play, Square, Download, History, GitCompare, Trash2, Clock, Plus, Minus, Activity, Upload, Save, FolderOpen, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Scan, CheckCircle, XCircle, Percent } from 'lucide-react'
import { useStore } from '@/store'

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

interface ScanProfile {
  name: string
  target: string
  timeout: string
  aggressiveness: string
  onlyResponding: boolean
}

interface ComparisonResult {
  added: PingResult[]
  removed: PingResult[]
  unchanged: PingResult[]
  changed: { ip: string; old: PingResult; new: PingResult }[]
}

const STORAGE_KEY = 'nettools-scan-history'
const PROFILES_KEY = 'nettools-scan-profiles'
const ITEMS_PER_PAGE = 50

export function ScannerPage() {
  const { setActiveTool } = useStore()
  const [target, setTarget] = useState('192.168.1.1-254')
  const [timeout, setTimeout] = useState('1000')
  const [aggressiveness, setAggressiveness] = useState<'low' | 'medium' | 'high'>('medium')
  const [onlyResponding, setOnlyResponding] = useState(true)
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  
  // History & Comparison state
  const [history, setHistory] = useState<SavedScan[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [showComparison, setShowComparison] = useState(false)
  const [selectedScans, setSelectedScans] = useState<string[]>([])
  const [comparison, setComparison] = useState<ComparisonResult | null>(null)
  
  // Profiles
  const [profiles, setProfiles] = useState<ScanProfile[]>([])
  const [showProfiles, setShowProfiles] = useState(false)
  const [newProfileName, setNewProfileName] = useState('')

  // Load history and profiles on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY)
    if (savedHistory) {
      try { setHistory(JSON.parse(savedHistory)) } catch (e) { console.error('Failed to load scan history:', e) }
    }
    const savedProfiles = localStorage.getItem(PROFILES_KEY)
    if (savedProfiles) {
      try { setProfiles(JSON.parse(savedProfiles)) } catch (e) { console.error('Failed to load profiles:', e) }
    }
  }, [])

  const saveHistory = (newHistory: SavedScan[]) => {
    setHistory(newHistory)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory))
  }

  const saveProfiles = (newProfiles: ScanProfile[]) => {
    setProfiles(newProfiles)
    localStorage.setItem(PROFILES_KEY, JSON.stringify(newProfiles))
  }

  // Aggressiveness to timeout mapping
  const getTimeoutFromAggressiveness = (agg: string) => {
    switch (agg) {
      case 'low': return '3000'
      case 'high': return '500'
      default: return '1000'
    }
  }

  const handleAggressivenessChange = (value: string) => {
    setAggressiveness(value as 'low' | 'medium' | 'high')
    setTimeout(getTimeoutFromAggressiveness(value))
  }

  const startScan = async () => {
    setIsScanning(true)
    setError(null)
    setResults(null)
    setComparison(null)
    setCurrentPage(1)
    try {
      const result = await invoke<ScanResult>('scan_network', { target, timeoutMs: parseInt(timeout), onlyResponding: false })
      setResults(result)
    } catch (e) { setError(String(e)) } finally { setIsScanning(false) }
  }

  const cancelScan = () => {
    setIsScanning(false)
  }

  const saveScan = () => {
    if (!results) return
    const newScan: SavedScan = {
      id: Date.now().toString(), timestamp: new Date().toISOString(), target,
      results: results.results, total_hosts: results.total_hosts, responding_hosts: results.responding_hosts,
    }
    const newHistory = [newScan, ...history].slice(0, 20)
    saveHistory(newHistory)
  }

  const deleteScan = (id: string) => {
    saveHistory(history.filter(h => h.id !== id))
    setSelectedScans(prev => prev.filter(s => s !== id))
  }

  const clearHistory = () => { saveHistory([]); setSelectedScans([]); setComparison(null) }

  const toggleScanSelection = (id: string) => {
    setSelectedScans(prev => {
      if (prev.includes(id)) return prev.filter(s => s !== id)
      if (prev.length >= 2) return [prev[1], id]
      return [...prev, id]
    })
  }

  const compareScans = () => {
    if (selectedScans.length !== 2) return
    const scan1 = history.find(h => h.id === selectedScans[0])
    const scan2 = history.find(h => h.id === selectedScans[1])
    if (!scan1 || !scan2) return

    const ips1 = new Set(scan1.results.filter(r => r.status === 'online').map(r => r.ip))
    const ips2 = new Set(scan2.results.filter(r => r.status === 'online').map(r => r.ip))

    const added: PingResult[] = [], removed: PingResult[] = [], unchanged: PingResult[] = []
    const changed: { ip: string; old: PingResult; new: PingResult }[] = []

    scan2.results.forEach(r => { if (r.status === 'online' && !ips1.has(r.ip)) added.push(r) })
    scan1.results.forEach(r => { if (r.status === 'online' && !ips2.has(r.ip)) removed.push(r) })
    scan1.results.forEach(r1 => {
      if (r1.status === 'online' && ips2.has(r1.ip)) {
        const r2 = scan2.results.find(r => r.ip === r1.ip)
        if (r2) {
          if (r1.hostname !== r2.hostname || r1.rtt !== r2.rtt) changed.push({ ip: r1.ip, old: r1, new: r2 })
          else unchanged.push(r2)
        }
      }
    })

    setComparison({ added, removed, unchanged, changed })
    setShowComparison(true)
    setShowHistory(false)
  }

  const loadScan = (scan: SavedScan) => {
    setResults({ results: scan.results, total_hosts: scan.total_hosts, responding_hosts: scan.responding_hosts, duration_ms: 0 })
    setTarget(scan.target)
    setShowHistory(false)
    setCurrentPage(1)
  }

  // Profile functions
  const saveProfile = () => {
    if (!newProfileName.trim()) return
    const profile: ScanProfile = { name: newProfileName.trim(), target, timeout, aggressiveness, onlyResponding }
    const newProfiles = [...profiles.filter(p => p.name !== profile.name), profile]
    saveProfiles(newProfiles)
    setNewProfileName('')
    setShowProfiles(false)
  }

  const loadProfile = (profile: ScanProfile) => {
    setTarget(profile.target)
    setTimeout(profile.timeout)
    setAggressiveness(profile.aggressiveness as 'low' | 'medium' | 'high')
    setOnlyResponding(profile.onlyResponding)
    setShowProfiles(false)
  }

  const deleteProfile = (name: string) => {
    saveProfiles(profiles.filter(p => p.name !== name))
  }

  // Import IP list
  const importIpList = async () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.txt,.csv'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return
      const text = await file.text()
      const ips = text.split(/[\n,;]+/).map(ip => ip.trim()).filter(ip => ip.length > 0)
      setTarget(ips.join(', '))
    }
    input.click()
  }

  const exportCsv = () => {
    if (!results) return
    const csv = ['IP,Hostname,Status,RTT (ms),TTL', ...results.results.map(r => `${r.ip},${r.hostname || ''},${r.status},${r.rtt || ''},${r.ttl || ''}`)].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scan_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
  }

  const formatDate = (iso: string) => new Date(iso).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })

  // Pagination
  const filteredResults = results?.results.filter(r => !onlyResponding || r.status === 'online') || []
  const totalPages = Math.ceil(filteredResults.length / ITEMS_PER_PAGE)
  const paginatedResults = filteredResults.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)

  // Statistics
  const totalScanned = results?.total_hosts || 0
  const onlineCount = results?.results.filter(r => r.status === 'online').length || 0
  const noResponseCount = results?.results.filter(r => r.status !== 'online').length || 0
  const onlinePercent = totalScanned > 0 ? ((onlineCount / totalScanned) * 100).toFixed(1) : '0'

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Radar className="w-8 h-8 text-accent-blue" />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">IPv4 Scanner</h1>
            <p className="text-text-secondary">Scannen Sie Ihr Netzwerk nach aktiven Hosts</p>
          </div>
        </div>
      </div>

      {/* Scan Configuration */}
      <Card variant="bordered">
        <CardContent className="pt-6">
          {/* Input Row */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-4">
            <div className="md:col-span-8">
              <Input
                label="IPv4 / CIDR / Hostname"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="z.B. 192.168.1.0/24 oder server.example.com"
              />
            </div>
            <div className="md:col-span-4">
              <label className="block text-sm font-medium text-text-secondary mb-2">Aggressiveness</label>
              <select
                value={aggressiveness}
                onChange={(e) => handleAggressivenessChange(e.target.value)}
                className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
              >
                <option value="low">Low (3000ms)</option>
                <option value="medium">Medium (1000ms)</option>
                <option value="high">High (500ms)</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Button
              onClick={startScan}
              disabled={isScanning}
              loading={isScanning}
              icon={<Play className="w-4 h-4" />}
            >
              Start Scan
            </Button>
            <Button variant="secondary" onClick={importIpList} icon={<Upload className="w-4 h-4" />}>
              Import IP List
            </Button>
            <Button variant="success" onClick={() => setActiveTool('live-monitor')} icon={<Activity className="w-4 h-4" />}>
              Live Monitor
            </Button>
            {isScanning && (
              <Button variant="danger" onClick={cancelScan} icon={<Square className="w-4 h-4" />}>
                Cancel
              </Button>
            )}
            <div className="flex-1" />
            <Button variant="secondary" onClick={() => setShowProfiles(true)} icon={<Save className="w-4 h-4" />}>
              Save Profile
            </Button>
            <Button variant="secondary" onClick={() => setShowProfiles(true)} icon={<FolderOpen className="w-4 h-4" />}>
              Load Profile
            </Button>
          </div>

          {/* Filter Row */}
          <div className="flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={onlyResponding}
                onChange={(e) => { setOnlyResponding(e.target.checked); setCurrentPage(1) }}
                className="rounded accent-accent-blue"
              />
              Show only responding hosts
            </label>
            <Button variant="ghost" size="sm" onClick={() => { setOnlyResponding(false); setCurrentPage(1) }}>
              Show All Addresses
            </Button>
            <div className="flex-1" />
            <Button 
              variant={showHistory ? 'primary' : 'secondary'} 
              size="sm" 
              onClick={() => { setShowHistory(!showHistory); setShowComparison(false) }} 
              icon={<GitCompare className="w-4 h-4" />}
            >
              Compare Scans
            </Button>
            {results && (
              <Button variant="success" size="sm" onClick={exportCsv} icon={<Download className="w-4 h-4" />}>
                Export Results (Ctrl+E)
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Profiles Modal */}
      {showProfiles && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Scan-Profile</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setShowProfiles(false)}>Schließen</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <Input
                value={newProfileName}
                onChange={(e) => setNewProfileName(e.target.value)}
                placeholder="Profilname eingeben..."
                className="flex-1"
              />
              <Button onClick={saveProfile} disabled={!newProfileName.trim()} icon={<Save className="w-4 h-4" />}>
                Speichern
              </Button>
            </div>
            {profiles.length === 0 ? (
              <p className="text-text-muted text-center py-4">Keine gespeicherten Profile.</p>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {profiles.map((profile) => (
                  <div key={profile.name} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div>
                      <p className="font-medium text-text-primary">{profile.name}</p>
                      <p className="text-xs text-text-muted">{profile.target} • {profile.aggressiveness}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => loadProfile(profile)}>Laden</Button>
                      <Button variant="ghost" size="sm" onClick={() => deleteProfile(profile.name)} icon={<Trash2 className="w-4 h-4" />} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card variant="bordered">
          <CardContent className="p-4 text-center">
            <Scan className="w-6 h-6 mx-auto mb-2 text-text-muted" />
            <p className="text-2xl font-bold text-text-primary">{totalScanned}</p>
            <p className="text-sm text-text-muted">Total Scanned</p>
          </CardContent>
        </Card>
        <Card variant="bordered">
          <CardContent className="p-4 text-center">
            <CheckCircle className="w-6 h-6 mx-auto mb-2 text-accent-green" />
            <p className="text-2xl font-bold text-accent-green">{onlineCount}</p>
            <p className="text-sm text-text-muted">Online</p>
          </CardContent>
        </Card>
        <Card variant="bordered">
          <CardContent className="p-4 text-center">
            <XCircle className="w-6 h-6 mx-auto mb-2 text-accent-red" />
            <p className="text-2xl font-bold text-accent-red">{noResponseCount}</p>
            <p className="text-sm text-text-muted">No Response</p>
          </CardContent>
        </Card>
        <Card variant="bordered">
          <CardContent className="p-4 text-center">
            <Percent className="w-6 h-6 mx-auto mb-2 text-accent-cyan" />
            <p className="text-2xl font-bold text-accent-cyan">{onlinePercent}%</p>
            <p className="text-sm text-text-muted">Online %</p>
          </CardContent>
        </Card>
      </div>

      {/* History Panel */}
      {showHistory && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Scan-History</CardTitle>
              <div className="flex gap-2">
                {selectedScans.length === 2 && <Button size="sm" onClick={compareScans} icon={<GitCompare className="w-4 h-4" />}>Vergleichen</Button>}
                {history.length > 0 && <Button variant="ghost" size="sm" onClick={clearHistory} icon={<Trash2 className="w-4 h-4" />}>Alle löschen</Button>}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <p className="text-text-muted text-center py-8">Keine gespeicherten Scans. Führen Sie einen Scan durch und klicken Sie auf "Speichern".</p>
            ) : (
              <>
                <p className="text-sm text-text-muted mb-3">Wählen Sie 2 Scans zum Vergleichen:</p>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {history.map((scan) => (
                    <div key={scan.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer ${selectedScans.includes(scan.id) ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`} onClick={() => toggleScanSelection(scan.id)}>
                      <input type="checkbox" checked={selectedScans.includes(scan.id)} onChange={() => toggleScanSelection(scan.id)} className="rounded" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-text-muted" /><span className="text-sm font-medium">{formatDate(scan.timestamp)}</span></div>
                        <p className="text-xs text-text-muted truncate">{scan.target} • {scan.responding_hosts}/{scan.total_hosts} aktiv</p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); loadScan(scan) }}>Laden</Button>
                        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); deleteScan(scan.id) }} icon={<Trash2 className="w-4 h-4" />} />
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
              <Button variant="ghost" size="sm" onClick={() => setShowComparison(false)}>Schließen</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-accent-green/10 rounded-lg border border-accent-green/30">
                <div className="flex items-center gap-2"><Plus className="w-5 h-5 text-accent-green" /><span className="text-2xl font-bold text-accent-green">{comparison.added.length}</span></div>
                <p className="text-sm text-text-secondary">Neue Hosts</p>
              </div>
              <div className="p-4 bg-accent-red/10 rounded-lg border border-accent-red/30">
                <div className="flex items-center gap-2"><Minus className="w-5 h-5 text-accent-red" /><span className="text-2xl font-bold text-accent-red">{comparison.removed.length}</span></div>
                <p className="text-sm text-text-secondary">Entfernte Hosts</p>
              </div>
              <div className="p-4 bg-accent-yellow/10 rounded-lg border border-accent-yellow/30">
                <div className="flex items-center gap-2"><GitCompare className="w-5 h-5 text-accent-yellow" /><span className="text-2xl font-bold text-accent-yellow">{comparison.changed.length}</span></div>
                <p className="text-sm text-text-secondary">Geänderte Hosts</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg border border-border-default">
                <span className="text-2xl font-bold text-text-primary">{comparison.unchanged.length}</span>
                <p className="text-sm text-text-secondary">Unverändert</p>
              </div>
            </div>
            {comparison.added.length > 0 && <div className="mb-4"><h4 className="text-sm font-medium text-accent-green mb-2 flex items-center gap-2"><Plus className="w-4 h-4" /> Neue Hosts</h4><div className="flex flex-wrap gap-2">{comparison.added.map(h => <Badge key={h.ip} variant="success">{h.ip}</Badge>)}</div></div>}
            {comparison.removed.length > 0 && <div className="mb-4"><h4 className="text-sm font-medium text-accent-red mb-2 flex items-center gap-2"><Minus className="w-4 h-4" /> Entfernte Hosts</h4><div className="flex flex-wrap gap-2">{comparison.removed.map(h => <Badge key={h.ip} variant="error">{h.ip}</Badge>)}</div></div>}
          </CardContent>
        </Card>
      )}

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Results Table */}
      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Ergebnisse</CardTitle>
              <div className="flex items-center gap-4">
                {results.duration_ms > 0 && (
                  <span className="text-sm text-text-secondary">Dauer: <strong>{results.duration_ms}ms</strong></span>
                )}
                {results && (
                  <Button variant="secondary" size="sm" onClick={saveScan} icon={<History className="w-4 h-4" />}>
                    Save to History
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-accent-blue text-white">
                    <th className="text-left py-3 px-4 text-sm font-medium rounded-tl-lg">IP Address</th>
                    <th className="text-left py-3 px-4 text-sm font-medium">Hostname/FQDN</th>
                    <th className="text-left py-3 px-4 text-sm font-medium">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium rounded-tr-lg">RTT (ms)</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedResults.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-text-muted">No results</td>
                    </tr>
                  ) : (
                    paginatedResults.map((result, idx) => (
                      <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                        <td className="py-3 px-4 font-mono text-sm">{result.ip}</td>
                        <td className="py-3 px-4 text-sm text-text-secondary">{result.hostname || '-'}</td>
                        <td className="py-3 px-4">
                          <Badge variant={result.status === 'online' ? 'success' : result.status === 'timeout' ? 'warning' : 'error'}>
                            {result.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-sm">{result.rtt ? `${result.rtt}` : '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-border-default">
                <Button variant="secondary" size="sm" onClick={() => setCurrentPage(1)} disabled={currentPage === 1} icon={<ChevronsLeft className="w-4 h-4" />}>
                  First
                </Button>
                <Button variant="secondary" size="sm" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} icon={<ChevronLeft className="w-4 h-4" />}>
                  Prev
                </Button>
                <span className="px-4 text-sm text-text-secondary">
                  Page {currentPage} of {totalPages}
                </span>
                <Button variant="secondary" size="sm" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                  Next <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
                <Button variant="secondary" size="sm" onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages}>
                  Last <ChevronsRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
