import { useState, useEffect } from 'react'
import { Sidebar, Header, CommandPalette } from '@/components/layout'
import { ToastContainer } from '@/components/ui'
import { DashboardPage, SettingsPage, PlaceholderPage } from '@/pages'
import { useStore } from '@/store'
import { getToolById } from '@/types/tools'
import { 
  Radar, Network, Globe, Route, Table2, Calculator, 
  Gauge, Search, ShieldCheck, Fingerprint, Hash, Key, Send, Shield 
} from 'lucide-react'

function App() {
  const { activeTool, sidebarCollapsed, toggleSidebar, toasts, removeToast } = useStore()
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K - Open command palette
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Render the active tool page
  const renderPage = () => {
    // Tool info available via getToolById(activeTool) if needed
    
    switch (activeTool) {
      case 'dashboard':
        return <DashboardPage />
      case 'settings':
        return <SettingsPage />
      case 'scanner':
        return (
          <PlaceholderPage 
            title="IPv4 Scanner" 
            description="Scannen Sie Ihr Netzwerk nach aktiven Hosts"
            icon={<Radar className="w-16 h-16 text-accent-blue" />}
          />
        )
      case 'portscan':
        return (
          <PlaceholderPage 
            title="Port Scanner" 
            description="Finden Sie offene Ports auf Zielsystemen"
            icon={<Network className="w-16 h-16 text-accent-blue" />}
          />
        )
      case 'dns':
        return (
          <PlaceholderPage 
            title="DNS Lookup" 
            description="Fragen Sie DNS-Einträge ab"
            icon={<Globe className="w-16 h-16 text-accent-green" />}
          />
        )
      case 'traceroute':
        return (
          <PlaceholderPage 
            title="Traceroute" 
            description="Verfolgen Sie den Netzwerkpfad zu einem Ziel"
            icon={<Route className="w-16 h-16 text-accent-green" />}
          />
        )
      case 'arp':
        return (
          <PlaceholderPage 
            title="ARP Viewer" 
            description="Zeigen Sie die ARP-Tabelle an"
            icon={<Table2 className="w-16 h-16 text-accent-green" />}
          />
        )
      case 'subnet':
        return (
          <PlaceholderPage 
            title="Subnet Calculator" 
            description="Berechnen Sie Subnetz-Informationen"
            icon={<Calculator className="w-16 h-16 text-accent-green" />}
          />
        )
      case 'bandwidth':
        return (
          <PlaceholderPage 
            title="Bandwidth Test" 
            description="Messen Sie die Netzwerk-Bandbreite mit iperf3"
            icon={<Gauge className="w-16 h-16 text-accent-cyan" />}
          />
        )
      case 'whois':
        return (
          <PlaceholderPage 
            title="WHOIS Lookup" 
            description="Rufen Sie Domain-Registrierungsinformationen ab"
            icon={<Search className="w-16 h-16 text-accent-purple" />}
          />
        )
      case 'ssl':
        return (
          <PlaceholderPage 
            title="SSL Checker" 
            description="Überprüfen Sie SSL-Zertifikate"
            icon={<ShieldCheck className="w-16 h-16 text-accent-green" />}
          />
        )
      case 'mac':
        return (
          <PlaceholderPage 
            title="MAC Formatter" 
            description="Formatieren Sie MAC-Adressen und schauen Sie OUI nach"
            icon={<Fingerprint className="w-16 h-16 text-accent-purple" />}
          />
        )
      case 'hash':
        return (
          <PlaceholderPage 
            title="Hash Generator" 
            description="Erzeugen Sie Hash-Werte für Text und Dateien"
            icon={<Hash className="w-16 h-16 text-accent-yellow" />}
          />
        )
      case 'password':
        return (
          <PlaceholderPage 
            title="Password Generator" 
            description="Generieren Sie sichere Passwörter"
            icon={<Key className="w-16 h-16 text-accent-yellow" />}
          />
        )
      case 'api-tester':
        return (
          <PlaceholderPage 
            title="API Tester" 
            description="Testen Sie HTTP-Requests"
            icon={<Send className="w-16 h-16 text-accent-blue" />}
          />
        )
      case 'panos':
        return (
          <PlaceholderPage 
            title="PAN-OS Generator" 
            description="Generieren Sie Palo Alto Firewall-Konfigurationen"
            icon={<Shield className="w-16 h-16 text-accent-red" />}
          />
        )
      default:
        return <DashboardPage />
    }
  }

  return (
    <div className="flex h-screen bg-bg-primary overflow-hidden">
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={toggleSidebar} 
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onOpenCommandPalette={() => setCommandPaletteOpen(true)} />
        <main className="flex-1 overflow-hidden bg-bg-primary">
          {renderPage()}
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette 
        isOpen={commandPaletteOpen} 
        onClose={() => setCommandPaletteOpen(false)} 
      />

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts.map(t => ({...t, onClose: removeToast}))} onClose={removeToast} />
    </div>
  )
}

export default App
