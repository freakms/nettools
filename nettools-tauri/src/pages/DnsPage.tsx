import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Globe, Search, ExternalLink, Copy, Check } from 'lucide-react'

interface DnsRecord {
  record_type: string
  value: string
  ttl: number | null
}

interface DnsResult {
  query: string
  records: DnsRecord[]
  server: string
}

type DnsServer = 'system' | 'google' | 'cloudflare' | 'quad9' | 'opendns' | 'custom'

const DNS_SERVERS: Record<DnsServer, string> = {
  system: '',
  google: '8.8.8.8',
  cloudflare: '1.1.1.1',
  quad9: '9.9.9.9',
  opendns: '208.67.222.222',
  custom: '',
}

export function DnsPage() {
  const [query, setQuery] = useState('')
  const [selectedServer, setSelectedServer] = useState<DnsServer>('system')
  const [customServer, setCustomServer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<DnsResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copiedValue, setCopiedValue] = useState<string | null>(null)

  const lookup = async () => {
    if (!query.trim()) {
      setError('Bitte geben Sie einen Hostnamen oder eine IP-Adresse ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const server = selectedServer === 'custom' ? customServer : DNS_SERVERS[selectedServer]
      const result = await invoke<DnsResult>('lookup_dns', { 
        query: query.trim(),
        server: server || null,
      })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const openMXToolbox = () => {
    if (!query.trim()) return
    window.open(`https://mxtoolbox.com/SuperTool.aspx?action=dns%3a${encodeURIComponent(query)}`, '_blank')
  }

  const openDNSDumpster = () => {
    window.open('https://dnsdumpster.com/', '_blank')
  }

  const copyToClipboard = async (value: string) => {
    await navigator.clipboard.writeText(value)
    setCopiedValue(value)
    setTimeout(() => setCopiedValue(null), 2000)
  }

  const getRecordColor = (type: string) => {
    switch (type) {
      case 'A': return 'success'
      case 'AAAA': return 'info'
      case 'CNAME': return 'warning'
      case 'MX': return 'error'
      case 'NS': return 'secondary'
      case 'TXT': return 'info'
      case 'PTR': return 'success'
      default: return 'secondary'
    }
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Globe className="w-8 h-8 text-accent-blue" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">DNS Lookup</h1>
          <p className="text-text-secondary">Resolve hostnames to IP addresses and vice versa</p>
        </div>
      </div>

      {/* Configuration */}
      <Card variant="bordered">
        <CardContent className="pt-6">
          {/* Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-text-primary mb-2">
              Enter Hostname or IP Address:
            </label>
            <p className="text-xs text-text-muted mb-2">
              Examples: google.com, 8.8.8.8, github.com, 192.168.1.1
            </p>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="google.com or 8.8.8.8"
              onKeyDown={(e) => e.key === 'Enter' && lookup()}
            />
          </div>

          {/* DNS Server Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-text-primary mb-2">
              DNS Server:
            </label>
            <p className="text-xs text-text-muted mb-3">
              Select a preset or enter custom DNS server IP
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
              <label className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'system' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
                <input
                  type="radio"
                  name="dnsServer"
                  checked={selectedServer === 'system'}
                  onChange={() => setSelectedServer('system')}
                  className="accent-accent-blue"
                />
                <span className="text-sm text-text-primary">System Default</span>
              </label>
              
              <label className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'google' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
                <input
                  type="radio"
                  name="dnsServer"
                  checked={selectedServer === 'google'}
                  onChange={() => setSelectedServer('google')}
                  className="accent-accent-blue"
                />
                <span className="text-sm text-text-primary">Google (8.8.8.8)</span>
              </label>
              
              <label className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'cloudflare' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
                <input
                  type="radio"
                  name="dnsServer"
                  checked={selectedServer === 'cloudflare'}
                  onChange={() => setSelectedServer('cloudflare')}
                  className="accent-accent-blue"
                />
                <span className="text-sm text-text-primary">Cloudflare (1.1.1.1)</span>
              </label>
              
              <label className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'quad9' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
                <input
                  type="radio"
                  name="dnsServer"
                  checked={selectedServer === 'quad9'}
                  onChange={() => setSelectedServer('quad9')}
                  className="accent-accent-blue"
                />
                <span className="text-sm text-text-primary">Quad9 (9.9.9.9)</span>
              </label>
              
              <label className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'opendns' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
                <input
                  type="radio"
                  name="dnsServer"
                  checked={selectedServer === 'opendns'}
                  onChange={() => setSelectedServer('opendns')}
                  className="accent-accent-blue"
                />
                <span className="text-sm text-text-primary">OpenDNS (208.67.222.222)</span>
              </label>
            </div>

            {/* Custom DNS */}
            <label className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${selectedServer === 'custom' ? 'border-accent-blue bg-accent-blue/10' : 'border-border-default hover:bg-bg-hover'}`}>
              <input
                type="radio"
                name="dnsServer"
                checked={selectedServer === 'custom'}
                onChange={() => setSelectedServer('custom')}
                className="accent-accent-blue"
              />
              <span className="text-sm text-text-primary whitespace-nowrap">Custom:</span>
              <Input
                value={customServer}
                onChange={(e) => { setCustomServer(e.target.value); setSelectedServer('custom') }}
                placeholder="Enter DNS server IP (e.g., 192.168.1.1)"
                className="flex-1"
              />
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <Button onClick={lookup} disabled={isLoading} loading={isLoading} icon={<Search className="w-4 h-4" />}>
              DNS Lookup
            </Button>
            <Button variant="secondary" onClick={openMXToolbox} icon={<ExternalLink className="w-4 h-4" />}>
              MXToolbox (DNS Check)
            </Button>
            <Button variant="secondary" onClick={openDNSDumpster} icon={<ExternalLink className="w-4 h-4" />}>
              DNSDumpster
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Results */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle className="text-accent-green">Results</CardTitle>
        </CardHeader>
        <CardContent>
          {!results ? (
            <p className="text-text-muted text-center py-8">
              No lookup performed yet. Enter a hostname or IP address and click Lookup.
            </p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-4 text-sm text-text-secondary">
                <span>Query: <strong className="text-text-primary">{results.query}</strong></span>
                {results.server && <span>Server: <strong className="text-text-primary">{results.server}</strong></span>}
              </div>

              {results.records.length === 0 ? (
                <p className="text-text-muted text-center py-4">No records found.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-default">
                        <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Type</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Value</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">TTL</th>
                        <th className="text-right py-2 px-3 text-sm font-medium text-text-secondary"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.records.map((record, idx) => (
                        <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                          <td className="py-2 px-3">
                            <Badge variant={getRecordColor(record.record_type) as any}>
                              {record.record_type}
                            </Badge>
                          </td>
                          <td className="py-2 px-3 font-mono text-sm text-text-primary break-all">
                            {record.value}
                          </td>
                          <td className="py-2 px-3 text-sm text-text-secondary">
                            {record.ttl || '-'}
                          </td>
                          <td className="py-2 px-3 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(record.value)}
                              icon={copiedValue === record.value ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
