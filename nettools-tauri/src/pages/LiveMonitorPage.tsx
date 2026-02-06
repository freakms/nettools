import { useState, useEffect, useRef, useCallback } from 'react'
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
  return ips.sort((a, b) => {
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
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const hostsRef = useRef<Map<string, HostStats>>(new Map())
  const abortRef = useRef(false)

  // Keep hostsRef in sync with hosts state
  useEffect(() => {
    hostsRef.current = hosts
  }, [hosts])

  const startMonitoring = async () => {
    if (!hostsInput.trim()) {
      setError('Bitte geben Sie mindestens eine IP-Adresse ein')
      return
    }

    setError(null)
    abortRef.current = false
    
    try {
      // Parse and validate hosts
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
      const sortedList = sortIpsNumerically([...ipList])
      setSortedIps(sortedList)

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
      setIsPaused(false)

      // Resolve hostnames in background (non-blocking)
      sortedList.forEach(ip => {
        if (abortRef.current) return
        invoke<string | null>('monitor_resolve_hostname', { ip }).then(hostname => {
          if (abortRef.current) return
          setHosts(prev => {
            const updated = new Map(prev)
            const host = updated.get(ip)
            if (host) {
              updated.set(ip, { ...host, hostname })
            }
            return updated
          })
        }).catch(() => {})
      })

      // Start ping loop
      const pingAll = async () => {
        if (abortRef.current) return
        
        const currentHosts = hostsRef.current
        const promises: Promise<void>[] = []
        
        for (const [ip, currentStats] of currentHosts) {
          if (abortRef.current) break
          
          const promise = invoke<HostStats>('monitor_ping_host', {
            ip,
            currentStats
          }).then(updatedStats => {
            if (abortRef.current) return
            
            setHosts(prev => {
              const updated = new Map(prev)
              const existing = updated.get(ip)
              if (existing?.hostname && !updatedStats.hostname) {
                updatedStats.hostname = existing.hostname
              }
              updated.set(ip, updatedStats)
              return updated
            })
          }).catch(e => {
            console.error(`Ping error for ${ip}:`, e)
          })
          
          promises.push(promise)
        }
        
        await Promise.all(promises)
      }

      // Initial ping
      await pingAll()

      // Start interval
      if (!abortRef.current) {
        intervalRef.current = setInterval(pingAll, 1000)
      }

    } catch (e) {
      setError(String(e))
    }
  }

  const stopMonitoring = useCallback(() => {
    abortRef.current = true
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsRunning(false)
    setIsPaused(false)
  }, [])

  const pauseMonitoring = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsPaused(true)
  }

  const resumeMonitoring = () => {
    if (!isRunning) return
    
    setIsPaused(false)
    abortRef.current = false
    
    const pingAll = async () => {
      if (abortRef.current) return
      
      const currentHosts = hostsRef.current
      const promises: Promise<void>[] = []
      
      for (const [ip, currentStats] of currentHosts) {
        if (abortRef.current) break
        
        const promise = invoke<HostStats>('monitor_ping_host', {
          ip,
          currentStats
        }).then(updatedStats => {
          if (abortRef.current) return
          
          setHosts(prev => {
            const updated = new Map(prev)
            const existing = updated.get(ip)
            if (existing?.hostname && !updatedStats.hostname) {
              updatedStats.hostname = existing.hostname
            }
            updated.set(ip, updatedStats)
            return updated
          })
        }).catch(e => {
          console.error(`Ping error for ${ip}:`, e)
        })
        
        promises.push(promise)
      }
      
      await Promise.all(promises)
    }

    intervalRef.current = setInterval(pingAll, 1000)
  }

  const clearResults = useCallback(() => {
    setIsClearing(true)
    abortRef.current = true
    
    // Stop monitoring first
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    // Use setTimeout to allow UI to update
    setTimeout(() => {
      setHosts(new Map())
      setSortedIps([])
      hostsRef.current = new Map()
      setIsRunning(false)
      setIsPaused(false)
      setIsClearing(false)
    }, 50)
  }, [])

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
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
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

      // Clear canvas
      ctx.clearRect(0, 0, width, height)

      // Get valid RTT values
      const validData = history.filter(p => p.success && p.rtt_ms !== null)
      if (validData.length === 0) return

      const maxRtt = Math.max(...validData.map(p => p.rtt_ms || 0), 100)
      const xStep = (width - 2 * padding) / Math.max(history.length - 1, 1)

      // Draw line
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

      // Draw points
      history.forEach((point, i) => {
        const x = padding + i * xStep
        
        if (point.success && point.rtt_ms !== null) {
          const y = height - padding - (point.rtt_ms / maxRtt) * (height - 2 * padding)
          ctx.beginPath()
          ctx.fillStyle = '#06b6d4'
          ctx.arc(x, y, 2, 0, Math.PI * 2)
          ctx.fill()
        } else {
          // Draw timeout indicator
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

      {/* Legend */}
      <div className="flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-accent-green" />
          <span className="text-text-secondary">0-50ms</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-accent-yellow" />
          <span className="text-text-secondary">51-150ms</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-accent-red" />
          <span className="text-text-secondary">150ms+ / Offline</span>
        </div>
      </div>

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
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
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
                        <td className="py-2 px-3 text-sm text-text-secondary">{host.hostname || '-'}</td>
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
