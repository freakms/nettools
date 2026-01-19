import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert } from '@/components/ui'
import { Fingerprint, Copy, Check, RefreshCw } from 'lucide-react'

interface MacResult {
  original: string
  formats: {
    colon_upper: string      // AA:BB:CC:DD:EE:FF
    colon_lower: string      // aa:bb:cc:dd:ee:ff
    hyphen_upper: string     // AA-BB-CC-DD-EE-FF
    hyphen_lower: string     // aa-bb-cc-dd-ee-ff
    dot_upper: string        // AABB.CCDD.EEFF
    dot_lower: string        // aabb.ccdd.eeff
    no_separator: string     // AABBCCDDEEFF
    cisco: string            // aabb.ccdd.eeff
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
    // Set locally administered bit and unicast
    bytes[0] = (parseInt(bytes[0], 16) & 0xFC | 0x02).toString(16).padStart(2, '0')
    setMac(bytes.join(':').toUpperCase())
  }

  const FormatRow = ({ label, value, format }: { label: string; value: string; format: string }) => (
    <div className="flex items-center justify-between py-3 border-b border-border-default">
      <span className="text-sm text-text-secondary">{label}</span>
      <div className="flex items-center gap-2">
        <code className="font-mono text-sm text-text-primary bg-bg-tertiary px-3 py-1 rounded">
          {value}
        </code>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => copyToClipboard(value, format)}
          icon={copiedFormat === format ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
        />
      </div>
    </div>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Fingerprint className="w-8 h-8 text-accent-purple" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">MAC Formatter</h1>
          <p className="text-text-secondary">Konvertieren und formatieren Sie MAC-Adressen</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>MAC-Adresse eingeben</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                label="MAC-Adresse"
                value={mac}
                onChange={(e) => setMac(e.target.value)}
                placeholder="AA:BB:CC:DD:EE:FF oder AABBCCDDEEFF"
                onKeyDown={(e) => e.key === 'Enter' && formatMac()}
              />
            </div>
            <div className="flex items-end gap-2">
              <Button onClick={formatMac} disabled={isLoading} loading={isLoading} icon={<Fingerprint className="w-4 h-4" />}>
                Formatieren
              </Button>
              <Button variant="secondary" onClick={generateRandomMac} icon={<RefreshCw className="w-4 h-4" />}>
                Zufällig
              </Button>
            </div>
          </div>
          
          <div className="mt-3 text-xs text-text-muted">
            Unterstützte Formate: AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF, AABB.CCDD.EEFF, AABBCCDDEEFF
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && results.is_valid && (
        <>
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>Formatierte Ausgaben</CardTitle>
            </CardHeader>
            <CardContent>
              <FormatRow label="Doppelpunkt (Groß)" value={results.formats.colon_upper} format="colon_upper" />
              <FormatRow label="Doppelpunkt (Klein)" value={results.formats.colon_lower} format="colon_lower" />
              <FormatRow label="Bindestrich (Groß)" value={results.formats.hyphen_upper} format="hyphen_upper" />
              <FormatRow label="Bindestrich (Klein)" value={results.formats.hyphen_lower} format="hyphen_lower" />
              <FormatRow label="Cisco-Format" value={results.formats.cisco} format="cisco" />
              <FormatRow label="Ohne Trennzeichen" value={results.formats.no_separator} format="no_separator" />
            </CardContent>
          </Card>

          {results.vendor && (
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>Hersteller (OUI Lookup)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-accent-purple/20 rounded-lg flex items-center justify-center">
                    <Fingerprint className="w-6 h-6 text-accent-purple" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-text-primary">{results.vendor}</p>
                    <p className="text-sm text-text-secondary">OUI: {results.formats.colon_upper.substring(0, 8)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
