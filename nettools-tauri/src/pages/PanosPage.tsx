import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Checkbox } from '@/components/ui'
import { Shield, Copy, Check, Download, Plus, Trash2, Upload, Tag } from 'lucide-react'

// Types
interface AddressObject {
  name: string
  type: 'ip-netmask' | 'ip-range' | 'fqdn'
  value: string
  description: string
  tag: string
}

interface AddressGroup {
  name: string
  members: string[]
  description: string
  tag: string
}

interface ServiceObject {
  name: string
  protocol: 'tcp' | 'udp' | 'sctp'
  port: string
  description: string
  tag: string
}

interface NatRule {
  name: string
  nat_type: 'source' | 'destination'
  source_zone: string
  dest_zone: string
  source_address: string
  dest_address: string
  service: string
  translated_address: string
  translated_port: string
  description: string
}

interface SecurityRule {
  name: string
  source_zone: string
  dest_zone: string
  source_addresses: string[]
  dest_addresses: string[]
  services: string[]
  applications: string[]
  action: 'allow' | 'deny' | 'drop'
  log_start: boolean
  log_end: boolean
  tag: string
  description: string
}

type NameFormat = 'ipaddress_name' | 'name_ipaddress' | 'custom_prefix' | 'ip_only'
type ActiveTab = 'address' | 'group' | 'service' | 'nat' | 'rule' | 'bulk'

