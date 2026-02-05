import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Checkbox } from '@/components/ui'
import { Shield, Copy, Check, Download } from 'lucide-react'

interface AddressObject {
  name: string
  type: 'ip-netmask' | 'ip-range' | 'fqdn'
  value: string
  description: string
}

interface ServiceObject {
  name: string
  protocol: 'tcp' | 'udp'
  port: string
  description: string
}

interface SecurityRule {
  name: string
  source_zone: string
  dest_zone: string
  source_addresses: string[]
  dest_addresses: string[]
  services: string[]
  action: 'allow' | 'deny' | 'drop'
  log_start: boolean
  log_end: boolean
}

type NameFormat = 'ipaddress_name' | 'name_ipaddress' | 'custom_prefix' | 'ip_only'

export function PanosPage() {
  const [activeTab, setActiveTab] = useState<'address' | 'service' | 'rule'>('address')
  const [copied, setCopied] = useState(false)
  
  // Shared Objects (default: true)
  const [isShared, setIsShared] = useState(true)
  
  // Name Format
  const [nameFormat, setNameFormat] = useState<NameFormat>('ipaddress_name')
  const [customPrefix, setCustomPrefix] = useState('')
  
  // Address Object State
  const [addressObj, setAddressObj] = useState<AddressObject>({
    name: '',
    type: 'ip-netmask',
    value: '',
    description: ''
  })
  
  // Service Object State
  const [serviceObj, setServiceObj] = useState<ServiceObject>({
    name: '',
    protocol: 'tcp',
    port: '',
    description: ''
  })
  
  // Security Rule State
  const [rule, setRule] = useState<SecurityRule>({
    name: '',
    source_zone: 'trust',
    dest_zone: 'untrust',
    source_addresses: ['any'],
    dest_addresses: ['any'],
    services: ['application-default'],
    action: 'allow',
    log_start: false,
    log_end: true
  })

  const [generatedConfig, setGeneratedConfig] = useState('')

  // Generate name based on format
  const generateObjectName = (value: string, customName?: string): string => {
    const cleanValue = value.replace(/\//g, '_').replace(/\./g, '-')
    
    switch (nameFormat) {
      case 'ipaddress_name':
        return customName ? `${cleanValue}_${customName}` : cleanValue
      case 'name_ipaddress':
        return customName ? `${customName}_${cleanValue}` : cleanValue
      case 'custom_prefix':
        return customPrefix ? `${customPrefix}_${cleanValue}` : cleanValue
      case 'ip_only':
        return cleanValue
      default:
        return cleanValue
    }
  }

  const generateAddressConfig = () => {
    if (!addressObj.value) return
    
    const objectName = addressObj.name 
      ? generateObjectName(addressObj.value, addressObj.name)
      : generateObjectName(addressObj.value)
    
    // Build command based on shared or device-specific
    const prefix = isShared ? 'set shared address' : 'set address'
    
    let config = `${prefix} "${objectName}" ${addressObj.type} "${addressObj.value}"`
    if (addressObj.description) {
      config += `\n${prefix} "${objectName}" description "${addressObj.description}"`
    }
    
    setGeneratedConfig(config)
  }

  const generateServiceConfig = () => {
    if (!serviceObj.name || !serviceObj.port) return
    
    const prefix = isShared ? 'set shared service' : 'set service'
    
    let config = `${prefix} "${serviceObj.name}" protocol ${serviceObj.protocol} port ${serviceObj.port}`
    if (serviceObj.description) {
      config += `\n${prefix} "${serviceObj.name}" description "${serviceObj.description}"`
    }
    
    setGeneratedConfig(config)
  }

  const generateRuleConfig = () => {
    if (!rule.name) return
    
    const prefix = isShared 
      ? 'set shared pre-rulebase security rules'
      : 'set rulebase security rules'
    
    const lines = [
      `${prefix} "${rule.name}" from "${rule.source_zone}"`,
      `${prefix} "${rule.name}" to "${rule.dest_zone}"`,
      `${prefix} "${rule.name}" source [ ${rule.source_addresses.map(a => `"${a}"`).join(' ')} ]`,
      `${prefix} "${rule.name}" destination [ ${rule.dest_addresses.map(a => `"${a}"`).join(' ')} ]`,
      `${prefix} "${rule.name}" service [ ${rule.services.map(s => `"${s}"`).join(' ')} ]`,
      `${prefix} "${rule.name}" action ${rule.action}`,
    ]
    
    if (rule.log_start) {
      lines.push(`${prefix} "${rule.name}" log-start yes`)
    }
    if (rule.log_end) {
      lines.push(`${prefix} "${rule.name}" log-end yes`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  const copyConfig = async () => {
    await navigator.clipboard.writeText(generatedConfig)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadConfig = () => {
    const blob = new Blob([generatedConfig], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `panos_config_${new Date().toISOString().slice(0,10)}.txt`
    a.click()
  }

  const TabButton = ({ id, label }: { id: typeof activeTab; label: string }) => (
    <button
      onClick={() => { setActiveTab(id); setGeneratedConfig('') }}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
        activeTab === id 
          ? 'bg-accent-red text-white' 
          : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center gap-3">
        <Shield className="w-8 h-8 text-accent-red" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">PAN-OS Generator</h1>
          <p className="text-text-secondary">Generieren Sie Palo Alto Firewall CLI-Konfigurationen</p>
        </div>
      </div>

      {/* Global Settings */}
      <Card variant="bordered">
        <CardContent className="pt-4">
          <div className="flex flex-wrap items-center gap-6">
            <Checkbox
              label="Shared Objects (Panorama)"
              checked={isShared}
              onChange={(e) => setIsShared(e.target.checked)}
            />
            
            <div className="flex items-center gap-2">
              <span className="text-sm text-text-secondary">Namensformat:</span>
              <select
                value={nameFormat}
                onChange={(e) => setNameFormat(e.target.value as NameFormat)}
                className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-red"
              >
                <option value="ipaddress_name">IP_Name</option>
                <option value="name_ipaddress">Name_IP</option>
                <option value="custom_prefix">Eigener Prefix</option>
                <option value="ip_only">Nur IP</option>
              </select>
            </div>

            {nameFormat === 'custom_prefix' && (
              <Input
                value={customPrefix}
                onChange={(e) => setCustomPrefix(e.target.value)}
                placeholder="Prefix eingeben"
                className="w-40"
              />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2">
        <TabButton id="address" label="Address Objects" />
        <TabButton id="service" label="Service Objects" />
        <TabButton id="rule" label="Security Rules" />
      </div>

      {/* Address Object Form */}
      {activeTab === 'address' && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Address Object erstellen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Name (optional - wird automatisch generiert)"
                value={addressObj.name}
                onChange={(e) => setAddressObj(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. WebServer-01"
              />
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Typ</label>
                <select
                  value={addressObj.type}
                  onChange={(e) => setAddressObj(prev => ({ ...prev, type: e.target.value as AddressObject['type'] }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="ip-netmask">IP/Netmask</option>
                  <option value="ip-range">IP Range</option>
                  <option value="fqdn">FQDN</option>
                </select>
              </div>
              <Input
                label="Wert"
                value={addressObj.value}
                onChange={(e) => setAddressObj(prev => ({ ...prev, value: e.target.value }))}
                placeholder={addressObj.type === 'ip-netmask' ? '192.168.1.0/24' : addressObj.type === 'ip-range' ? '192.168.1.1-192.168.1.10' : 'example.com'}
              />
              <Input
                label="Beschreibung (optional)"
                value={addressObj.description}
                onChange={(e) => setAddressObj(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Webserver im DMZ"
              />
            </div>
            
            {/* Preview */}
            {addressObj.value && (
              <div className="mt-4 p-3 bg-bg-tertiary rounded-lg">
                <span className="text-xs text-text-muted">Vorschau Objektname: </span>
                <code className="text-sm text-accent-red">
                  {addressObj.name 
                    ? generateObjectName(addressObj.value, addressObj.name)
                    : generateObjectName(addressObj.value)}
                </code>
              </div>
            )}
            
            <div className="mt-4">
              <Button onClick={generateAddressConfig} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Service Object Form */}
      {activeTab === 'service' && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Service Object erstellen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Name"
                value={serviceObj.name}
                onChange={(e) => setServiceObj(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. Custom-HTTPS"
              />
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Protokoll</label>
                <select
                  value={serviceObj.protocol}
                  onChange={(e) => setServiceObj(prev => ({ ...prev, protocol: e.target.value as 'tcp' | 'udp' }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                </select>
              </div>
              <Input
                label="Port(s)"
                value={serviceObj.port}
                onChange={(e) => setServiceObj(prev => ({ ...prev, port: e.target.value }))}
                placeholder="443 oder 8000-8100"
              />
              <Input
                label="Beschreibung (optional)"
                value={serviceObj.description}
                onChange={(e) => setServiceObj(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Custom HTTPS Port"
              />
            </div>
            <div className="mt-4">
              <Button onClick={generateServiceConfig} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Rule Form */}
      {activeTab === 'rule' && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Security Rule erstellen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Regel-Name"
                value={rule.name}
                onChange={(e) => setRule(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. Allow-Web-Traffic"
              />
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Aktion</label>
                <select
                  value={rule.action}
                  onChange={(e) => setRule(prev => ({ ...prev, action: e.target.value as SecurityRule['action'] }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="drop">Drop</option>
                </select>
              </div>
              <Input
                label="Source Zone"
                value={rule.source_zone}
                onChange={(e) => setRule(prev => ({ ...prev, source_zone: e.target.value }))}
                placeholder="trust"
              />
              <Input
                label="Destination Zone"
                value={rule.dest_zone}
                onChange={(e) => setRule(prev => ({ ...prev, dest_zone: e.target.value }))}
                placeholder="untrust"
              />
              <Input
                label="Source Addresses (kommagetrennt)"
                value={rule.source_addresses.join(', ')}
                onChange={(e) => setRule(prev => ({ ...prev, source_addresses: e.target.value.split(',').map(s => s.trim()) }))}
                placeholder="any"
              />
              <Input
                label="Destination Addresses (kommagetrennt)"
                value={rule.dest_addresses.join(', ')}
                onChange={(e) => setRule(prev => ({ ...prev, dest_addresses: e.target.value.split(',').map(s => s.trim()) }))}
                placeholder="any"
              />
              <Input
                label="Services (kommagetrennt)"
                value={rule.services.join(', ')}
                onChange={(e) => setRule(prev => ({ ...prev, services: e.target.value.split(',').map(s => s.trim()) }))}
                placeholder="application-default"
              />
              <div className="flex gap-4 items-end">
                <Checkbox
                  label="Log Start"
                  checked={rule.log_start}
                  onChange={(e) => setRule(prev => ({ ...prev, log_start: e.target.checked }))}
                />
                <Checkbox
                  label="Log End"
                  checked={rule.log_end}
                  onChange={(e) => setRule(prev => ({ ...prev, log_end: e.target.checked }))}
                />
              </div>
            </div>
            <div className="mt-4">
              <Button onClick={generateRuleConfig} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Config Output */}
      {generatedConfig && (
        <Card variant="bordered">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Generierte PAN-OS CLI Konfiguration</CardTitle>
              <div className="flex gap-2">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={copyConfig}
                  icon={copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
                >
                  {copied ? 'Kopiert!' : 'Kopieren'}
                </Button>
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={downloadConfig}
                  icon={<Download className="w-4 h-4" />}
                >
                  Download
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="bg-bg-tertiary p-4 rounded-lg overflow-x-auto text-sm font-mono text-accent-green whitespace-pre-wrap">
              {generatedConfig}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Info Box */}
      <Alert variant="info" title="Hinweis">
        Die generierte Konfiguration kann direkt in die PAN-OS CLI eingefügt werden. 
        Vergessen Sie nicht, nach dem Einfügen <code className="bg-bg-tertiary px-1 rounded">commit</code> auszuführen.
        {isShared && (
          <> Shared Objects werden im Panorama-Kontext erstellt.</>
        )}
      </Alert>
    </div>
  )
}
