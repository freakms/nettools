import { useState, useEffect, useRef } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Activity, Play, Square, Pause, PlayCircle, Download, Trash2 } from 'lucide-react'

interface PingDataPoint {
  timestamp: number
  success: boolean
  rtt_ms: number | null
}

interface HostStats {
  ip: string
  hostname: string | null
  status: string
  current_rtt: number | null
  avg_rtt: number | null
  min_rtt: number | null
  max_rtt: number | null
  packet_loss: number
  total_sent: number
  total_received: number
  history: PingDataPoint[]
}

// Numerische IP-Sortierung
const sortIpsNumerically = (ips: string[]): string[] => {
  return [...ips].sort((a, b) => {
    const partsA = a.split('.').map(Number)
    const partsB = b.split('.').map(Number)
    
    for (let i = 0; i < 4; i++) {
      if (partsA[i] !== partsB[i]) {
        return partsA[i] - partsB[i]
      }
    }
    return 0
  })
}

export function LiveMonitorPage() {
  const [hostsInput, setHostsInput] = useState('')
  const [hosts, setHosts] = useState<Map<string, HostStats>>(new Map())
  const [sortedIps, setSortedIps] = useState<string[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isClearing, setIsClearing] = useState(false)
  
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const hostsRef = useRef<Map<string, HostStats>>(new Map())
  const sortedIpsRef = useRef<string[]>([])
  const abortRef = useRef(false)
  const isRunningRef = useRef(false)

  const startMonitoring = async () => {
    if (!hostsInput.trim()) {
      setError('Bitte geben Sie mindestens eine IP-Adresse ein')
      return
    }

    setError(null)
    abortRef.current = false
    
    try {
      const ipList = await invoke<string[]>('monitor_init_hosts', { hostsInput })
      
      if (ipList.length === 0) {
        setError('Keine gültigen IP-Adressen gefunden')
        return
      }

      if (ipList.length > 100) {
        setError('Maximal 100 Hosts gleichzeitig erlaubt')
        return
      }

      // Sort IPs numerically
      const sortedList = sortIpsNumerically(ipList)
      setSortedIps(sortedList)
      sortedIpsRef.current = sortedList

      // Initialize host stats
      const initialHosts = new Map<string, HostStats>()
      for (const ip of sortedList) {
        initialHosts.set(ip, {
          ip,
          hostname: null,
          status: 'unknown',
          current_rtt: null,
          avg_rtt: null,
          min_rtt: null,
          max_rtt: null,
          packet_loss: 0,
          total_sent: 0,
          total_received: 0,
          history: []
        })
      }
      
      setHosts(initialHosts)
      hostsRef.current = initialHosts
      setIsRunning(true)
      isRunningRef.current = true
      setIsPaused(false)

      // Resolve hostnames in background
      sortedList.forEach(ip => {
        invoke<string | null>('monitor_resolve_hostname', { ip })
          .then(hostname => {
            if (hostname && !abortRef.current) {
              hostsRef.current = new Map(hostsRef.current)
              const host = hostsRef.current.get(ip)
              if (host && !host.hostname) {
                hostsRef.current.set(ip, { ...host, hostname })
                setHosts(new Map(hostsRef.current))
              }
            }
          })
          .catch(() => {})
      })

      // Start ping loop
      runPingCycle()

    } catch (e) {
      setError(String(e))
    }
  }

  const runPingCycle = async () => {
    if (abortRef.current || !isRunningRef.current) return

    const currentIps = sortedIpsRef.current
    const updatedHosts = new Map(hostsRef.current)
    
    // Ping in batches of 5
    const batchSize = 5
    for (let i = 0; i < currentIps.length; i += batchSize) {
      if (abortRef.current) break

      const batch = currentIps.slice(i, i + batchSize)
      
      await Promise.all(batch.map(async (ip) => {
        if (abortRef.current) return
        
        try {
          const currentStats = updatedHosts.get(ip)
          const result = await invoke<HostStats>('monitor_ping_host', {
            ip,
            currentStats
          })
          
          // Preserve hostname
          if (currentStats?.hostname && !result.hostname) {
            result.hostname = currentStats.hostname
          }
          
          updatedHosts.set(ip, result)
        } catch (e) {
          console.error(`Ping error for ${ip}:`, e)
        }
      }))
    }

    // Update state once after all pings
    if (!abortRef.current) {
      hostsRef.current = updatedHosts
      setHosts(new Map(updatedHosts))
      
      // Schedule next cycle
      timeoutRef.current = setTimeout(runPingCycle, 1000)
    }
  }

  const stopMonitoring = () => {
    abortRef.current = true
    isRunningRef.current = false
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    setIsRunning(false)
    setIsPaused(false)
  }

  const pauseMonitoring = () => {
    abortRef.current = true
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    setIsPaused(true)
  }

  const resumeMonitoring = () => {
    if (!isRunning) return
    abortRef.current = false
    setIsPaused(false)
    runPingCycle()
  }

  const clearResults = () => {
    setIsClearing(true)
    abortRef.current = true
    isRunningRef.current = false
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    
    setHosts(new Map())
    setSortedIps([])
    hostsRef.current = new Map()
    sortedIpsRef.current = []
    setIsRunning(false)
    setIsPaused(false)
    setIsClearing(false)
  }

  const exportData = async () => {
    try {
      const hostsArray = Array.from(hosts.values())
      const data = await invoke<string>('monitor_export_data', { hosts: hostsArray })
      
      const blob = new Blob([data], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ping_monitor_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
      a.click()
    } catch (e) {
      setError(String(e))
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortRef.current = true
      isRunningRef.current = false
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-accent-green'
      case 'offline': return 'bg-accent-red'
      default: return 'bg-gray-500'
    }
  }

  const getLatencyColor = (rtt: number | null) => {
    if (rtt === null) return 'text-text-muted'
    if (rtt <= 50) return 'text-accent-green'
    if (rtt <= 150) return 'text-accent-yellow'
    return 'text-accent-red'
  }

  // Mini sparkline graph component
  const SparklineGraph = ({ history }: { history: PingDataPoint[] }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
      const canvas = canvasRef.current
      if (!canvas || history.length === 0) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const width = canvas.width
      const height = canvas.height
      const padding = 2

      ctx.clearRect(0, 0, width, height)

      const validData = history.filter(p => p.success && p.rtt_ms !== null)
      if (validData.length === 0) return

      const maxRtt = Math.max(...validData.map(p => p.rtt_ms || 0), 100)
      const xStep = (width - 2 * padding) / Math.max(history.length - 1, 1)

      ctx.beginPath()
      ctx.strokeStyle = '#06b6d4'
      ctx.lineWidth = 1.5

      let firstPoint = true
      history.forEach((point, i) => {
        if (point.success && point.rtt_ms !== null) {
          const x = padding + i * xStep
          const y = height - padding - (point.rtt_ms / maxRtt) * (height - 2 * padding)
          
          if (firstPoint) {
            ctx.moveTo(x, y)
            firstPoint = false
          } else {
            ctx.lineTo(x, y)
          }
        }
      })
      ctx.stroke()

      history.forEach((point, i) => {
        const x = padding + i * xStep
        
        if (point.success && point.rtt_ms !== null) {
          const y = height - padding - (point.rtt_ms / maxRtt) * (height - 2 * padding)
          ctx.beginPath()
          ctx.fillStyle = '#06b6d4'
          ctx.arc(x, y, 2, 0, Math.PI * 2)
          ctx.fill()
        } else {
          ctx.beginPath()
          ctx.fillStyle = '#ef4444'
          ctx.arc(x, height - padding - 2, 2, 0, Math.PI * 2)
          ctx.fill()
        }
      })
    }, [history])

    return (
      <canvas
        ref={canvasRef}
        width={200}
        height={30}
        className="bg-bg-tertiary rounded"
      />
    )
  }

  // Summary stats
  const onlineCount = Array.from(hosts.values()).filter(h => h.status === 'online').length
  const offlineCount = Array.from(hosts.values()).filter(h => h.status === 'offline').length

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Activity className="w-8 h-8 text-accent-cyan" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Live Ping Monitor</h1>
          <p className="text-text-secondary">Überwachen Sie Hosts in Echtzeit</p>
        </div>
      </div>

      {/* Controls */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Hosts konfigurieren</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                value={hostsInput}
                onChange={(e) => setHostsInput(e.target.value)}
                placeholder="IPs, CIDRs, Ranges: z.B. 192.168.1.0/24, 10.0.0.1-50, 8.8.8.8"
                disabled={isRunning}
                onKeyDown={(e) => e.key === 'Enter' && !isRunning && startMonitoring()}
              />
              <p className="mt-1 text-xs text-text-muted">
                Unterstützt: Einzelne IPs, CIDR (192.168.1.0/24), Ranges (192.168.1.1-254), kommagetrennt
              </p>
            </div>
            <div className="flex items-start gap-2">
              {!isRunning ? (
                <Button onClick={startMonitoring} icon={<Play className="w-4 h-4" />}>
                  Start
                </Button>
              ) : (
                <>
                  {!isPaused ? (
                    <Button onClick={pauseMonitoring} variant="secondary" icon={<Pause className="w-4 h-4" />}>
                      Pause
                    </Button>
                  ) : (
                    <Button onClick={resumeMonitoring} variant="success" icon={<PlayCircle className="w-4 h-4" />}>
                      Fortsetzen
                    </Button>
                  )}
                  <Button onClick={stopMonitoring} variant="danger" icon={<Square className="w-4 h-4" />}>
                    Stop
                  </Button>
                </>
              )}
            </div>
          </div>

          {hosts.size > 0 && (
            <div className="flex gap-2 mt-4">
              <Button variant="secondary" size="sm" onClick={exportData} icon={<Download className="w-4 h-4" />}>
                Export
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={clearResults} 
                disabled={isClearing}
                icon={<Trash2 className="w-4 h-4" />}
              >
                {isClearing ? 'Wird geleert...' : 'Leeren'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary Stats */}
      {hosts.size > 0 && (
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-bg-secondary rounded-lg">
            <span className="text-text-muted">Gesamt:</span>
            <span className="font-bold text-text-primary">{hosts.size}</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-accent-green/10 rounded-lg">
            <div className="w-3 h-3 rounded-full bg-accent-green" />
            <span className="text-accent-green font-bold">{onlineCount}</span>
            <span className="text-text-muted">Online</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-accent-red/10 rounded-lg">
            <div className="w-3 h-3 rounded-full bg-accent-red" />
            <span className="text-accent-red font-bold">{offlineCount}</span>
            <span className="text-text-muted">Offline</span>
          </div>
        </div>
      )}

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Host Table */}
      {hosts.size > 0 && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Überwachte Hosts ({hosts.size})</CardTitle>
              {isRunning && (
                <Badge variant={isPaused ? 'warning' : 'success'}>
                  {isPaused ? 'Pausiert' : 'Aktiv'}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
              <table className="w-full">
                <thead className="sticky top-0 bg-bg-secondary">
                  <tr className="border-b border-border-default">
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary w-8"></th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">IP-Adresse</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Hostname</th>
                    <th className="text-center py-2 px-3 text-sm font-medium text-text-secondary">Aktuell</th>
                    <th className="text-center py-2 px-3 text-sm font-medium text-text-secondary">Avg</th>
                    <th className="text-center py-2 px-3 text-sm font-medium text-text-secondary">Min</th>
                    <th className="text-center py-2 px-3 text-sm font-medium text-text-secondary">Max</th>
                    <th className="text-center py-2 px-3 text-sm font-medium text-text-secondary">Loss</th>
                    <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Graph</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedIps.map((ip) => {
                    const host = hosts.get(ip)
                    if (!host) return null
                    return (
                      <tr key={host.ip} className="border-b border-border-default hover:bg-bg-hover">
                        <td className="py-2 px-3">
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(host.status)}`} />
                        </td>
                        <td className="py-2 px-3 font-mono text-sm">{host.ip}</td>
                        <td className="py-2 px-3 text-sm text-text-secondary truncate max-w-[150px]">{host.hostname || '-'}</td>
                        <td className={`py-2 px-3 text-sm text-center font-mono ${getLatencyColor(host.current_rtt)}`}>
                          {host.current_rtt !== null ? `${Math.round(host.current_rtt)}ms` : '-'}
                        </td>
                        <td className="py-2 px-3 text-sm text-center font-mono text-text-secondary">
                          {host.avg_rtt !== null ? `${Math.round(host.avg_rtt)}ms` : '-'}
                        </td>
                        <td className="py-2 px-3 text-sm text-center font-mono text-text-secondary">
                          {host.min_rtt !== null ? `${Math.round(host.min_rtt)}ms` : '-'}
                        </td>
                        <td className="py-2 px-3 text-sm text-center font-mono text-text-secondary">
                          {host.max_rtt !== null ? `${Math.round(host.max_rtt)}ms` : '-'}
                        </td>
                        <td className={`py-2 px-3 text-sm text-center font-mono ${host.packet_loss > 0 ? 'text-accent-red' : 'text-text-secondary'}`}>
                          {host.packet_loss.toFixed(1)}%
                        </td>
                        <td className="py-2 px-3">
                          <SparklineGraph history={host.history} />
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty state */}
      {hosts.size === 0 && !error && (
        <Card variant="bordered">
          <CardContent className="py-16 text-center">
            <Activity className="w-16 h-16 mx-auto mb-4 text-text-muted" />
            <h3 className="text-lg font-medium text-text-primary mb-2">Keine Hosts konfiguriert</h3>
            <p className="text-text-secondary">
              Geben Sie IP-Adressen, CIDR-Notationen oder Ranges ein und klicken Sie auf "Start"
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