export function PanosPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('address')
  const [copied, setCopied] = useState(false)
  
  // Global Settings
  const [isShared, setIsShared] = useState(true)
  const [nameFormat, setNameFormat] = useState<NameFormat>('ipaddress_name')
  const [customPrefix, setCustomPrefix] = useState('')
  const [defaultTag, setDefaultTag] = useState('')
  
  // Address Object State
  const [addressObj, setAddressObj] = useState<AddressObject>({
    name: '', type: 'ip-netmask', value: '', description: '', tag: ''
  })
  
  // Address Group State
  const [addressGroup, setAddressGroup] = useState<AddressGroup>({
    name: '', members: [], description: '', tag: ''
  })
  const [newMember, setNewMember] = useState('')
  
  // Service Object State
  const [serviceObj, setServiceObj] = useState<ServiceObject>({
    name: '', protocol: 'tcp', port: '', description: '', tag: ''
  })
  
  // NAT Rule State
  const [natRule, setNatRule] = useState<NatRule>({
    name: '', nat_type: 'source', source_zone: 'trust', dest_zone: 'untrust',
    source_address: 'any', dest_address: 'any', service: 'any',
    translated_address: '', translated_port: '', description: ''
  })
  
  // Security Rule State
  const [secRule, setSecRule] = useState<SecurityRule>({
    name: '', source_zone: 'trust', dest_zone: 'untrust',
    source_addresses: ['any'], dest_addresses: ['any'],
    services: ['application-default'], applications: ['any'],
    action: 'allow', log_start: false, log_end: true,
    tag: '', description: ''
  })
  
  // Bulk Import State
  const [bulkInput, setBulkInput] = useState('')
  const [bulkType, setBulkType] = useState<'ip-netmask' | 'fqdn'>('ip-netmask')

  const [generatedConfig, setGeneratedConfig] = useState('')

  // Helper: Generate name based on format
  const generateObjectName = (value: string, customName?: string): string => {
    const cleanValue = value.replace(/\//g, '_').replace(/\./g, '-').replace(/:/g, '-')
    
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

  // Get command prefix based on shared setting
  const getPrefix = (objectType: string) => {
    return isShared ? `set shared ${objectType}` : `set ${objectType}`
  }

  // Generate Address Object Config
  const generateAddressConfig = () => {
    if (!addressObj.value) return
    
    const objectName = addressObj.name 
      ? generateObjectName(addressObj.value, addressObj.name)
      : generateObjectName(addressObj.value)
    
    const prefix = getPrefix('address')
    const tag = addressObj.tag || defaultTag
    
    const lines: string[] = []
    lines.push(`${prefix} "${objectName}" ${addressObj.type} "${addressObj.value}"`)
    if (addressObj.description) {
      lines.push(`${prefix} "${objectName}" description "${addressObj.description}"`)
    }
    if (tag) {
      lines.push(`${prefix} "${objectName}" tag [ "${tag}" ]`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Generate Address Group Config
  const generateGroupConfig = () => {
    if (!addressGroup.name || addressGroup.members.length === 0) return
    
    const prefix = getPrefix('address-group')
    const tag = addressGroup.tag || defaultTag
    
    const lines: string[] = []
    const membersStr = addressGroup.members.map(m => `"${m}"`).join(' ')
    lines.push(`${prefix} "${addressGroup.name}" static [ ${membersStr} ]`)
    if (addressGroup.description) {
      lines.push(`${prefix} "${addressGroup.name}" description "${addressGroup.description}"`)
    }
    if (tag) {
      lines.push(`${prefix} "${addressGroup.name}" tag [ "${tag}" ]`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Generate Service Object Config
  const generateServiceConfig = () => {
    if (!serviceObj.name || !serviceObj.port) return
    
    const prefix = getPrefix('service')
    const tag = serviceObj.tag || defaultTag
    
    const lines: string[] = []
    lines.push(`${prefix} "${serviceObj.name}" protocol ${serviceObj.protocol} port ${serviceObj.port}`)
    if (serviceObj.description) {
      lines.push(`${prefix} "${serviceObj.name}" description "${serviceObj.description}"`)
    }
    if (tag) {
      lines.push(`${prefix} "${serviceObj.name}" tag [ "${tag}" ]`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Generate NAT Rule Config
  const generateNatConfig = () => {
    if (!natRule.name || !natRule.translated_address) return
    
    const prefix = isShared 
      ? `set shared pre-rulebase nat rules`
      : `set rulebase nat rules`
    
    const lines: string[] = []
    lines.push(`${prefix} "${natRule.name}" from "${natRule.source_zone}"`)
    lines.push(`${prefix} "${natRule.name}" to "${natRule.dest_zone}"`)
    lines.push(`${prefix} "${natRule.name}" source "${natRule.source_address}"`)
    lines.push(`${prefix} "${natRule.name}" destination "${natRule.dest_address}"`)
    lines.push(`${prefix} "${natRule.name}" service "${natRule.service}"`)
    
    if (natRule.nat_type === 'source') {
      lines.push(`${prefix} "${natRule.name}" source-translation dynamic-ip-and-port translated-address "${natRule.translated_address}"`)
    } else {
      lines.push(`${prefix} "${natRule.name}" destination-translation translated-address "${natRule.translated_address}"`)
      if (natRule.translated_port) {
        lines.push(`${prefix} "${natRule.name}" destination-translation translated-port ${natRule.translated_port}`)
      }
    }
    
    if (natRule.description) {
      lines.push(`${prefix} "${natRule.name}" description "${natRule.description}"`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Generate Security Rule Config
  const generateSecurityConfig = () => {
    if (!secRule.name) return
    
    const prefix = isShared 
      ? `set shared pre-rulebase security rules`
      : `set rulebase security rules`
    
    const tag = secRule.tag || defaultTag
    
    const lines: string[] = []
    lines.push(`${prefix} "${secRule.name}" from "${secRule.source_zone}"`)
    lines.push(`${prefix} "${secRule.name}" to "${secRule.dest_zone}"`)
    lines.push(`${prefix} "${secRule.name}" source [ ${secRule.source_addresses.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${secRule.name}" destination [ ${secRule.dest_addresses.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${secRule.name}" service [ ${secRule.services.map(s => `"${s}"`).join(' ')} ]`)
    lines.push(`${prefix} "${secRule.name}" application [ ${secRule.applications.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${secRule.name}" action ${secRule.action}`)
    
    if (secRule.log_start) {
      lines.push(`${prefix} "${secRule.name}" log-start yes`)
    }
    if (secRule.log_end) {
      lines.push(`${prefix} "${secRule.name}" log-end yes`)
    }
    if (tag) {
      lines.push(`${prefix} "${secRule.name}" tag [ "${tag}" ]`)
    }
    if (secRule.description) {
      lines.push(`${prefix} "${secRule.name}" description "${secRule.description}"`)
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Generate Bulk Import Config
  const generateBulkConfig = () => {
    if (!bulkInput.trim()) return
    
    const prefix = getPrefix('address')
    const tag = defaultTag
    const lines: string[] = []
    
    // Parse input: one entry per line, format: "value" or "value,name" or "value,name,description"
    const entries = bulkInput.split('\n').filter(line => line.trim())
    
    for (const entry of entries) {
      const parts = entry.split(',').map(p => p.trim())
      const value = parts[0]
      const customName = parts[1] || ''
      const description = parts[2] || ''
      
      if (!value) continue
      
      const objectName = customName 
        ? generateObjectName(value, customName)
        : generateObjectName(value)
      
      lines.push(`${prefix} "${objectName}" ${bulkType} "${value}"`)
      if (description) {
        lines.push(`${prefix} "${objectName}" description "${description}"`)
      }
      if (tag) {
        lines.push(`${prefix} "${objectName}" tag [ "${tag}" ]`)
      }
    }
    
    setGeneratedConfig(lines.join('\n'))
  }

  // Bulk Import from File
  const importFromFile = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.txt,.csv'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return
      const text = await file.text()
      setBulkInput(text)
    }
    input.click()
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

  // Add member to address group
  const addGroupMember = () => {
    if (!newMember.trim()) return
    if (addressGroup.members.includes(newMember.trim())) return
    setAddressGroup(prev => ({
      ...prev,
      members: [...prev.members, newMember.trim()]
    }))
    setNewMember('')
  }

  const removeGroupMember = (member: string) => {
    setAddressGroup(prev => ({
      ...prev,
      members: prev.members.filter(m => m !== member)
    }))
  }

  const TabButton = ({ id, label }: { id: ActiveTab; label: string }) => (
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

            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-text-muted" />
              <Input
                value={defaultTag}
                onChange={(e) => setDefaultTag(e.target.value)}
                placeholder="Standard-Tag (optional)"
                className="w-48"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        <TabButton id="address" label="Address Objects" />
        <TabButton id="group" label="Address Groups" />
        <TabButton id="service" label="Services" />
        <TabButton id="nat" label="NAT Rules" />
        <TabButton id="rule" label="Security Rules" />
        <TabButton id="bulk" label="Bulk Import" />
      </div>

      {/* Address Object Form */}
      {activeTab === 'address' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>Address Object erstellen</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Name (optional)"
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
                label="Tag (optional)"
                value={addressObj.tag}
                onChange={(e) => setAddressObj(prev => ({ ...prev, tag: e.target.value }))}
                placeholder="z.B. Production"
              />
              <Input
                label="Beschreibung (optional)"
                value={addressObj.description}
                onChange={(e) => setAddressObj(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Webserver im DMZ"
                className="md:col-span-2"
              />
            </div>
            {addressObj.value && (
              <div className="mt-4 p-3 bg-bg-tertiary rounded-lg">
                <span className="text-xs text-text-muted">Vorschau Objektname: </span>
                <code className="text-sm text-accent-red">
                  {addressObj.name ? generateObjectName(addressObj.value, addressObj.name) : generateObjectName(addressObj.value)}
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

      {/* Address Group Form */}
      {activeTab === 'group' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>Address Group erstellen</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Gruppenname"
                value={addressGroup.name}
                onChange={(e) => setAddressGroup(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. WebServers"
              />
              <Input
                label="Tag (optional)"
                value={addressGroup.tag}
                onChange={(e) => setAddressGroup(prev => ({ ...prev, tag: e.target.value }))}
                placeholder="z.B. Production"
              />
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-text-secondary mb-2">Mitglieder</label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newMember}
                    onChange={(e) => setNewMember(e.target.value)}
                    placeholder="Objektname hinzufügen"
                    onKeyDown={(e) => e.key === 'Enter' && addGroupMember()}
                    className="flex-1"
                  />
                  <Button onClick={addGroupMember} icon={<Plus className="w-4 h-4" />}>
                    Hinzufügen
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 min-h-[40px] p-2 bg-bg-tertiary rounded-lg">
                  {addressGroup.members.length === 0 ? (
                    <span className="text-text-muted text-sm">Keine Mitglieder</span>
                  ) : (
                    addressGroup.members.map(member => (
                      <span key={member} className="inline-flex items-center gap-1 px-2 py-1 bg-accent-red/20 text-accent-red rounded text-sm">
                        {member}
                        <button onClick={() => removeGroupMember(member)} className="hover:text-white">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>
              <Input
                label="Beschreibung (optional)"
                value={addressGroup.description}
                onChange={(e) => setAddressGroup(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Alle Webserver"
                className="md:col-span-2"
              />
            </div>
            <div className="mt-4">
              <Button onClick={generateGroupConfig} disabled={addressGroup.members.length === 0} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Service Object Form */}
      {activeTab === 'service' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>Service Object erstellen</CardTitle></CardHeader>
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
                  onChange={(e) => setServiceObj(prev => ({ ...prev, protocol: e.target.value as ServiceObject['protocol'] }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                  <option value="sctp">SCTP</option>
                </select>
              </div>
              <Input
                label="Port(s)"
                value={serviceObj.port}
                onChange={(e) => setServiceObj(prev => ({ ...prev, port: e.target.value }))}
                placeholder="443 oder 8000-8100"
              />
              <Input
                label="Tag (optional)"
                value={serviceObj.tag}
                onChange={(e) => setServiceObj(prev => ({ ...prev, tag: e.target.value }))}
                placeholder="z.B. Web"
              />
              <Input
                label="Beschreibung (optional)"
                value={serviceObj.description}
                onChange={(e) => setServiceObj(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Custom HTTPS Port"
                className="md:col-span-2"
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

      {/* NAT Rule Form */}
      {activeTab === 'nat' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>NAT Rule erstellen</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Regel-Name"
                value={natRule.name}
                onChange={(e) => setNatRule(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. SNAT-Internal"
              />
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">NAT Typ</label>
                <select
                  value={natRule.nat_type}
                  onChange={(e) => setNatRule(prev => ({ ...prev, nat_type: e.target.value as NatRule['nat_type'] }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="source">Source NAT (SNAT)</option>
                  <option value="destination">Destination NAT (DNAT)</option>
                </select>
              </div>
              <Input
                label="Source Zone"
                value={natRule.source_zone}
                onChange={(e) => setNatRule(prev => ({ ...prev, source_zone: e.target.value }))}
                placeholder="trust"
              />
              <Input
                label="Destination Zone"
                value={natRule.dest_zone}
                onChange={(e) => setNatRule(prev => ({ ...prev, dest_zone: e.target.value }))}
                placeholder="untrust"
              />
              <Input
                label="Source Address"
                value={natRule.source_address}
                onChange={(e) => setNatRule(prev => ({ ...prev, source_address: e.target.value }))}
                placeholder="any oder Objektname"
              />
              <Input
                label="Destination Address"
                value={natRule.dest_address}
                onChange={(e) => setNatRule(prev => ({ ...prev, dest_address: e.target.value }))}
                placeholder="any oder Objektname"
              />
              <Input
                label="Service"
                value={natRule.service}
                onChange={(e) => setNatRule(prev => ({ ...prev, service: e.target.value }))}
                placeholder="any oder Service-Name"
              />
              <Input
                label="Translated Address"
                value={natRule.translated_address}
                onChange={(e) => setNatRule(prev => ({ ...prev, translated_address: e.target.value }))}
                placeholder="Ziel-IP oder Objektname"
              />
              {natRule.nat_type === 'destination' && (
                <Input
                  label="Translated Port (optional)"
                  value={natRule.translated_port}
                  onChange={(e) => setNatRule(prev => ({ ...prev, translated_port: e.target.value }))}
                  placeholder="z.B. 8080"
                />
              )}
              <Input
                label="Beschreibung (optional)"
                value={natRule.description}
                onChange={(e) => setNatRule(prev => ({ ...prev, description: e.target.value }))}
                placeholder="NAT für interne Server"
                className="md:col-span-2"
              />
            </div>
            <div className="mt-4">
              <Button onClick={generateNatConfig} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Rule Form */}
      {activeTab === 'rule' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>Security Rule erstellen</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Regel-Name"
                value={secRule.name}
                onChange={(e) => setSecRule(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. Allow-Web-Traffic"
              />
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Aktion</label>
                <select
                  value={secRule.action}
                  onChange={(e) => setSecRule(prev => ({ ...prev, action: e.target.value as SecurityRule['action'] }))}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                >
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="drop">Drop</option>
                </select>
              </div>
              <Input
                label="Source Zone"
                value={secRule.source_zone}
                onChange={(e) => setSecRule(prev => ({ ...prev, source_zone: e.target.value }))}
                placeholder="trust"
              />
              <Input
                label="Destination Zone"
                value={secRule.dest_zone}
                onChange={(e) => setSecRule(prev => ({ ...prev, dest_zone: e.target.value }))}
                placeholder="untrust"
              />
              <Input
                label="Source Addresses (kommagetrennt)"
                value={secRule.source_addresses.join(', ')}
                onChange={(e) => setSecRule(prev => ({ ...prev, source_addresses: e.target.value.split(',').map(s => s.trim()).filter(s => s) }))}
                placeholder="any"
              />
              <Input
                label="Destination Addresses (kommagetrennt)"
                value={secRule.dest_addresses.join(', ')}
                onChange={(e) => setSecRule(prev => ({ ...prev, dest_addresses: e.target.value.split(',').map(s => s.trim()).filter(s => s) }))}
                placeholder="any"
              />
              <Input
                label="Services (kommagetrennt)"
                value={secRule.services.join(', ')}
                onChange={(e) => setSecRule(prev => ({ ...prev, services: e.target.value.split(',').map(s => s.trim()).filter(s => s) }))}
                placeholder="application-default"
              />
              <Input
                label="Applications (kommagetrennt)"
                value={secRule.applications.join(', ')}
                onChange={(e) => setSecRule(prev => ({ ...prev, applications: e.target.value.split(',').map(s => s.trim()).filter(s => s) }))}
                placeholder="any"
              />
              <Input
                label="Tag (optional)"
                value={secRule.tag}
                onChange={(e) => setSecRule(prev => ({ ...prev, tag: e.target.value }))}
                placeholder="z.B. Web-Rules"
              />
              <div className="flex gap-4 items-end">
                <Checkbox
                  label="Log Start"
                  checked={secRule.log_start}
                  onChange={(e) => setSecRule(prev => ({ ...prev, log_start: e.target.checked }))}
                />
                <Checkbox
                  label="Log End"
                  checked={secRule.log_end}
                  onChange={(e) => setSecRule(prev => ({ ...prev, log_end: e.target.checked }))}
                />
              </div>
              <Input
                label="Beschreibung (optional)"
                value={secRule.description}
                onChange={(e) => setSecRule(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Regel-Beschreibung"
                className="md:col-span-2"
              />
            </div>
            <div className="mt-4">
              <Button onClick={generateSecurityConfig} icon={<Shield className="w-4 h-4" />}>
                Konfiguration generieren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bulk Import Form */}
      {activeTab === 'bulk' && (
        <Card variant="bordered">
          <CardHeader><CardTitle>Bulk Import</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">Typ</label>
                  <select
                    value={bulkType}
                    onChange={(e) => setBulkType(e.target.value as 'ip-netmask' | 'fqdn')}
                    className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                  >
                    <option value="ip-netmask">IP/Netmask</option>
                    <option value="fqdn">FQDN</option>
                  </select>
                </div>
                <Button variant="secondary" onClick={importFromFile} icon={<Upload className="w-4 h-4" />}>
                  Aus Datei importieren
                </Button>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Adressen eingeben (eine pro Zeile)
                </label>
                <p className="text-xs text-text-muted mb-2">
                  Format: <code className="bg-bg-tertiary px-1 rounded">wert</code> oder{' '}
                  <code className="bg-bg-tertiary px-1 rounded">wert,name</code> oder{' '}
                  <code className="bg-bg-tertiary px-1 rounded">wert,name,beschreibung</code>
                </p>
                <textarea
                  value={bulkInput}
                  onChange={(e) => setBulkInput(e.target.value)}
                  placeholder={`192.168.1.0/24\n10.0.0.1/32,Server1\n172.16.0.0/16,Network,Internes Netzwerk`}
                  className="w-full h-48 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono focus:outline-none focus:border-accent-blue resize-none"
                />
              </div>
              
              <div className="text-sm text-text-muted">
                {bulkInput.split('\n').filter(l => l.trim()).length} Einträge erkannt
              </div>
              
              <Button onClick={generateBulkConfig} icon={<Shield className="w-4 h-4" />}>
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
            <pre className="bg-bg-tertiary p-4 rounded-lg overflow-x-auto text-sm font-mono text-accent-green whitespace-pre-wrap max-h-96">
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
