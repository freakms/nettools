import { useState, useEffect } from 'react'
import { Sidebar, Header, CommandPalette } from '@/components/layout'
import { ToastContainer } from '@/components/ui'
import { 
  DashboardPage, SettingsPage,
  ScannerPage, PortScanPage, DnsPage, TraceroutePage,
  SubnetPage, HashPage, PasswordPage, ArpPage, MacPage, PanosPage,
  WhoisPage, SslPage, BandwidthPage, ApiTesterPage
} from '@/pages'
import { useStore } from '@/store'

function App() {
  const { activeTool, sidebarCollapsed, toggleSidebar, toasts, removeToast } = useStore()
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const renderPage = () => {
    switch (activeTool) {
      case 'dashboard':
        return <DashboardPage />
      case 'settings':
        return <SettingsPage />
      case 'scanner':
        return <ScannerPage />
      case 'portscan':
        return <PortScanPage />
      case 'dns':
        return <DnsPage />
      case 'traceroute':
        return <TraceroutePage />
      case 'subnet':
        return <SubnetPage />
      case 'hash':
        return <HashPage />
      case 'password':
        return <PasswordPage />
      case 'arp':
        return <ArpPage />
      case 'mac':
        return <MacPage />
      case 'panos':
        return <PanosPage />
      case 'whois':
        return <WhoisPage />
      case 'ssl':
        return <SslPage />
      case 'bandwidth':
        return <BandwidthPage />
      case 'api-tester':
        return <ApiTesterPage />
      default:
        return <DashboardPage />
    }
  }

  return (
    <div className="flex h-screen bg-bg-primary overflow-hidden">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={toggleSidebar} 
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Header onOpenCommandPalette={() => setCommandPaletteOpen(true)} />
        <main className="flex-1 overflow-hidden bg-bg-primary">
          {renderPage()}
        </main>
      </div>

      <CommandPalette 
        isOpen={commandPaletteOpen} 
        onClose={() => setCommandPaletteOpen(false)} 
      />

      <ToastContainer toasts={toasts.map(t => ({...t, onClose: removeToast}))} onClose={removeToast} />
    </div>
  )
}

export default App
