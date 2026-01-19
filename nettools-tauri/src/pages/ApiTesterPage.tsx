import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge } from '@/components/ui'
import { Send, Plus, Trash2, Copy, Check, Clock } from 'lucide-react'

interface Header {
  key: string
  value: string
}

interface ApiResponse {
  status: number
  status_text: string
  headers: Record<string, string>
  body: string
  duration_ms: number
}

export function ApiTesterPage() {
  const [method, setMethod] = useState<'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'>('GET')
  const [url, setUrl] = useState('')
  const [headers, setHeaders] = useState<Header[]>([{ key: 'Content-Type', value: 'application/json' }])
  const [body, setBody] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<ApiResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState<'body' | 'headers'>('body')

  const sendRequest = async () => {
    if (!url.trim()) {
      setError('Bitte geben Sie eine URL ein')
      return
    }

    setIsLoading(true)
    setError(null)
    setResponse(null)

    const start = Date.now()

    try {
      const headerObj: Record<string, string> = {}
      headers.forEach(h => {
        if (h.key && h.value) headerObj[h.key] = h.value
      })

      const result = await invoke<ApiResponse>('send_http_request', {
        method,
        url: url.trim(),
        headers: headerObj,
        body: ['POST', 'PUT', 'PATCH'].includes(method) ? body : null,
      })

      setResponse({
        ...result,
        duration_ms: Date.now() - start,
      })
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const addHeader = () => {
    setHeaders([...headers, { key: '', value: '' }])
  }

  const removeHeader = (index: number) => {
    setHeaders(headers.filter((_, i) => i !== index))
  }

  const updateHeader = (index: number, field: 'key' | 'value', value: string) => {
    const newHeaders = [...headers]
    newHeaders[index][field] = value
    setHeaders(newHeaders)
  }

  const copyResponse = async () => {
    if (!response) return
    await navigator.clipboard.writeText(response.body)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return 'success'
    if (status >= 300 && status < 400) return 'info'
    if (status >= 400 && status < 500) return 'warning'
    return 'error'
  }

  const formatJson = (str: string) => {
    try {
      return JSON.stringify(JSON.parse(str), null, 2)
    } catch {
      return str
    }
  }

  const MethodButton = ({ m }: { m: typeof method }) => (
    <button
      onClick={() => setMethod(m)}
      className={`px-3 py-2 text-sm font-medium rounded transition-colors ${
        method === m 
          ? m === 'GET' ? 'bg-accent-green text-white'
          : m === 'POST' ? 'bg-accent-blue text-white'
          : m === 'PUT' ? 'bg-accent-yellow text-black'
          : m === 'DELETE' ? 'bg-accent-red text-white'
          : 'bg-accent-purple text-white'
          : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
      }`}
    >
      {m}
    </button>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Send className="w-8 h-8 text-accent-blue" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">API Tester</h1>
          <p className="text-text-secondary">Testen Sie HTTP-Requests</p>
        </div>
      </div>

      {/* Request Configuration */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>Request</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Method & URL */}
          <div className="flex gap-2 mb-4">
            <div className="flex gap-1 p-1 bg-bg-tertiary rounded-lg">
              <MethodButton m="GET" />
              <MethodButton m="POST" />
              <MethodButton m="PUT" />
              <MethodButton m="DELETE" />
              <MethodButton m="PATCH" />
            </div>
          </div>

          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://api.example.com/endpoint"
                onKeyDown={(e) => e.key === 'Enter' && sendRequest()}
              />
            </div>
            <Button onClick={sendRequest} disabled={isLoading} loading={isLoading} icon={<Send className="w-4 h-4" />}>
              Senden
            </Button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-4 border-b border-border-default">
            <button
              onClick={() => setActiveTab('headers')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'headers' 
                  ? 'border-accent-blue text-accent-blue' 
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              Headers ({headers.filter(h => h.key).length})
            </button>
            <button
              onClick={() => setActiveTab('body')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'body' 
                  ? 'border-accent-blue text-accent-blue' 
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              Body
            </button>
          </div>

          {/* Headers Tab */}
          {activeTab === 'headers' && (
            <div className="space-y-2">
              {headers.map((header, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={header.key}
                    onChange={(e) => updateHeader(index, 'key', e.target.value)}
                    placeholder="Header-Name"
                    className="flex-1"
                  />
                  <Input
                    value={header.value}
                    onChange={(e) => updateHeader(index, 'value', e.target.value)}
                    placeholder="Wert"
                    className="flex-1"
                  />
                  <Button variant="ghost" size="sm" onClick={() => removeHeader(index)} icon={<Trash2 className="w-4 h-4" />} />
                </div>
              ))}
              <Button variant="ghost" size="sm" onClick={addHeader} icon={<Plus className="w-4 h-4" />}>
                Header hinzufügen
              </Button>
            </div>
          )}

          {/* Body Tab */}
          {activeTab === 'body' && (
            <div>
              {['POST', 'PUT', 'PATCH'].includes(method) ? (
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder='{"key": "value"}'
                  className="w-full h-40 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm font-mono text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue resize-none"
                />
              ) : (
                <p className="text-text-muted text-sm py-4 text-center">
                  Body ist nur für POST, PUT und PATCH verfügbar
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}

      {/* Response */}
      {response && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CardTitle>Response</CardTitle>
                <Badge variant={getStatusColor(response.status)}>
                  {response.status} {response.status_text}
                </Badge>
                <div className="flex items-center gap-1 text-sm text-text-secondary">
                  <Clock className="w-4 h-4" />
                  {response.duration_ms}ms
                </div>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={copyResponse}
                icon={copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
              >
                {copied ? 'Kopiert!' : 'Kopieren'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="bg-bg-tertiary p-4 rounded-lg overflow-x-auto text-sm font-mono text-text-primary whitespace-pre-wrap max-h-96 overflow-y-auto">
              {formatJson(response.body)}
            </pre>

            {Object.keys(response.headers).length > 0 && (
              <div className="mt-4 pt-4 border-t border-border-default">
                <p className="text-sm font-medium text-text-secondary mb-2">Response Headers</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(response.headers).slice(0, 10).map(([key, value]) => (
                    <div key={key} className="flex gap-2">
                      <span className="text-text-muted">{key}:</span>
                      <span className="text-text-primary truncate">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
