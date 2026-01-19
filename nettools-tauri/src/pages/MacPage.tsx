import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert } from '@/components/ui'
import { Fingerprint, Copy, Check, RefreshCw } from 'lucide-react'

interface MacResult {
  original: string
  formats: {
    colon_upper: string
    colon_lower: string
    hyphen_upper: string
    hyphen_lower: string
    dot_upper: string
    dot_lower: string
    no_separator: string
    cisco: string
  }
  vendor: string | null
  is_valid: boolean
}

export function MacPage() {
  const [mac, setMac] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<MacResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copiedFormat, setCopiedFormat] = useState<string | null>(null)

  const formatMac = async () => {
    if (!mac.trim()) {
      setError('Bitte geben Sie eine MAC-Adresse ein')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await invoke<MacResult>('format_mac', { mac: mac.trim() })
      setResults(result)
      if (!result.is_valid) {
        setError('Ungültiges MAC-Adressformat')
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (value: string, format: string) => {
    await navigator.clipboard.writeText(value)
    setCopiedFormat(format)
    setTimeout(() => setCopiedFormat(null), 2000)
  }

  const generateRandomMac = () => {
    const bytes = Array.from({ length: 6 }, () => 
      Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
    )
    bytes[0] = (parseInt(bytes[0], 16) & 0xFC | 0x02).toString(16).padStart(2, '0')
    setMac(bytes.join(':').toUpperCase())
  }

  // Generate switch commands from MAC
  const generateSwitchCommands = (macAddress: string) => {
    if (!results?.is_valid) return null
    
    const plain = results.formats.no_separator.toLowerCase()
    const colonLower = results.formats.colon_lower
    const hyphenLower = results.formats.hyphen_lower
    const cisco = results.formats.cisco
    
    return {
      extreme: `show fdb ${colonLower}`,
      huawei: `display mac-address ${hyphenLower}`,
      huaweiAccessUser: `display access-user mac-address ${hyphenLower}`,
      dell: `show mac address-table address ${colonLower}`,
      cisco: `show mac address-table address ${cisco}`,
      juniper: `show ethernet-switching table | match ${colonLower}`,
      aruba: `show mac-address ${colonLower}`,
    }
  }

  const switchCommands = generateSwitchCommands(mac)

  const FormatRow = ({ label, value, format }: { label: string; value: string; format: string }) => (
    <div className="flex items-center gap-4 py-3">
      <span className="text-sm text-text-secondary w-36 shrink-0">{label}:</span>
      <div className="flex-1 bg-bg-tertiary rounded-lg px-4 py-2">
        <code className="font-mono text-sm text-text-primary">{value || '-'}</code>
      </div>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => copyToClipboard(value, format)}
        disabled={!value}
      >
        {copiedFormat === format ? <Check className="w-4 h-4 text-accent-green" /> : 'Copy'}
      </Button>
    </div>
  )

  const CommandRow = ({ label, value, format }: { label: string; value: string; format: string }) => (
    <div className="flex items-center gap-4 py-3">
      <span className="text-sm text-text-secondary w-44 shrink-0">{label}:</span>
      <div className="flex-1 bg-bg-tertiary rounded-lg px-4 py-2">
        <code className="font-mono text-sm text-accent-green">{value || '-'}</code>
      </div>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => copyToClipboard(value, format)}
        disabled={!value}
      >
        {copiedFormat === format ? <Check className="w-4 h-4 text-accent-green" /> : 'Copy'}
      </Button>
    </div>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Fingerprint className="w-8 h-8 text-accent-purple" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">MAC Formatter</h1>
          <p className="text-text-secondary">Konvertieren Sie MAC-Adressen in verschiedene Formate</p>
        </div>
      </div>

      {/* Input */}
      <Card variant="bordered">
        <CardContent className="pt-6">
          <label className="block text-sm font-medium text-text-primary mb-2">
            Enter MAC Address:
          </label>
          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                value={mac}
                onChange={(e) => setMac(e.target.value)}
                placeholder="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF"
                onKeyDown={(e) => e.key === 'Enter' && formatMac()}
              />
            </div>
            <Button onClick={formatMac} disabled={isLoading} loading={isLoading} icon={<Fingerprint className="w-4 h-4" />}>
              Format
            </Button>
            <Button variant="secondary" onClick={generateRandomMac} icon={<RefreshCw className="w-4 h-4" />}>
              Random
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Vendor Info */}
      {results?.is_valid && results.vendor && (
        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-accent-purple/20 rounded-lg flex items-center justify-center">
                <Fingerprint className="w-6 h-6 text-accent-purple" />
              </div>
              <div>
                <p className="text-sm text-text-secondary">Hersteller (OUI Lookup)</p>
                <p className="text-lg font-medium text-text-primary">{results.vendor}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Standard MAC Formats */}
      {results?.is_valid && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="text-accent-purple">Standard MAC Formats</CardTitle>
          </CardHeader>
          <CardContent>
            <FormatRow label="Format 1 (Plain)" value={results.formats.no_separator} format="plain" />
            <FormatRow label="Format 2 (Colon)" value={results.formats.colon_upper} format="colon" />
            <FormatRow label="Format 3 (Dash-4)" value={results.formats.cisco.toUpperCase()} format="dash4" />
            <FormatRow label="Format 4 (Dash-2)" value={results.formats.hyphen_upper} format="dash2" />
            <FormatRow label="Cisco Format" value={results.formats.cisco} format="cisco" />
            <FormatRow label="Lowercase Colon" value={results.formats.colon_lower} format="colon_lower" />
          </CardContent>
        </Card>
      )}

      {/* Switch Commands */}
      {results?.is_valid && switchCommands && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="text-accent-orange">Switch Commands</CardTitle>
          </CardHeader>
          <CardContent>
            <CommandRow label="EXTREME CLI" value={switchCommands.extreme} format="extreme" />
            <CommandRow label="Huawei CLI" value={switchCommands.huawei} format="huawei" />
            <CommandRow label="Huawei Access-User CLI" value={switchCommands.huaweiAccessUser} format="huawei_access" />
            <CommandRow label="Dell CLI" value={switchCommands.dell} format="dell" />
            <CommandRow label="Cisco CLI" value={switchCommands.cisco} format="cisco_cmd" />
            <CommandRow label="Juniper CLI" value={switchCommands.juniper} format="juniper" />
            <CommandRow label="Aruba CLI" value={switchCommands.aruba} format="aruba" />
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!results && !error && (
        <Card variant="bordered">
          <CardContent className="py-16 text-center">
            <Fingerprint className="w-16 h-16 mx-auto mb-4 text-text-muted" />
            <h3 className="text-lg font-medium text-text-primary mb-2">Keine MAC-Adresse eingegeben</h3>
            <p className="text-text-secondary">
              Geben Sie eine MAC-Adresse ein und klicken Sie auf "Format"
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
