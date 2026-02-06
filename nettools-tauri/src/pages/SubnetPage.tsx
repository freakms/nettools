import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Calculator, ChevronDown, ChevronUp, Copy, Check, Network } from 'lucide-react'

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

interface SplitOption {
  prefix: number
  subnets: number
  hostsPerSubnet: number
}

interface SubnetSplit {
  network: string
  broadcast: string
  firstHost: string
  lastHost: string
  usableHosts: number
}

export function SubnetPage() {
  const [cidr, setCidr] = useState('192.168.1.0/24')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<SubnetInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Split functionality
  const [showSplitOptions, setShowSplitOptions] = useState(false)
  const [splitOptions, setSplitOptions] = useState<SplitOption[]>([])
  const [selectedSplitPrefix, setSelectedSplitPrefix] = useState<number | null>(null)
  const [splitResults, setSplitResults] = useState<SubnetSplit[]>([])
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const calculate = async () => {
    if (!cidr) {
      setError('Bitte geben Sie eine CIDR-Notation ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setSplitResults([])
    setSelectedSplitPrefix(null)

    try {
      const result = await invoke<SubnetInfo>('calculate_subnet', { cidr })
      setResults(result)
      
      // Calculate available split options
      const currentPrefix = result.cidr
      const options: SplitOption[] = []
      
      for (let newPrefix = currentPrefix + 1; newPrefix <= 30; newPrefix++) {
        const subnets = Math.pow(2, newPrefix - currentPrefix)
        const hostsPerSubnet = Math.pow(2, 32 - newPrefix) - 2
        if (hostsPerSubnet >= 2) {
          options.push({ prefix: newPrefix, subnets, hostsPerSubnet })
        }
      }
      
      setSplitOptions(options)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const splitNetwork = () => {
    if (!results || !selectedSplitPrefix) return
    
    // Parse the network address
    const networkParts = results.network.split('/')[0].split('.').map(Number)
    const networkInt = (networkParts[0] << 24) | (networkParts[1] << 16) | (networkParts[2] << 8) | networkParts[3]
    
    const currentPrefix = results.cidr
    const newPrefix = selectedSplitPrefix
    const numSubnets = Math.pow(2, newPrefix - currentPrefix)
    const subnetSize = Math.pow(2, 32 - newPrefix)
    
    const subnets: SubnetSplit[] = []
    
    for (let i = 0; i < numSubnets; i++) {
      const subnetStart = networkInt + (i * subnetSize)
      const subnetEnd = subnetStart + subnetSize - 1
      
      const intToIp = (num: number): string => {
        return [
          (num >>> 24) & 255,
          (num >>> 16) & 255,
          (num >>> 8) & 255,
          num & 255
        ].join('.')
      }
      
      subnets.push({
        network: `${intToIp(subnetStart)}/${newPrefix}`,
        broadcast: intToIp(subnetEnd),
        firstHost: intToIp(subnetStart + 1),
        lastHost: intToIp(subnetEnd - 1),
        usableHosts: subnetSize - 2
      })
    }
    
    setSplitResults(subnets)
  }

  const quickSelect = (prefix: number) => {
    const parts = cidr.split('/')
    const ip = parts[0] || '192.168.1.0'
    setCidr(`${ip}/${prefix}`)
  }

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const copyAllSubnets = async () => {
    const text = splitResults.map(s => s.network).join('\n')
    await navigator.clipboard.writeText(text)
    setCopiedIndex(-1)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Calculator className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Subnet Calculator</h1>
          <p className="text-text-secondary">Calculate subnet information from CIDR notation</p>
        </div>
      </div>

      {/* Input Section */}
      <Card variant="bordered">
        <CardContent className="pt-6">
          <p className="text-sm text-text-secondary mb-2">Enter Network in CIDR Notation:</p>
          <p className="text-xs text-text-muted mb-3">Examples: 192.168.1.0/24, 10.0.0.0/8, 172.16.0.0/16</p>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                value={cidr}
                onChange={(e) => setCidr(e.target.value)}
                placeholder="192.168.1.0/24"
                onKeyDown={(e) => e.key === 'Enter' && calculate()}
                className="font-mono"
              />
            </div>
          </div>
          
          <div className="mt-4 flex justify-center">
            <Button onClick={calculate} disabled={isLoading} loading={isLoading} icon={<Calculator className="w-4 h-4" />} size="lg">
              Calculate
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Subnet Splitter Section */}
      {results && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Network className="w-5 h-5 text-accent-purple" />
              <CardTitle>Subnet Splitter</CardTitle>
            </div>
            <p className="text-sm text-text-muted">Split a network into smaller subnets of equal size</p>
          </CardHeader>
          <CardContent>
            {!showSplitOptions ? (
              <div className="p-4 bg-bg-tertiary rounded-lg text-center text-text-muted">
                Enter a network above and click 'Show Options' to see available splits
              </div>
            ) : splitOptions.length === 0 ? (
              <div className="p-4 bg-bg-tertiary rounded-lg text-center text-text-muted">
                No split options available for this network
              </div>
            ) : (
              <div className="overflow-x-auto max-h-48 overflow-y-auto mb-4">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-bg-secondary">
                    <tr className="border-b border-border-default">
                      <th className="text-left py-2 px-3 text-text-secondary">Prefix</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Anzahl Subnetze</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Hosts/Subnetz</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Auswahl</th>
                    </tr>
                  </thead>
                  <tbody>
                    {splitOptions.map((opt) => (
                      <tr 
                        key={opt.prefix} 
                        className={`border-b border-border-default hover:bg-bg-hover cursor-pointer ${selectedSplitPrefix === opt.prefix ? 'bg-accent-purple/10' : ''}`}
                        onClick={() => setSelectedSplitPrefix(opt.prefix)}
                      >
                        <td className="py-2 px-3 font-mono">/{opt.prefix}</td>
                        <td className="py-2 px-3">{opt.subnets.toLocaleString()}</td>
                        <td className="py-2 px-3">{opt.hostsPerSubnet.toLocaleString()}</td>
                        <td className="py-2 px-3">
                          <input
                            type="radio"
                            name="splitPrefix"
                            checked={selectedSplitPrefix === opt.prefix}
                            onChange={() => setSelectedSplitPrefix(opt.prefix)}
                            className="accent-accent-purple"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="flex gap-2 items-center">
              <Button 
                variant="secondary" 
                onClick={() => setShowSplitOptions(!showSplitOptions)}
                icon={showSplitOptions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              >
                {showSplitOptions ? 'Hide Options' : 'Show Split Options'}
              </Button>
              
              {showSplitOptions && selectedSplitPrefix && (
                <>
                  <span className="text-text-muted">Split into subnets with prefix:</span>
                  <Badge variant="info">/{selectedSplitPrefix}</Badge>
                  <Button onClick={splitNetwork} icon={<Network className="w-4 h-4" />}>
                    Split Network
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Split Results */}
      {splitResults.length > 0 && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-accent-purple">Split Results ({splitResults.length} Subnetze)</CardTitle>
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={copyAllSubnets}
                icon={copiedIndex === -1 ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
              >
                {copiedIndex === -1 ? 'Kopiert!' : 'Alle kopieren'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-bg-secondary">
                  <tr className="border-b border-border-default">
                    <th className="text-left py-2 px-3 text-text-secondary">#</th>
                    <th className="text-left py-2 px-3 text-text-secondary">Netzwerk</th>
                    <th className="text-left py-2 px-3 text-text-secondary">Erster Host</th>
                    <th className="text-left py-2 px-3 text-text-secondary">Letzter Host</th>
                    <th className="text-left py-2 px-3 text-text-secondary">Broadcast</th>
                    <th className="text-left py-2 px-3 text-text-secondary">Hosts</th>
                    <th className="text-left py-2 px-3 text-text-secondary"></th>
                  </tr>
                </thead>
                <tbody>
                  {splitResults.map((subnet, idx) => (
                    <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                      <td className="py-2 px-3 text-text-muted">{idx + 1}</td>
                      <td className="py-2 px-3 font-mono text-accent-green">{subnet.network}</td>
                      <td className="py-2 px-3 font-mono">{subnet.firstHost}</td>
                      <td className="py-2 px-3 font-mono">{subnet.lastHost}</td>
                      <td className="py-2 px-3 font-mono text-text-muted">{subnet.broadcast}</td>
                      <td className="py-2 px-3">{subnet.usableHosts}</td>
                      <td className="py-2 px-3">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => copyToClipboard(subnet.network, idx)}
                        >
                          {copiedIndex === idx ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subnet Information */}
      {results && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="text-accent-blue">Subnet Information</CardTitle>
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
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">CIDR-Notation</span>
                  <span className="font-mono text-accent-blue">/{results.cidr}</span>
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
                  <span className="text-text-secondary">Gesamte Adressen</span>
                  <span className="font-mono text-text-primary">{results.total_hosts.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Nutzbare Hosts</span>
                  <span className="font-mono text-accent-green font-bold">{results.usable_hosts.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">IP-Klasse</span>
                  <span className="text-text-primary">{results.ip_class}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border-default">
                  <span className="text-text-secondary">Privates Netzwerk</span>
                  <Badge variant={results.is_private ? 'success' : 'warning'}>
                    {results.is_private ? 'Ja (RFC 1918)' : 'Nein (Öffentlich)'}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Reference */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Quick Reference - CIDR Präfixe</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {[
              { prefix: 8, hosts: '16.7M', name: 'Class A' },
              { prefix: 16, hosts: '65,534', name: 'Class B' },
              { prefix: 24, hosts: '254', name: 'Class C' },
              { prefix: 25, hosts: '126', name: '' },
              { prefix: 26, hosts: '62', name: '' },
              { prefix: 27, hosts: '30', name: '' },
              { prefix: 28, hosts: '14', name: '' },
              { prefix: 29, hosts: '6', name: '' },
              { prefix: 30, hosts: '2', name: 'Point-to-Point' },
            ].map(item => (
              <Button 
                key={item.prefix} 
                variant="ghost" 
                size="sm" 
                onClick={() => quickSelect(item.prefix)}
                className="flex-col h-auto py-2"
              >
                <span className="font-mono text-accent-blue">/{item.prefix}</span>
                <span className="text-xs text-text-muted">{item.hosts} hosts</span>
                {item.name && <span className="text-xs text-accent-purple">{item.name}</span>}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
