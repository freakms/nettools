import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Radar, Play, Square, Download } from 'lucide-react'

interface PingResult {
  ip: string
  hostname: string | null
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

export function ScannerPage() {
  const [target, setTarget] = useState('192.168.1.1-254')
  const [timeout, setTimeout] = useState('1000')
  const [onlyResponding, setOnlyResponding] = useState(true)
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const startScan = async () => {
    setIsScanning(true)
    setError(null)
    setResults(null)

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

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Radar className="w-8 h-8 text-accent-blue" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">IPv4 Scanner</h1>
          <p className="text-text-secondary">Scannen Sie Ihr Netzwerk nach aktiven Hosts</p>
        </div>
      </div>

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
              <Button variant="secondary" onClick={exportCsv} icon={<Download className="w-4 h-4" />}>
                CSV Export
              </Button>
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
                <span className="text-text-secondary">
                  Dauer: <strong className="text-text-primary">{results.duration_ms}ms</strong>
                </span>
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
