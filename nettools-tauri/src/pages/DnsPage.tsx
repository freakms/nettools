import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Checkbox } from '@/components/ui'
import { Globe, Search } from 'lucide-react'

interface DnsRecord {
  record_type: string
  name: string
  value: string
  ttl: number
}

interface DnsResult {
  domain: string
  records: DnsRecord[]
  duration_ms: number
}

export function DnsPage() {
  const [domain, setDomain] = useState('')
  const [recordTypes, setRecordTypes] = useState({
    A: true,
    AAAA: false,
    MX: true,
    NS: true,
    TXT: false,
    CNAME: false,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<DnsResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const lookup = async () => {
    if (!domain) {
      setError('Bitte geben Sie eine Domain ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const types = Object.entries(recordTypes)
        .filter(([_, enabled]) => enabled)
        .map(([type]) => type)
      
      const result = await invoke<DnsResult>('lookup_dns', {
        domain,
        recordTypes: types,
      })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const toggleRecordType = (type: string) => {
    setRecordTypes(prev => ({ ...prev, [type]: !prev[type as keyof typeof prev] }))
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Globe className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">DNS Lookup</h1>
          <p className="text-text-secondary">Fragen Sie DNS-Einträge ab</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Abfrage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                label="Domain"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="example.com"
                onKeyDown={(e) => e.key === 'Enter' && lookup()}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={lookup} disabled={isLoading} loading={isLoading} icon={<Search className="w-4 h-4" />}>
                Abfragen
              </Button>
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-text-secondary mb-2">Record-Typen</label>
            <div className="flex flex-wrap gap-4">
              {Object.entries(recordTypes).map(([type, enabled]) => (
                <Checkbox
                  key={type}
                  label={type}
                  checked={enabled}
                  onChange={() => toggleRecordType(type)}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Ergebnisse für {results.domain}</CardTitle>
              <span className="text-sm text-text-secondary">{results.duration_ms}ms</span>
            </div>
          </CardHeader>
          <CardContent>
            {results.records.length === 0 ? (
              <p className="text-text-muted text-center py-8">Keine Einträge gefunden</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-default">
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Typ</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Name</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">Wert</th>
                      <th className="text-left py-2 px-3 text-sm font-medium text-text-secondary">TTL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.records.map((record, idx) => (
                      <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                        <td className="py-2 px-3">
                          <span className="px-2 py-1 bg-accent-blue/20 text-accent-blue rounded text-xs font-medium">
                            {record.record_type}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-sm">{record.name}</td>
                        <td className="py-2 px-3 font-mono text-sm break-all">{record.value}</td>
                        <td className="py-2 px-3 text-sm text-text-secondary">{record.ttl}s</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
