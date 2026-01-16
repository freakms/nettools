import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Network, Play, Download } from 'lucide-react'

interface PortResult {
  port: number
  status: string
  service: string | null
  banner: string | null
}

interface PortScanResult {
  target: string
  results: PortResult[]
  open_ports: number
  duration_ms: number
}

export function PortScanPage() {
  const [target, setTarget] = useState('')
  const [ports, setPorts] = useState('21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080')
  const [timeout, setTimeout] = useState('1000')
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState<PortScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const parsePortsString = (portsStr: string): number[] => {
    const ports: number[] = []
    const parts = portsStr.split(',').map(p => p.trim())
    
    for (const part of parts) {
      if (part.includes('-')) {
        const [start, end] = part.split('-').map(p => parseInt(p.trim()))
        for (let i = start; i <= end && i <= 65535; i++) {
          if (i >= 1) ports.push(i)
        }
      } else {
        const port = parseInt(part)
        if (port >= 1 && port <= 65535) ports.push(port)
      }
    }
    
    return [...new Set(ports)].sort((a, b) => a - b)
  }

  const startScan = async () => {
    if (!target) {
      setError('Bitte geben Sie ein Ziel ein')
      return
    }

    setIsScanning(true)
    setError(null)
    setResults(null)

    try {
      const portList = parsePortsString(ports)
      const result = await invoke<PortScanResult>('scan_ports', {
        target,
        ports: portList,
        timeoutMs: parseInt(timeout),
      })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsScanning(false)
    }
  }

  const setCommonPorts = (preset: string) => {
    const presets: Record<string, string> = {
      'quick': '21,22,23,25,80,110,143,443,445,3389',
      'web': '80,443,8080,8443,8000,3000,5000',
      'database': '1433,1521,3306,5432,6379,27017',
      'full': '1-1024',
    }
    setPorts(presets[preset] || presets.quick)
  }

  const exportCsv = () => {
    if (!results) return
    const csv = [
      'Port,Status,Service',
      ...results.results.map(r => `${r.port},${r.status},${r.service || ''}`)
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `portscan_${target}_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Network className="w-8 h-8 text-accent-blue" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Port Scanner</h1>
          <p className="text-text-secondary">Finden Sie offene Ports auf Zielsystemen</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Scan-Konfiguration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Ziel (IP oder Hostname)"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="192.168.1.1 oder example.com"
            />
            <Input
              label="Timeout (ms)"
              type="number"
              value={timeout}
              onChange={(e) => setTimeout(e.target.value)}
            />
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Ports (kommagetrennt oder Bereich)
            </label>
            <Input
              value={ports}
              onChange={(e) => setPorts(e.target.value)}
              placeholder="80,443,8080 oder 1-1024"
            />
            <div className="flex gap-2 mt-2">
              <Button variant="ghost" size="sm" onClick={() => setCommonPorts('quick')}>Quick</Button>
              <Button variant="ghost" size="sm" onClick={() => setCommonPorts('web')}>Web</Button>
              <Button variant="ghost" size="sm" onClick={() => setCommonPorts('database')}>Database</Button>
              <Button variant="ghost" size="sm" onClick={() => setCommonPorts('full')}>Top 1024</Button>
            </div>
          </div>
          
          <div className="flex gap-3 mt-4">
            <Button onClick={startScan} disabled={isScanning} loading={isScanning} icon={<Play className="w-4 h-4" />}>
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

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Ergebnisse für {results.target}</CardTitle>
              <div className="flex gap-4 text-sm">
                <span className="text-text-secondary">
                  Offen: <strong className="text-accent-green">{results.open_ports}</strong>
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
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Port</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Status</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Service</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((result, idx) => (
                    <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                      <td className="py-2 px-3 font-mono text-sm">{result.port}</td>
                      <td className="py-2 px-3">
                        <Badge variant={result.status === 'open' ? 'success' : result.status === 'filtered' ? 'warning' : 'error'}>
                          {result.status === 'open' ? 'Offen' : result.status === 'filtered' ? 'Gefiltert' : 'Geschlossen'}
                        </Badge>
                      </td>
                      <td className="py-2 px-3 text-sm text-text-secondary">{result.service || '-'}</td>
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
