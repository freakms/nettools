import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Checkbox, Alert } from '@/components/ui'
import { Key, RefreshCw, Copy, Check } from 'lucide-react'

interface PasswordResult {
  password: string
  strength: string
  entropy_bits: number
}

interface PasswordOptions {
  length: number
  uppercase: boolean
  lowercase: boolean
  numbers: boolean
  symbols: boolean
  exclude_ambiguous: boolean
}

export function PasswordPage() {
  const [options, setOptions] = useState<PasswordOptions>({
    length: 16,
    uppercase: true,
    lowercase: true,
    numbers: true,
    symbols: true,
    exclude_ambiguous: false,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<PasswordResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const generate = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await invoke<PasswordResult>('generate_password', { options })
      setResult(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const copyPassword = async () => {
    if (!result) return
    await navigator.clipboard.writeText(result.password)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const updateOption = <K extends keyof PasswordOptions>(key: K, value: PasswordOptions[K]) => {
    setOptions(prev => ({ ...prev, [key]: value }))
  }

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case 'Sehr stark': return 'text-accent-green'
      case 'Stark': return 'text-accent-green'
      case 'Mittel': return 'text-accent-yellow'
      case 'Schwach': return 'text-accent-red'
      default: return 'text-accent-red'
    }
  }

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Key className="w-8 h-8 text-accent-yellow" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Password Generator</h1>
          <p className="text-text-secondary">Generieren Sie sichere Passwörter</p>
        </div>
      </div>

      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Optionen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Länge: {options.length} Zeichen
              </label>
              <input
                type="range"
                min="4"
                max="64"
                value={options.length}
                onChange={(e) => updateOption('length', parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-text-muted mt-1">
                <span>4</span>
                <span>64</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <Checkbox
                label="Großbuchstaben (A-Z)"
                checked={options.uppercase}
                onChange={(e) => updateOption('uppercase', e.target.checked)}
              />
              <Checkbox
                label="Kleinbuchstaben (a-z)"
                checked={options.lowercase}
                onChange={(e) => updateOption('lowercase', e.target.checked)}
              />
              <Checkbox
                label="Zahlen (0-9)"
                checked={options.numbers}
                onChange={(e) => updateOption('numbers', e.target.checked)}
              />
              <Checkbox
                label="Symbole (!@#$...)"
                checked={options.symbols}
                onChange={(e) => updateOption('symbols', e.target.checked)}
              />
              <Checkbox
                label="Mehrdeutige ausschließen (0,O,l,1)"
                checked={options.exclude_ambiguous}
                onChange={(e) => updateOption('exclude_ambiguous', e.target.checked)}
              />
            </div>

            <Button onClick={generate} disabled={isLoading} loading={isLoading} icon={<RefreshCw className="w-4 h-4" />}>
              Generieren
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {result && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Generiertes Passwort</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3 mb-4">
              <code className="flex-1 text-lg font-mono text-text-primary bg-bg-tertiary px-4 py-3 rounded-lg break-all select-all">
                {result.password}
              </code>
              <Button
                variant="secondary"
                onClick={copyPassword}
                icon={copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
              >
                {copied ? 'Kopiert!' : 'Kopieren'}
              </Button>
              <Button variant="secondary" onClick={generate} icon={<RefreshCw className="w-4 h-4" />}>
                Neu
              </Button>
            </div>
            
            <div className="flex gap-6 text-sm">
              <div>
                <span className="text-text-secondary">Stärke: </span>
                <span className={`font-medium ${getStrengthColor(result.strength)}`}>{result.strength}</span>
              </div>
              <div>
                <span className="text-text-secondary">Entropie: </span>
                <span className="text-text-primary">{result.entropy_bits.toFixed(1)} Bits</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
