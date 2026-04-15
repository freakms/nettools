import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Search, Globe, Calendar, Server, Copy, Check } from 'lucide-react'

interface WhoisResult {
  domain: string
  registrar: string | null
  creation_date: string | null
  expiration_date: string | null
  name_servers: string[]
  status: string[]
  raw_data: string
}

export function WhoisPage() {
  const [domain, setDomain] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<WhoisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showRaw, setShowRaw] = useState(false)
  const [copied, setCopied] = useState(false)

  const lookup = async () => {
    if (!domain.trim()) {
      setError('Bitte geben Sie eine Domain ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const result = await invoke<WhoisResult>('lookup_whois', { domain: domain.trim() })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const copyRaw = async () => {
    if (!results) return
    await navigator.clipboard.writeText(results.raw_data)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const InfoRow = ({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | null }) => {
    if (!value) return null
    return (
      <div className="flex items-start gap-3 py-3 border-b border-border-default">
        <div className="text-text-muted mt-0.5">{icon}</div>
        <div className="flex-1">
          <p className="text-sm text-text-secondary">{label}</p>
          <p className="text-text-primary font-medium">{value}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Search className="w-8 h-8 text-accent-purple" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">WHOIS Lookup</h1>
          <p className="text-text-secondary">Rufen Sie Domain-Registrierungsinformationen ab</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Domain-Abfrage</CardTitle>
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
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <>
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>Ergebnisse für {results.domain}</CardTitle>
            </CardHeader>
            <CardContent>
              <InfoRow 
                icon={<Globe className="w-4 h-4" />} 
                label="Registrar" 
                value={results.registrar} 
              />
              <InfoRow 
                icon={<Calendar className="w-4 h-4" />} 
                label="Erstellt am" 
                value={results.creation_date} 
              />
              <InfoRow 
                icon={<Calendar className="w-4 h-4" />} 
                label="Läuft ab am" 
                value={results.expiration_date} 
              />
              
              {results.name_servers.length > 0 && (
                <div className="py-3 border-b border-border-default">
                  <div className="flex items-center gap-2 mb-2">
                    <Server className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-secondary">Nameserver</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {results.name_servers.map((ns, idx) => (
                      <Badge key={idx} variant="default">{ns}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {results.status.length > 0 && (
                <div className="py-3">
                  <p className="text-sm text-text-secondary mb-2">Status</p>
                  <div className="flex flex-wrap gap-2">
                    {results.status.slice(0, 5).map((s, idx) => (
                      <Badge key={idx} variant="info">{s.split(' ')[0]}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card variant="bordered">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Raw WHOIS Daten</CardTitle>
                <div className="flex gap-2">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setShowRaw(!showRaw)}
                  >
                    {showRaw ? 'Ausblenden' : 'Anzeigen'}
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={copyRaw}
                    icon={copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
                  >
                    {copied ? 'Kopiert!' : 'Kopieren'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            {showRaw && (
              <CardContent>
                <pre className="bg-bg-tertiary p-4 rounded-lg overflow-x-auto text-xs font-mono text-text-secondary whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {results.raw_data}
                </pre>
              </CardContent>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
