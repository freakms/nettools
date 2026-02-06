import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Alert, Badge, Checkbox } from '@/components/ui'
import { 
  Network, Settings, Power, PowerOff, RefreshCw, Save, Trash2, 
  Plus, Copy, Check, Monitor, Wifi, Cable, Edit2, FileText,
  Server, Globe, HardDrive
} from 'lucide-react'

interface NetworkAdapter {
  name: string
  description: string
  status: string
  mac_address: string | null
  ip_address: string | null
  subnet_mask: string | null
  gateway: string | null
  dns_servers: string[]
  dhcp_enabled: boolean
  speed: string | null
  adapter_type: string
}

interface NetworkProfile {
  id: string
  name: string
  adapter_name: string
  use_dhcp: boolean
  ip_address: string | null
  subnet_mask: string | null
  gateway: string | null
  dns_primary: string | null
  dns_secondary: string | null
}

interface HostsEntry {
  ip: string
  hostname: string
  comment: string | null
}

type ActiveTab = 'adapters' | 'profiles' | 'hosts' | 'settings'

const STORAGE_KEY = 'nettools_network_profiles'

export function NetworkProfilePage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('adapters')
  const [adapters, setAdapters] = useState<NetworkAdapter[]>([])
  const [profiles, setProfiles] = useState<NetworkProfile[]>([])
  const [hostsEntries, setHostsEntries] = useState<HostsEntry[]>([])
  const [computerName, setComputerName] = useState('')
  const [newComputerName, setNewComputerName] = useState('')
  
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Profile editor state
  const [editingProfile, setEditingProfile] = useState<NetworkProfile | null>(null)
  const [showProfileEditor, setShowProfileEditor] = useState(false)
  
  // Hosts editor state
  const [newHostIp, setNewHostIp] = useState('')
  const [newHostName, setNewHostName] = useState('')
  const [newHostComment, setNewHostComment] = useState('')

  // Load saved profiles from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setProfiles(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load profiles:', e)
      }
    }
  }, [])

  // Save profiles to localStorage
  const saveProfiles = (newProfiles: NetworkProfile[]) => {
    setProfiles(newProfiles)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newProfiles))
  }

  // Fetch adapters
  const fetchAdapters = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await invoke<NetworkAdapter[]>('get_network_adapters')
      setAdapters(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch hosts file
  const fetchHostsFile = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await invoke<HostsEntry[]>('get_hosts_file')
      setHostsEntries(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch computer name
  const fetchComputerName = async () => {
    try {
      const result = await invoke<string>('get_computer_name')
      setComputerName(result)
      setNewComputerName(result)
    } catch (e) {
      console.error('Failed to get computer name:', e)
    }
  }

  // Load data on mount
  useEffect(() => {
    fetchAdapters()
    fetchHostsFile()
    fetchComputerName()
  }, [])

  // Enable/Disable adapter
  const toggleAdapter = async (adapter: NetworkAdapter) => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    try {
      if (adapter.status === 'Up') {
        const result = await invoke<string>('disable_adapter', { adapterName: adapter.name })
        setSuccess(result)
      } else {
        const result = await invoke<string>('enable_adapter', { adapterName: adapter.name })
        setSuccess(result)
      }
      // Refresh adapters
      await fetchAdapters()
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Apply profile
  const applyProfile = async (profile: NetworkProfile) => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await invoke<string>('apply_network_profile', { profile })
      setSuccess(result)
      await fetchAdapters()
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Create new profile from current adapter config
  const createProfileFromAdapter = (adapter: NetworkAdapter) => {
    const newProfile: NetworkProfile = {
      id: Date.now().toString(),
      name: `${adapter.name} - Profil`,
      adapter_name: adapter.name,
      use_dhcp: adapter.dhcp_enabled,
      ip_address: adapter.ip_address,
      subnet_mask: adapter.subnet_mask,
      gateway: adapter.gateway,
      dns_primary: adapter.dns_servers[0] || null,
      dns_secondary: adapter.dns_servers[1] || null,
    }
    setEditingProfile(newProfile)
    setShowProfileEditor(true)
  }

  // Save profile
  const saveProfile = () => {
    if (!editingProfile) return
    
    const existing = profiles.findIndex(p => p.id === editingProfile.id)
    if (existing >= 0) {
      const updated = [...profiles]
      updated[existing] = editingProfile
      saveProfiles(updated)
    } else {
      saveProfiles([...profiles, editingProfile])
    }
    
    setShowProfileEditor(false)
    setEditingProfile(null)
    setSuccess('Profil gespeichert')
  }

  // Delete profile
  const deleteProfile = (id: string) => {
    saveProfiles(profiles.filter(p => p.id !== id))
    setSuccess('Profil gelöscht')
  }

  // Add hosts entry
  const addHostsEntry = () => {
    if (!newHostIp || !newHostName) return
    
    setHostsEntries([...hostsEntries, {
      ip: newHostIp,
      hostname: newHostName,
      comment: newHostComment || null
    }])
    
    setNewHostIp('')
    setNewHostName('')
    setNewHostComment('')
  }

  // Remove hosts entry
  const removeHostsEntry = (index: number) => {
    setHostsEntries(hostsEntries.filter((_, i) => i !== index))
  }

  // Save hosts file
  const saveHostsFile = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await invoke<string>('update_hosts_file', { entries: hostsEntries })
      setSuccess(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Flush DNS
  const flushDns = async () => {
    setIsLoading(true)
    try {
      const result = await invoke<string>('flush_dns_cache')
      setSuccess(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Renew DHCP
  const renewDhcp = async (adapterName: string) => {
    setIsLoading(true)
    try {
      const result = await invoke<string>('renew_dhcp', { adapterName })
      setSuccess(result)
      await fetchAdapters()
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Change computer name
  const changeComputerName = async () => {
    if (!newComputerName || newComputerName === computerName) return
    
    setIsLoading(true)
    setError(null)
    try {
      const result = await invoke<string>('set_computer_name', { newName: newComputerName })
      setSuccess(result)
      setComputerName(newComputerName)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  const getAdapterIcon = (adapter: NetworkAdapter) => {
    if (adapter.adapter_type?.toLowerCase().includes('wi-fi') || adapter.adapter_type?.toLowerCase().includes('wireless')) {
      return <Wifi className="w-5 h-5" />
    }
    return <Cable className="w-5 h-5" />
  }

  const TabButton = ({ id, label, icon }: { id: ActiveTab; label: string; icon: React.ReactNode }) => (
    <button
      onClick={() => { setActiveTab(id); setError(null); setSuccess(null) }}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
        activeTab === id 
          ? 'bg-accent-blue text-white' 
          : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
      }`}
    >
      {icon}
      {label}
    </button>
  )

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Network className="w-8 h-8 text-accent-blue" />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Netzwerk-Profile</h1>
            <p className="text-text-secondary">Verwalten Sie Netzwerkadapter und Profile</p>
          </div>
        </div>
        <Button variant="secondary" onClick={fetchAdapters} disabled={isLoading} icon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}>
          Aktualisieren
        </Button>
      </div>

      {/* Admin Warning */}
      <Alert variant="warning" title="Administrator-Rechte">
        Einige Funktionen (IP ändern, Adapter deaktivieren) erfordern Admin-Rechte. 
        Starten Sie die App als Administrator für volle Funktionalität.
      </Alert>

      {error && <Alert variant="error" title="Fehler">{error}</Alert>}
      {success && <Alert variant="success" title="Erfolg">{success}</Alert>}

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        <TabButton id="adapters" label="Adapter" icon={<Cable className="w-4 h-4" />} />
        <TabButton id="profiles" label="Profile" icon={<Save className="w-4 h-4" />} />
        <TabButton id="hosts" label="Hosts-Datei" icon={<FileText className="w-4 h-4" />} />
        <TabButton id="settings" label="Einstellungen" icon={<Settings className="w-4 h-4" />} />
      </div>

      {/* Adapters Tab */}
      {activeTab === 'adapters' && (
        <div className="space-y-4">
          {adapters.length === 0 ? (
            <Card variant="bordered">
              <CardContent className="py-12 text-center">
                <Network className="w-12 h-12 mx-auto mb-4 text-text-muted" />
                <p className="text-text-secondary">Keine Netzwerkadapter gefunden</p>
              </CardContent>
            </Card>
          ) : (
            adapters.map((adapter) => (
              <Card key={adapter.name} variant="bordered">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-lg ${adapter.status === 'Up' ? 'bg-accent-green/20 text-accent-green' : 'bg-bg-tertiary text-text-muted'}`}>
                        {getAdapterIcon(adapter)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-text-primary">{adapter.name}</h3>
                          <Badge variant={adapter.status === 'Up' ? 'success' : 'default'}>
                            {adapter.status === 'Up' ? 'Verbunden' : 'Getrennt'}
                          </Badge>
                          {adapter.dhcp_enabled && <Badge variant="info">DHCP</Badge>}
                        </div>
                        <p className="text-sm text-text-secondary">{adapter.description}</p>
                        
                        {adapter.status === 'Up' && (
                          <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-text-muted">IP-Adresse:</span>
                              <p className="font-mono text-text-primary">{adapter.ip_address || '-'}</p>
                            </div>
                            <div>
                              <span className="text-text-muted">Subnetzmaske:</span>
                              <p className="font-mono text-text-primary">{adapter.subnet_mask || '-'}</p>
                            </div>
                            <div>
                              <span className="text-text-muted">Gateway:</span>
                              <p className="font-mono text-text-primary">{adapter.gateway || '-'}</p>
                            </div>
                            <div>
                              <span className="text-text-muted">DNS:</span>
                              <p className="font-mono text-text-primary">{adapter.dns_servers.join(', ') || '-'}</p>
                            </div>
                            <div>
                              <span className="text-text-muted">MAC:</span>
                              <p className="font-mono text-text-primary">{adapter.mac_address || '-'}</p>
                            </div>
                            <div>
                              <span className="text-text-muted">Geschwindigkeit:</span>
                              <p className="font-mono text-text-primary">{adapter.speed || '-'}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => createProfileFromAdapter(adapter)}
                        icon={<Plus className="w-4 h-4" />}
                      >
                        Profil erstellen
                      </Button>
                      {adapter.dhcp_enabled && adapter.status === 'Up' && (
                        <Button 
                          variant="secondary" 
                          size="sm" 
                          onClick={() => renewDhcp(adapter.name)}
                          disabled={isLoading}
                          icon={<RefreshCw className="w-4 h-4" />}
                        >
                          DHCP erneuern
                        </Button>
                      )}
                      <Button
                        variant={adapter.status === 'Up' ? 'danger' : 'success'}
                        size="sm"
                        onClick={() => toggleAdapter(adapter)}
                        disabled={isLoading}
                        icon={adapter.status === 'Up' ? <PowerOff className="w-4 h-4" /> : <Power className="w-4 h-4" />}
                      >
                        {adapter.status === 'Up' ? 'Deaktivieren' : 'Aktivieren'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Profiles Tab */}
      {activeTab === 'profiles' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-text-secondary">Gespeicherte Netzwerkprofile zum schnellen Wechseln</p>
            <Button onClick={() => { setEditingProfile({ id: Date.now().toString(), name: '', adapter_name: adapters[0]?.name || '', use_dhcp: true, ip_address: null, subnet_mask: null, gateway: null, dns_primary: null, dns_secondary: null }); setShowProfileEditor(true) }} icon={<Plus className="w-4 h-4" />}>
              Neues Profil
            </Button>
          </div>

          {profiles.length === 0 ? (
            <Card variant="bordered">
              <CardContent className="py-12 text-center">
                <Save className="w-12 h-12 mx-auto mb-4 text-text-muted" />
                <p className="text-text-secondary">Keine Profile gespeichert</p>
                <p className="text-sm text-text-muted mt-1">Erstellen Sie ein Profil von einem Adapter oder klicken Sie auf "Neues Profil"</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profiles.map((profile) => (
                <Card key={profile.id} variant="bordered">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-text-primary">{profile.name}</h3>
                        <p className="text-sm text-text-secondary">Adapter: {profile.adapter_name}</p>
                      </div>
                      <Badge variant={profile.use_dhcp ? 'info' : 'warning'}>
                        {profile.use_dhcp ? 'DHCP' : 'Statisch'}
                      </Badge>
                    </div>
                    
                    {!profile.use_dhcp && (
                      <div className="text-sm space-y-1 mb-3">
                        <p><span className="text-text-muted">IP:</span> <span className="font-mono">{profile.ip_address}</span></p>
                        <p><span className="text-text-muted">Gateway:</span> <span className="font-mono">{profile.gateway || '-'}</span></p>
                        <p><span className="text-text-muted">DNS:</span> <span className="font-mono">{profile.dns_primary || '-'}</span></p>
                      </div>
                    )}
                    
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => applyProfile(profile)} disabled={isLoading} icon={<Check className="w-4 h-4" />} className="flex-1">
                        Anwenden
                      </Button>
                      <Button variant="secondary" size="sm" onClick={() => { setEditingProfile(profile); setShowProfileEditor(true) }} icon={<Edit2 className="w-4 h-4" />}>
                        Bearbeiten
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => deleteProfile(profile.id)} icon={<Trash2 className="w-4 h-4" />} />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Hosts File Tab */}
      {activeTab === 'hosts' && (
        <div className="space-y-4">
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>Hosts-Datei bearbeiten</CardTitle>
              <p className="text-sm text-text-muted">C:\Windows\System32\drivers\etc\hosts</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add new entry */}
              <div className="flex gap-2">
                <Input placeholder="IP-Adresse" value={newHostIp} onChange={(e) => setNewHostIp(e.target.value)} className="w-40" />
                <Input placeholder="Hostname" value={newHostName} onChange={(e) => setNewHostName(e.target.value)} className="flex-1" />
                <Input placeholder="Kommentar (optional)" value={newHostComment} onChange={(e) => setNewHostComment(e.target.value)} className="w-48" />
                <Button onClick={addHostsEntry} disabled={!newHostIp || !newHostName} icon={<Plus className="w-4 h-4" />}>
                  Hinzufügen
                </Button>
              </div>

              {/* Entries table */}
              <div className="max-h-64 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-bg-secondary">
                    <tr className="border-b border-border-default">
                      <th className="text-left py-2 px-3 text-text-secondary">IP-Adresse</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Hostname</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Kommentar</th>
                      <th className="w-10"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {hostsEntries.map((entry, idx) => (
                      <tr key={idx} className="border-b border-border-default hover:bg-bg-hover">
                        <td className="py-2 px-3 font-mono">{entry.ip}</td>
                        <td className="py-2 px-3 font-mono">{entry.hostname}</td>
                        <td className="py-2 px-3 text-text-muted">{entry.comment || '-'}</td>
                        <td className="py-2 px-3">
                          <Button variant="ghost" size="sm" onClick={() => removeHostsEntry(idx)} icon={<Trash2 className="w-4 h-4" />} />
                        </td>
                      </tr>
                    ))}
                    {hostsEntries.length === 0 && (
                      <tr><td colSpan={4} className="py-8 text-center text-text-muted">Keine benutzerdefinierten Einträge</td></tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="secondary" onClick={fetchHostsFile} icon={<RefreshCw className="w-4 h-4" />}>
                  Neu laden
                </Button>
                <Button onClick={saveHostsFile} disabled={isLoading} icon={<Save className="w-4 h-4" />}>
                  Speichern
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Computer Name */}
          <Card variant="bordered">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Monitor className="w-5 h-5 text-accent-purple" />
                <CardTitle>Computer-Name</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-text-muted mb-2">Aktueller Name:</p>
                <p className="font-mono text-lg text-text-primary">{computerName}</p>
              </div>
              <div className="flex gap-2">
                <Input value={newComputerName} onChange={(e) => setNewComputerName(e.target.value)} placeholder="Neuer Name" className="flex-1" />
                <Button onClick={changeComputerName} disabled={isLoading || newComputerName === computerName} icon={<Save className="w-4 h-4" />}>
                  Ändern
                </Button>
              </div>
              <p className="text-xs text-text-muted">⚠️ Erfordert Neustart</p>
            </CardContent>
          </Card>

          {/* DNS Actions */}
          <Card variant="bordered">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-accent-cyan" />
                <CardTitle>DNS-Aktionen</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={flushDns} disabled={isLoading} className="w-full" icon={<RefreshCw className="w-4 h-4" />}>
                DNS-Cache leeren
              </Button>
              <p className="text-xs text-text-muted">Löscht den lokalen DNS-Resolver-Cache</p>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card variant="bordered" className="md:col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-accent-yellow" />
                <CardTitle>Schnellaktionen</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" onClick={() => { window.open('ms-settings:network', '_blank') }} icon={<Settings className="w-4 h-4" />}>
                  Windows Netzwerkeinstellungen
                </Button>
                <Button variant="secondary" onClick={() => { window.open('ncpa.cpl', '_blank') }} icon={<Network className="w-4 h-4" />}>
                  Netzwerkverbindungen
                </Button>
                <Button variant="secondary" onClick={() => { window.open('devmgmt.msc', '_blank') }} icon={<HardDrive className="w-4 h-4" />}>
                  Geräte-Manager
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Profile Editor Modal */}
      {showProfileEditor && editingProfile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card variant="bordered" className="w-full max-w-lg">
            <CardHeader>
              <CardTitle>{editingProfile.id ? 'Profil bearbeiten' : 'Neues Profil'}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input 
                label="Profilname" 
                value={editingProfile.name} 
                onChange={(e) => setEditingProfile({ ...editingProfile, name: e.target.value })}
                placeholder="z.B. Büro, Zuhause, VPN"
              />
              
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Netzwerkadapter</label>
                <select 
                  value={editingProfile.adapter_name}
                  onChange={(e) => setEditingProfile({ ...editingProfile, adapter_name: e.target.value })}
                  className="w-full bg-bg-tertiary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary"
                >
                  {adapters.map(a => (
                    <option key={a.name} value={a.name}>{a.name}</option>
                  ))}
                </select>
              </div>

              <Checkbox 
                label="DHCP verwenden (automatische IP)" 
                checked={editingProfile.use_dhcp}
                onChange={(e) => setEditingProfile({ ...editingProfile, use_dhcp: e.target.checked })}
              />

              {!editingProfile.use_dhcp && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <Input 
                      label="IP-Adresse" 
                      value={editingProfile.ip_address || ''} 
                      onChange={(e) => setEditingProfile({ ...editingProfile, ip_address: e.target.value })}
                      placeholder="192.168.1.100"
                    />
                    <Input 
                      label="Subnetzmaske" 
                      value={editingProfile.subnet_mask || ''} 
                      onChange={(e) => setEditingProfile({ ...editingProfile, subnet_mask: e.target.value })}
                      placeholder="255.255.255.0"
                    />
                  </div>
                  <Input 
                    label="Standard-Gateway" 
                    value={editingProfile.gateway || ''} 
                    onChange={(e) => setEditingProfile({ ...editingProfile, gateway: e.target.value })}
                    placeholder="192.168.1.1"
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <Input 
                      label="Primärer DNS" 
                      value={editingProfile.dns_primary || ''} 
                      onChange={(e) => setEditingProfile({ ...editingProfile, dns_primary: e.target.value })}
                      placeholder="8.8.8.8"
                    />
                    <Input 
                      label="Sekundärer DNS" 
                      value={editingProfile.dns_secondary || ''} 
                      onChange={(e) => setEditingProfile({ ...editingProfile, dns_secondary: e.target.value })}
                      placeholder="8.8.4.4"
                    />
                  </div>
                </>
              )}

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="secondary" onClick={() => { setShowProfileEditor(false); setEditingProfile(null) }}>
                  Abbrechen
                </Button>
                <Button onClick={saveProfile} disabled={!editingProfile.name} icon={<Save className="w-4 h-4" />}>
                  Speichern
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
