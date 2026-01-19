import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { ShieldCheck, Lock, Calendar, AlertTriangle, CheckCircle } from 'lucide-react'

interface SslCertificate {
  subject: string
  issuer: string
  valid_from: string
  valid_to: string
  serial_number: string
  is_valid: boolean
  days_until_expiry: number
  san: string[]
}

interface SslCheckResult {
  host: string
  port: number
  certificate: SslCertificate | null
  error: string | null
  protocol_version: string | null
}

export function SslPage() {
  const [host, setHost] = useState('')
  const [port, setPort] = useState('443')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<SslCheckResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const checkSsl = async () => {
    if (!host.trim()) {
      setError('Bitte geben Sie einen Hostnamen ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const result = await invoke<SslCheckResult>('check_ssl', { 
        host: host.trim().replace(/^https?:\/\//, ''), 
        port: parseInt(port) 
      })
      setResults(result)
      if (result.error) {
        setError(result.error)
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const getExpiryColor = (days: number) => {
    if (days <= 0) return 'text-accent-red'
    if (days <= 30) return 'text-accent-yellow'
    return 'text-accent-green'
  }

  const getExpiryBadge = (days: number) => {
    if (days <= 0) return { variant: 'error' as const, text: 'Abgelaufen' }
    if (days <= 7) return { variant: 'error' as const, text: `${days} Tage` }
    if (days <= 30) return { variant: 'warning' as const, text: `${days} Tage` }
    return { variant: 'success' as const, text: `${days} Tage` }
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('de-DE', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateStr
    }
  }

  const parseCN = (subject: string) => {
    const match = subject.match(/CN=([^,]+)/)
    return match ? match[1] : subject
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <ShieldCheck className="w-8 h-8 text-accent-green" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">SSL Checker</h1>
          <p className="text-text-secondary">Überprüfen Sie SSL/TLS-Zertifikate</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Host eingeben</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                label="Hostname"
                value={host}
                onChange={(e) => setHost(e.target.value)}
                placeholder="example.com oder https://example.com"
                onKeyDown={(e) => e.key === 'Enter' && checkSsl()}
              />
            </div>
            <div className="w-24">
              <Input
                label="Port"
                type="number"
                value={port}
                onChange={(e) => setPort(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={checkSsl} disabled={isLoading} loading={isLoading} icon={<Lock className="w-4 h-4" />}>
                Prüfen
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && results.certificate && (
        <>
          {/* Status Overview */}
          <Card variant="bordered">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                {results.certificate.is_valid ? (
                  <div className="w-16 h-16 bg-accent-green/20 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-accent-green" />
                  </div>
                ) : (
                  <div className="w-16 h-16 bg-accent-red/20 rounded-full flex items-center justify-center">
                    <AlertTriangle className="w-8 h-8 text-accent-red" />
                  </div>
                )}
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-text-primary">
                    {results.certificate.is_valid ? 'Zertifikat gültig' : 'Zertifikat ungültig'}
                  </h2>
                  <p className="text-text-secondary">{parseCN(results.certificate.subject)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-secondary">Gültig noch</p>
                  <p className={`text-2xl font-bold ${getExpiryColor(results.certificate.days_until_expiry)}`}>
                    {results.certificate.days_until_expiry} Tage
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Certificate Details */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>Zertifikat-Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-secondary mb-1">Subject (CN)</p>
                    <p className="font-mono text-sm text-text-primary break-all">{parseCN(results.certificate.subject)}</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-secondary mb-1">Aussteller</p>
                    <p className="font-mono text-sm text-text-primary break-all">{parseCN(results.certificate.issuer)}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3 p-4 bg-bg-tertiary rounded-lg">
                    <Calendar className="w-5 h-5 text-text-muted mt-0.5" />
                    <div>
                      <p className="text-sm text-text-secondary">Gültig ab</p>
                      <p className="text-text-primary">{formatDate(results.certificate.valid_from)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-4 bg-bg-tertiary rounded-lg">
                    <Calendar className="w-5 h-5 text-text-muted mt-0.5" />
                    <div>
                      <p className="text-sm text-text-secondary">Gültig bis</p>
                      <p className="text-text-primary">{formatDate(results.certificate.valid_to)}</p>
                      <Badge variant={getExpiryBadge(results.certificate.days_until_expiry).variant} className="mt-1">
                        {getExpiryBadge(results.certificate.days_until_expiry).text}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Seriennummer</p>
                  <p className="font-mono text-xs text-text-primary break-all">{results.certificate.serial_number}</p>
                </div>

                {results.protocol_version && (
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-secondary mb-1">Protokoll</p>
                    <Badge variant="info">{results.protocol_version}</Badge>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
