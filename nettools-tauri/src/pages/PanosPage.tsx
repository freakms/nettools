import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Checkbox } from '@/components/ui'
import { Shield, Copy, Check, Download, Trash2, RefreshCw, FileText, Tag, Settings } from 'lucide-react'

type ActiveTab = 'addresses' | 'policies' | 'services' | 'schedule' | 'appfilter' | 'urlcategory'
type NameFormat = 'name_ip' | 'ip_name' | 'name_only' | 'ip_only'
type Separator = '_' | '-' | '.'

export function PanosPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('addresses')
  const [copied, setCopied] = useState(false)
  
  // Global Settings
  const [isShared, setIsShared] = useState(true)
  const [nameFormat, setNameFormat] = useState<NameFormat>('name_ip')
  const [separator, setSeparator] = useState<Separator>('_')
  const [defaultTag, setDefaultTag] = useState('')
  
  // Address Generator State - Two Windows
  const [baseNames, setBaseNames] = useState('')
  const [ipAddresses, setIpAddresses] = useState('')
  const [addressType, setAddressType] = useState<'ip-netmask' | 'fqdn'>('ip-netmask')
  
  // Security Policy State
  const [policyName, setPolicyName] = useState('')
  const [sourceZone, setSourceZone] = useState('trust')
  const [destZone, setDestZone] = useState('untrust')
  const [sourceAddresses, setSourceAddresses] = useState('')
  const [destAddresses, setDestAddresses] = useState('')
  const [services, setServices] = useState('application-default')
  const [applications, setApplications] = useState('any')
  const [action, setAction] = useState<'allow' | 'deny' | 'drop'>('allow')
  const [logStart, setLogStart] = useState(false)
  const [logEnd, setLogEnd] = useState(true)
  
  // Service Object State - Bulk
  const [serviceName, setServiceName] = useState('')
  const [protocol, setProtocol] = useState<'tcp' | 'udp' | 'sctp' | 'tcp/udp'>('tcp')
  const [port, setPort] = useState('')
  const [serviceDescription, setServiceDescription] = useState('')
  // Service Bulk Import
  const [serviceNames, setServiceNames] = useState('')
  const [servicePorts, setServicePorts] = useState('')
  const [bulkProtocol, setBulkProtocol] = useState<'tcp' | 'udp' | 'sctp' | 'tcp/udp'>('tcp')

  // Schedule State
  const [scheduleName, setScheduleName] = useState('')
  const [scheduleType, setScheduleType] = useState<'recurring' | 'non-recurring'>('recurring')
  const [scheduleDays, setScheduleDays] = useState<string[]>(['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
  const [scheduleTimeStart, setScheduleTimeStart] = useState('08:00')
  const [scheduleTimeEnd, setScheduleTimeEnd] = useState('18:00')

  // App Filter State
  const [appFilterName, setAppFilterName] = useState('')
  const [appCategories, setAppCategories] = useState('')
  const [appRisk, setAppRisk] = useState<string[]>([])
  
  // URL Category State
  const [urlCategoryName, setUrlCategoryName] = useState('')
  const [urlList, setUrlList] = useState('')

  const [generatedConfig, setGeneratedConfig] = useState('')
  const [commandCount, setCommandCount] = useState(0)

  // Helper: Get command prefix
  const getPrefix = (objectType: string) => {
    return isShared ? `set shared ${objectType}` : `set ${objectType}`
  }

  // Generate object name based on format - IP bleibt mit Punkten
  const generateObjectName = (name: string, ip: string): string => {
    // Nur den CIDR-Teil ersetzen, Punkte in der IP behalten
    const cleanIp = ip.replace(/\//g, '_')
    const cleanName = name.trim()
    
    switch (nameFormat) {
      case 'name_ip':
        return cleanName ? `${cleanName}${separator}${cleanIp}` : cleanIp
      case 'ip_name':
        return cleanName ? `${cleanIp}${separator}${cleanName}` : cleanIp
      case 'name_only':
        return cleanName || cleanIp
      case 'ip_only':
        return cleanIp
      default:
        return cleanIp
    }
  }

  // Generate Address Objects from two lists
  const generateAddressConfig = () => {
    const names = baseNames.split('\n').map(n => n.trim()).filter(n => n)
    const ips = ipAddresses.split('\n').map(ip => ip.trim()).filter(ip => ip)
    
    if (ips.length === 0) {
      setGeneratedConfig('// Fehler: Keine IP-Adressen eingegeben')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('address')
    const lines: string[] = []
    
    // Match names with IPs line by line
    const maxLength = Math.max(names.length, ips.length)
    
    for (let i = 0; i < maxLength; i++) {
      const ip = ips[i] || ips[ips.length - 1] // Use last IP if not enough
      const name = names[i] || '' // Empty name if not enough
      
      if (!ip) continue
      
      const objectName = generateObjectName(name, ip)
      
      // Add /32 if no mask specified and type is ip-netmask
      let ipValue = ip
      if (addressType === 'ip-netmask' && !ip.includes('/')) {
        ipValue = `${ip}/32`
      }
      
      lines.push(`${prefix} "${objectName}" ${addressType} "${ipValue}"`)
      
      if (defaultTag) {
        lines.push(`${prefix} "${objectName}" tag [ "${defaultTag}" ]`)
      }
    }
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate Security Policy
  const generatePolicyConfig = () => {
    if (!policyName) {
      setGeneratedConfig('// Fehler: Kein Regel-Name eingegeben')
      setCommandCount(0)
      return
    }

    const prefix = isShared 
      ? `set shared pre-rulebase security rules`
      : `set rulebase security rules`
    
    const srcAddrs = sourceAddresses.split(',').map(s => s.trim()).filter(s => s) || ['any']
    const dstAddrs = destAddresses.split(',').map(s => s.trim()).filter(s => s) || ['any']
    const svcList = services.split(',').map(s => s.trim()).filter(s => s) || ['application-default']
    const appList = applications.split(',').map(s => s.trim()).filter(s => s) || ['any']
    
    const lines: string[] = []
    lines.push(`${prefix} "${policyName}" from "${sourceZone}"`)
    lines.push(`${prefix} "${policyName}" to "${destZone}"`)
    lines.push(`${prefix} "${policyName}" source [ ${srcAddrs.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${policyName}" destination [ ${dstAddrs.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${policyName}" service [ ${svcList.map(s => `"${s}"`).join(' ')} ]`)
    lines.push(`${prefix} "${policyName}" application [ ${appList.map(a => `"${a}"`).join(' ')} ]`)
    lines.push(`${prefix} "${policyName}" action ${action}`)
    
    if (logStart) lines.push(`${prefix} "${policyName}" log-start yes`)
    if (logEnd) lines.push(`${prefix} "${policyName}" log-end yes`)
    if (defaultTag) lines.push(`${prefix} "${policyName}" tag [ "${defaultTag}" ]`)
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate Service Object
  const generateServiceConfig = () => {
    if (!serviceName || !port) {
      setGeneratedConfig('// Fehler: Name und Port erforderlich')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('service')
    const lines: string[] = []
    
    if (protocol === 'tcp/udp') {
      // Generate both TCP and UDP services
      lines.push(`${prefix} "${serviceName}-tcp" protocol tcp port ${port}`)
      if (serviceDescription) {
        lines.push(`${prefix} "${serviceName}-tcp" description "${serviceDescription}"`)
      }
      if (defaultTag) {
        lines.push(`${prefix} "${serviceName}-tcp" tag [ "${defaultTag}" ]`)
      }
      lines.push(`${prefix} "${serviceName}-udp" protocol udp port ${port}`)
      if (serviceDescription) {
        lines.push(`${prefix} "${serviceName}-udp" description "${serviceDescription}"`)
      }
      if (defaultTag) {
        lines.push(`${prefix} "${serviceName}-udp" tag [ "${defaultTag}" ]`)
      }
    } else {
      lines.push(`${prefix} "${serviceName}" protocol ${protocol} port ${port}`)
      if (serviceDescription) {
        lines.push(`${prefix} "${serviceName}" description "${serviceDescription}"`)
      }
      if (defaultTag) {
        lines.push(`${prefix} "${serviceName}" tag [ "${defaultTag}" ]`)
      }
    }
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate Bulk Services
  const generateBulkServiceConfig = () => {
    const names = serviceNames.split('\n').map(n => n.trim()).filter(n => n)
    const ports = servicePorts.split('\n').map(p => p.trim()).filter(p => p)
    
    if (names.length === 0 || ports.length === 0) {
      setGeneratedConfig('// Fehler: Namen und Ports erforderlich')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('service')
    const lines: string[] = []
    const maxLength = Math.max(names.length, ports.length)
    
    for (let i = 0; i < maxLength; i++) {
      const name = names[i] || names[names.length - 1]
      const portVal = ports[i] || ports[ports.length - 1]
      
      if (!name || !portVal) continue
      
      if (bulkProtocol === 'tcp/udp') {
        // Generate both TCP and UDP
        lines.push(`${prefix} "${name}-tcp" protocol tcp port ${portVal}`)
        if (defaultTag) {
          lines.push(`${prefix} "${name}-tcp" tag [ "${defaultTag}" ]`)
        }
        lines.push(`${prefix} "${name}-udp" protocol udp port ${portVal}`)
        if (defaultTag) {
          lines.push(`${prefix} "${name}-udp" tag [ "${defaultTag}" ]`)
        }
      } else {
        lines.push(`${prefix} "${name}" protocol ${bulkProtocol} port ${portVal}`)
        if (defaultTag) {
          lines.push(`${prefix} "${name}" tag [ "${defaultTag}" ]`)
        }
      }
    }
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate Schedule
  const generateScheduleConfig = () => {
    if (!scheduleName) {
      setGeneratedConfig('// Fehler: Kein Schedule-Name eingegeben')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('schedule')
    const lines: string[] = []
    
    if (scheduleType === 'recurring') {
      lines.push(`${prefix} "${scheduleName}" schedule-type recurring weekly`)
      for (const day of scheduleDays) {
        lines.push(`${prefix} "${scheduleName}" schedule-type recurring weekly ${day} [ "${scheduleTimeStart}-${scheduleTimeEnd}" ]`)
      }
    } else {
      lines.push(`${prefix} "${scheduleName}" schedule-type non-recurring [ "${scheduleTimeStart}-${scheduleTimeEnd}" ]`)
    }
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate App Filter
  const generateAppFilterConfig = () => {
    if (!appFilterName) {
      setGeneratedConfig('// Fehler: Kein Filter-Name eingegeben')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('application-filter')
    const lines: string[] = []
    
    lines.push(`${prefix} "${appFilterName}"`)
    
    if (appCategories) {
      const cats = appCategories.split(',').map(c => c.trim()).filter(c => c)
      if (cats.length > 0) {
        lines.push(`${prefix} "${appFilterName}" category [ ${cats.map(c => `"${c}"`).join(' ')} ]`)
      }
    }
    
    if (appRisk.length > 0) {
      lines.push(`${prefix} "${appFilterName}" risk [ ${appRisk.join(' ')} ]`)
    }
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
  }

  // Generate URL Category
  const generateUrlCategoryConfig = () => {
    if (!urlCategoryName || !urlList.trim()) {
      setGeneratedConfig('// Fehler: Name und URLs erforderlich')
      setCommandCount(0)
      return
    }

    const prefix = getPrefix('profiles custom-url-category')
    const lines: string[] = []
    const urls = urlList.split('\n').map(u => u.trim()).filter(u => u)
    
    lines.push(`${prefix} "${urlCategoryName}" type "URL List"`)
    lines.push(`${prefix} "${urlCategoryName}" list [ ${urls.map(u => `"${u}"`).join(' ')} ]`)
    
    setGeneratedConfig(lines.join('\n'))
    setCommandCount(lines.length)
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

  const clearAll = () => {
    setGeneratedConfig('')
    setCommandCount(0)
  }

  const TabButton = ({ id, label, icon }: { id: ActiveTab; label: string; icon?: React.ReactNode }) => (
    <button
      onClick={() => { setActiveTab(id); setGeneratedConfig(''); setCommandCount(0) }}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
        activeTab === id 
          ? 'bg-accent-red text-white' 
          : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
      }`}
    >
      {icon}
      {label}
    </button>
  )

  // Count lines in each textarea
  const nameCount = baseNames.split('\n').filter(n => n.trim()).length
  const ipCount = ipAddresses.split('\n').filter(n => n.trim()).length

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
              <span className="text-sm text-text-secondary">Separator:</span>
              <select
                value={separator}
                onChange={(e) => setSeparator(e.target.value as Separator)}
                className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-red"
              >
                <option value="_">_ (Underscore)</option>
                <option value="-">- (Dash)</option>
                <option value=".">. (Dot)</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-text-secondary">Format:</span>
              <select
                value={nameFormat}
                onChange={(e) => setNameFormat(e.target.value as NameFormat)}
                className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-red"
              >
                <option value="name_ip">Name_IP</option>
                <option value="ip_name">IP_Name</option>
                <option value="name_only">Nur Name</option>
                <option value="ip_only">Nur IP</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-text-muted" />
              <Input
                value={defaultTag}
                onChange={(e) => setDefaultTag(e.target.value)}
                placeholder="Standard-Tag"
                className="w-36"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        <TabButton id="addresses" label="Addresses" icon={<Shield className="w-4 h-4" />} />
        <TabButton id="policies" label="Policies" />
        <TabButton id="services" label="Services" />
        <TabButton id="schedule" label="Schedule" />
        <TabButton id="appfilter" label="App Filter" />
        <TabButton id="urlcategory" label="URL Category" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Input Forms */}
        <div className="space-y-4">
          {/* Address Generator - Two Windows */}
          {activeTab === 'addresses' && (
            <Card variant="bordered">
              <CardHeader>
                <CardTitle className="text-accent-purple">Address Name Generator</CardTitle>
                <p className="text-sm text-text-muted">Generate address object names from base names and IPs, then create CLI commands</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 mb-2">
                  <span className="text-sm text-text-secondary">Typ:</span>
                  <select
                    value={addressType}
                    onChange={(e) => setAddressType(e.target.value as 'ip-netmask' | 'fqdn')}
                    className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-1.5 text-sm text-text-primary"
                  >
                    <option value="ip-netmask">IP/Netmask</option>
                    <option value="fqdn">FQDN</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Base Names (one per line): <span className="text-text-muted">({nameCount} Einträge)</span>
                  </label>
                  <textarea
                    value={baseNames}
                    onChange={(e) => setBaseNames(e.target.value)}
                    placeholder="Server1&#10;Server2&#10;WebServer"
                    className="w-full h-40 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono focus:outline-none focus:border-accent-red resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    IP Addresses/Netmasks (one per line): <span className="text-text-muted">({ipCount} Einträge)</span>
                  </label>
                  <textarea
                    value={ipAddresses}
                    onChange={(e) => setIpAddresses(e.target.value)}
                    placeholder="192.168.1.10&#10;192.168.1.20&#10;10.0.0.10"
                    className="w-full h-40 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono focus:outline-none focus:border-accent-red resize-none"
                  />
                </div>

                <div className="p-3 bg-accent-purple/10 rounded-lg text-sm">
                  <p className="font-medium text-accent-purple mb-1">💡 How it Works:</p>
                  <ul className="text-text-secondary space-y-1">
                    <li>• Both lists must have the same number of lines</li>
                    <li>• Each name pairs with corresponding IP (line 1 → line 1)</li>
                    <li>• Empty names will use IP-only format</li>
                  </ul>
                </div>

                <div className="flex gap-2">
                  <Button onClick={generateAddressConfig} icon={<RefreshCw className="w-4 h-4" />} className="flex-1">
                    Generate Object Names
                  </Button>
                  <Button variant="secondary" onClick={() => { setBaseNames(''); setIpAddresses('') }} icon={<Trash2 className="w-4 h-4" />}>
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Security Policy */}
          {activeTab === 'policies' && (
            <Card variant="bordered">
              <CardHeader><CardTitle>Security Policy erstellen</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Regel-Name" value={policyName} onChange={(e) => setPolicyName(e.target.value)} placeholder="Allow-Web" />
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">Aktion</label>
                    <select value={action} onChange={(e) => setAction(e.target.value as typeof action)} className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary">
                      <option value="allow">Allow</option>
                      <option value="deny">Deny</option>
                      <option value="drop">Drop</option>
                    </select>
                  </div>
                  <Input label="Source Zone" value={sourceZone} onChange={(e) => setSourceZone(e.target.value)} />
                  <Input label="Dest Zone" value={destZone} onChange={(e) => setDestZone(e.target.value)} />
                  <Input label="Source Addresses (kommagetrennt)" value={sourceAddresses} onChange={(e) => setSourceAddresses(e.target.value)} placeholder="any" />
                  <Input label="Dest Addresses (kommagetrennt)" value={destAddresses} onChange={(e) => setDestAddresses(e.target.value)} placeholder="any" />
                  <Input label="Services" value={services} onChange={(e) => setServices(e.target.value)} />
                  <Input label="Applications" value={applications} onChange={(e) => setApplications(e.target.value)} />
                </div>
                <div className="flex gap-4">
                  <Checkbox label="Log Start" checked={logStart} onChange={(e) => setLogStart(e.target.checked)} />
                  <Checkbox label="Log End" checked={logEnd} onChange={(e) => setLogEnd(e.target.checked)} />
                </div>
                <Button onClick={generatePolicyConfig} icon={<Shield className="w-4 h-4" />}>Generieren</Button>
              </CardContent>
            </Card>
          )}

          {/* Services */}
          {activeTab === 'services' && (
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>Service Objects erstellen</CardTitle>
                <p className="text-sm text-text-muted">Einzeln oder per Bulk-Import</p>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Single Service */}
                <div className="p-4 bg-bg-tertiary rounded-lg space-y-4">
                  <h4 className="font-medium text-text-primary">Einzelner Service</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Service-Name" value={serviceName} onChange={(e) => setServiceName(e.target.value)} placeholder="Custom-HTTPS" />
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">Protokoll</label>
                      <select value={protocol} onChange={(e) => setProtocol(e.target.value as typeof protocol)} className="w-full bg-bg-secondary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary">
                        <option value="tcp">TCP</option>
                        <option value="udp">UDP</option>
                        <option value="sctp">SCTP</option>
                      </select>
                    </div>
                    <Input label="Port(s)" value={port} onChange={(e) => setPort(e.target.value)} placeholder="443 oder 8000-8100" />
                    <Input label="Beschreibung" value={serviceDescription} onChange={(e) => setServiceDescription(e.target.value)} />
                  </div>
                  <Button onClick={generateServiceConfig} icon={<Shield className="w-4 h-4" />}>Einzeln Generieren</Button>
                </div>

                {/* Bulk Services */}
                <div className="p-4 bg-accent-purple/10 rounded-lg space-y-4">
                  <h4 className="font-medium text-accent-purple">Bulk Import</h4>
                  <div className="flex items-center gap-4 mb-2">
                    <span className="text-sm text-text-secondary">Protokoll für alle:</span>
                    <select value={bulkProtocol} onChange={(e) => setBulkProtocol(e.target.value as typeof bulkProtocol)} className="bg-bg-tertiary border border-border-default rounded-lg px-3 py-1.5 text-sm text-text-primary">
                      <option value="tcp">TCP</option>
                      <option value="udp">UDP</option>
                      <option value="sctp">SCTP</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Service Namen (one per line)
                      </label>
                      <textarea
                        value={serviceNames}
                        onChange={(e) => setServiceNames(e.target.value)}
                        placeholder="HTTP-8080&#10;HTTPS-Custom&#10;API-Service"
                        className="w-full h-32 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono resize-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Ports (one per line)
                      </label>
                      <textarea
                        value={servicePorts}
                        onChange={(e) => setServicePorts(e.target.value)}
                        placeholder="8080&#10;8443&#10;3000-3010"
                        className="w-full h-32 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono resize-none"
                      />
                    </div>
                  </div>
                  <Button onClick={generateBulkServiceConfig} icon={<Shield className="w-4 h-4" />} className="bg-accent-purple hover:bg-accent-purple/80">
                    Bulk Generieren
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Schedule */}
          {activeTab === 'schedule' && (
            <Card variant="bordered">
              <CardHeader><CardTitle>Schedule erstellen</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Input label="Schedule-Name" value={scheduleName} onChange={(e) => setScheduleName(e.target.value)} placeholder="Business-Hours" />
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">Typ</label>
                  <select value={scheduleType} onChange={(e) => setScheduleType(e.target.value as typeof scheduleType)} className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary">
                    <option value="recurring">Recurring (Wöchentlich)</option>
                    <option value="non-recurring">Non-Recurring (Einmalig)</option>
                  </select>
                </div>
                {scheduleType === 'recurring' && (
                  <div className="flex flex-wrap gap-2">
                    {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                      <label key={day} className="flex items-center gap-1 text-sm">
                        <input
                          type="checkbox"
                          checked={scheduleDays.includes(day)}
                          onChange={(e) => {
                            if (e.target.checked) setScheduleDays([...scheduleDays, day])
                            else setScheduleDays(scheduleDays.filter(d => d !== day))
                          }}
                          className="rounded"
                        />
                        {day.charAt(0).toUpperCase() + day.slice(1, 3)}
                      </label>
                    ))}
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Start-Zeit" type="time" value={scheduleTimeStart} onChange={(e) => setScheduleTimeStart(e.target.value)} />
                  <Input label="End-Zeit" type="time" value={scheduleTimeEnd} onChange={(e) => setScheduleTimeEnd(e.target.value)} />
                </div>
                <Button onClick={generateScheduleConfig} icon={<Shield className="w-4 h-4" />}>Generieren</Button>
              </CardContent>
            </Card>
          )}

          {/* App Filter */}
          {activeTab === 'appfilter' && (
            <Card variant="bordered">
              <CardHeader><CardTitle>Application Filter erstellen</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Input label="Filter-Name" value={appFilterName} onChange={(e) => setAppFilterName(e.target.value)} placeholder="High-Risk-Apps" />
                <Input label="Categories (kommagetrennt)" value={appCategories} onChange={(e) => setAppCategories(e.target.value)} placeholder="social-networking, file-sharing" />
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">Risk Level</label>
                  <div className="flex gap-4">
                    {['1', '2', '3', '4', '5'].map(risk => (
                      <label key={risk} className="flex items-center gap-1 text-sm">
                        <input
                          type="checkbox"
                          checked={appRisk.includes(risk)}
                          onChange={(e) => {
                            if (e.target.checked) setAppRisk([...appRisk, risk])
                            else setAppRisk(appRisk.filter(r => r !== risk))
                          }}
                          className="rounded"
                        />
                        {risk}
                      </label>
                    ))}
                  </div>
                </div>
                <Button onClick={generateAppFilterConfig} icon={<Shield className="w-4 h-4" />}>Generieren</Button>
              </CardContent>
            </Card>
          )}

          {/* URL Category */}
          {activeTab === 'urlcategory' && (
            <Card variant="bordered">
              <CardHeader><CardTitle>Custom URL Category erstellen</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Input label="Category-Name" value={urlCategoryName} onChange={(e) => setUrlCategoryName(e.target.value)} placeholder="Blocked-Sites" />
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">URLs (one per line)</label>
                  <textarea
                    value={urlList}
                    onChange={(e) => setUrlList(e.target.value)}
                    placeholder="example.com&#10;*.blocked-domain.com&#10;malware-site.net"
                    className="w-full h-40 bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary font-mono focus:outline-none focus:border-accent-red resize-none"
                  />
                </div>
                <Button onClick={generateUrlCategoryConfig} icon={<Shield className="w-4 h-4" />}>Generieren</Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Panel - Command Output */}
        <Card variant="bordered" className="h-fit sticky top-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-accent-cyan" />
                <CardTitle>Command Output</CardTitle>
              </div>
              <Button variant="ghost" size="sm" onClick={clearAll} icon={<Trash2 className="w-4 h-4" />}>
                Clear All
              </Button>
            </div>
            <p className="text-sm text-text-muted">{commandCount} commands generated</p>
          </CardHeader>
          <CardContent>
            {generatedConfig ? (
              <>
                <pre className="bg-bg-tertiary p-4 rounded-lg overflow-x-auto text-sm font-mono text-accent-green whitespace-pre-wrap max-h-[400px] overflow-y-auto mb-4">
                  {generatedConfig}
                </pre>
                <div className="flex gap-2">
                  <Button 
                    onClick={copyConfig}
                    icon={copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
                    className="flex-1"
                  >
                    {copied ? 'Kopiert!' : 'Kopieren'}
                  </Button>
                  <Button 
                    variant="secondary" 
                    onClick={downloadConfig}
                    icon={<Download className="w-4 h-4" />}
                  >
                    Download
                  </Button>
                </div>
              </>
            ) : (
              <div className="text-center py-12 text-text-muted">
                <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No commands generated yet</p>
                <p className="text-sm">Fill out the form to generate CLI commands</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info Box */}
      <Alert variant="info" title="Hinweis">
        Die generierte Konfiguration kann direkt in die PAN-OS CLI eingefügt werden. 
        Vergessen Sie nicht, nach dem Einfügen <code className="bg-bg-tertiary px-1 rounded">commit</code> auszuführen.
      </Alert>
    </div>
  )
}
