import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert } from '@/components/ui'
import { Calculator } from 'lucide-react'

interface SubnetInfo {
  network: string
  broadcast: string
  netmask: string
  wildcard_mask: string
  first_host: string
  last_host: string
  total_hosts: number
  usable_hosts: number
  cidr: number
  ip_class: string
  is_private: boolean
}

export function SubnetPage() {
  const [cidr, setCidr] = useState('192.168.1.0/24')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<SubnetInfo | null>(null)
  const [error, setError] = useState<string | null>(null)

  const calculate = async () => {
    if (!cidr) {
      setError('Bitte geben Sie eine CIDR-Notation ein')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await invoke<SubnetInfo>('calculate_subnet', { cidr })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const quickSelect = (prefix: number) => {
    const parts = cidr.split('/')
    setCidr(`${parts[0]}/${prefix}`)
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Calculator className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Subnet Calculator</h1>
          <p className="text-text-secondary">Berechnen Sie Subnetz-Informationen</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Eingabe</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                label="CIDR-Notation"
                value={cidr}
                onChange={(e) => setCidr(e.target.value)}
                placeholder="192.168.1.0/24"
                onKeyDown={(e) => e.key === 'Enter' && calculate()}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={calculate} disabled={isLoading} loading={isLoading} icon={<Calculator className="w-4 h-4" />}>
                Berechnen
              </Button>
            </div>
          </div>
          
          <div className="mt-3">
            <label className="block text-sm text-text-secondary mb-2">Schnellauswahl Präfix</label>
            <div className="flex flex-wrap gap-2">
              {[8, 16, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30].map(prefix => (
                <Button key={prefix} variant="ghost" size="sm" onClick={() => quickSelect(prefix)}>
                  /{prefix}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Ergebnisse</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Netzwerk-Adresse</span>
                  <span className="font-mono text-text-primary">{results.network}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Broadcast-Adresse</span>
                  <span className="font-mono text-text-primary">{results.broadcast}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Subnetzmaske</span>
                  <span className="font-mono text-text-primary">{results.netmask}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Wildcard-Maske</span>
                  <span className="font-mono text-text-primary">{results.wildcard_mask}</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Erster Host</span>
                  <span className="font-mono text-text-primary">{results.first_host}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Letzter Host</span>
                  <span className="font-mono text-text-primary">{results.last_host}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Nutzbare Hosts</span>
                  <span className="font-mono text-accent-green">{results.usable_hosts.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">IP-Klasse</span>
                  <span className="text-text-primary">{results.ip_class}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Privates Netzwerk</span>
                  <span className={results.is_private ? 'text-accent-green' : 'text-accent-yellow'}>
                    {results.is_private ? 'Ja' : 'Nein'}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
