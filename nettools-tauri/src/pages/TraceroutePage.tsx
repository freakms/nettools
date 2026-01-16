import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert } from '@/components/ui'
import { Route, Play } from 'lucide-react'

interface TracerouteHop {
  hop: number
  ip: string | null
  hostname: string | null
  rtt1: number | null
  rtt2: number | null
  rtt3: number | null
}

interface TracerouteResult {
  target: string
  hops: TracerouteHop[]
  duration_ms: number
}

export function TraceroutePage() {
  const [target, setTarget] = useState('')
  const [maxHops, setMaxHops] = useState('30')
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<TracerouteResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runTraceroute = async () => {
    if (!target) {
      setError('Bitte geben Sie ein Ziel ein')
      return
    }

    setIsRunning(true)
    setError(null)
    setResults(null)

    try {
      const result = await invoke<TracerouteResult>('run_traceroute', {
        target,
        maxHops: parseInt(maxHops),
      })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsRunning(false)
    }
  }

  const formatRtt = (rtt: number | null) => {
    if (rtt === null) return '*'
    return `${rtt.toFixed(1)}ms`
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Route className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Traceroute</h1>
          <p className="text-text-secondary">Verfolgen Sie den Netzwerkpfad zu einem Ziel</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Konfiguration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                label="Ziel (IP oder Hostname)"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="google.com oder 8.8.8.8"
                onKeyDown={(e) => e.key === 'Enter' && runTraceroute()}
              />
            </div>
            <div className="w-32">
              <Input
                label="Max Hops"
                type="number"
                value={maxHops}
                onChange={(e) => setMaxHops(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={runTraceroute} disabled={isRunning} loading={isRunning} icon={<Play className="w-4 h-4" />}>
                {isRunning ? 'Läuft...' : 'Starten'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Route zu {results.target}</CardTitle>
              <span className="text-sm text-text-secondary">{results.duration_ms}ms</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-default">
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary w-16">Hop</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">IP-Adresse</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Hostname</th>
                    <th className="text-right py-2 px-3 text-sm font-medium text-text-secondary">RTT 1</th>
                    <th className="text-right py-2 px-3 text-sm font-medium text-text-secondary">RTT 2</th>
                    <th className="text-right py-2 px-3 text-sm font-medium text-text-secondary">RTT 3</th>
                  </tr>
                </thead>
                <tbody>
                  {results.hops.map((hop, idx) => (
                    <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                      <td className="py-2 px-3 text-sm font-medium">{hop.hop}</td>
                      <td className="py-2 px-3 font-mono text-sm">{hop.ip || '*'}</td>
                      <td className="py-2 px-3 text-sm text-text-secondary">{hop.hostname || '-'}</td>
                      <td className="py-2 px-3 text-sm text-right">{formatRtt(hop.rtt1)}</td>
                      <td className="py-2 px-3 text-sm text-right">{formatRtt(hop.rtt2)}</td>
                      <td className="py-2 px-3 text-sm text-right">{formatRtt(hop.rtt3)}</td>
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
