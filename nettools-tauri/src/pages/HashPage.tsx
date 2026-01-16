import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert } from '@/components/ui'
import { Hash, Copy, Check } from 'lucide-react'

interface HashResult {
  input: string
  input_type: string
  md5: string
  sha1: string
  sha256: string
  sha512: string
}

export function HashPage() {
  const [text, setText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<HashResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copiedHash, setCopiedHash] = useState<string | null>(null)

  const generateHashes = async () => {
    if (!text) {
      setError('Bitte geben Sie Text ein')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await invoke<HashResult>('generate_hashes', { text })
      setResults(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const copyHash = async (hash: string, name: string) => {
    await navigator.clipboard.writeText(hash)
    setCopiedHash(name)
    setTimeout(() => setCopiedHash(null), 2000)
  }

  const HashRow = ({ name, value }: { name: string; value: string }) => (
    <div className="flex items-center gap-3 py-3 border-b border-border-default">
      <span className="w-20 text-sm font-medium text-text-secondary">{name}</span>
      <code className="flex-1 text-sm font-mono text-text-primary bg-bg-tertiary px-3 py-2 rounded break-all">
        {value}
      </code>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => copyHash(value, name)}
        icon={copiedHash === name ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
      />
    </div>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Hash className="w-8 h-8 text-accent-yellow" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Hash Generator</h1>
          <p className="text-text-secondary">Erzeugen Sie Hash-Werte für Text</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Eingabe</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Text</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Geben Sie hier den Text ein, der gehasht werden soll..."
                className="w-full h-32 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue resize-none"
              />
            </div>
            <Button onClick={generateHashes} disabled={isLoading} loading={isLoading} icon={<Hash className="w-4 h-4" />}>
              Hash generieren
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {results && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Hash-Werte</CardTitle>
          </CardHeader>
          <CardContent>
            <HashRow name="MD5" value={results.md5} />
            <HashRow name="SHA-1" value={results.sha1} />
            <HashRow name="SHA-256" value={results.sha256} />
            <HashRow name="SHA-512" value={results.sha512} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
