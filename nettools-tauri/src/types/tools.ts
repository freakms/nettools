// Tool definitions for the application
export type ToolId = 
  | 'dashboard'
  | 'scanner'
  | 'portscan'
  | 'dns'
  | 'traceroute'
  | 'arp'
  | 'subnet'
  | 'bandwidth'
  | 'whois'
  | 'ssl'
  | 'mac'
  | 'hash'
  | 'password'
  | 'api-tester'
  | 'panos'
  | 'live-monitor'
  | 'settings'

export interface Tool {
  id: ToolId
  name: string
  description: string
  icon: string
  category: 'dashboard' | 'scanning' | 'network' | 'lookup' | 'utilities' | 'integration' | 'settings'
  shortcut?: string
}

export const TOOLS: Tool[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    description: 'Übersicht und Schnellzugriff',
    icon: 'LayoutDashboard',
    category: 'dashboard',
    shortcut: 'Ctrl+1',
  },
  {
    id: 'live-monitor',
    name: 'Live Monitor',
    description: 'Echtzeit-Ping-Überwachung',
    icon: 'Activity',
    category: 'scanning',
    shortcut: 'Ctrl+L',
  },
  {
    id: 'scanner',
    name: 'IPv4 Scanner',
    description: 'Netzwerk-Hosts scannen',
    icon: 'Radar',
    category: 'scanning',
    shortcut: 'Ctrl+2',
  },
  {
    id: 'portscan',
    name: 'Port Scanner',
    description: 'Offene Ports finden',
    icon: 'Network',
    category: 'scanning',
    shortcut: 'Ctrl+3',
  },
  {
    id: 'dns',
    name: 'DNS Lookup',
    description: 'DNS-Einträge abfragen',
    icon: 'Globe',
    category: 'network',
    shortcut: 'Ctrl+4',
  },
  {
    id: 'traceroute',
    name: 'Traceroute',
    description: 'Netzwerkpfad verfolgen',
    icon: 'Route',
    category: 'network',
    shortcut: 'Ctrl+5',
  },
  {
    id: 'arp',
    name: 'ARP Viewer',
    description: 'ARP-Tabelle anzeigen',
    icon: 'Table2',
    category: 'network',
  },
  {
    id: 'subnet',
    name: 'Subnet Calculator',
    description: 'Subnetz berechnen',
    icon: 'Calculator',
    category: 'network',
    shortcut: 'Ctrl+6',
  },
  {
    id: 'bandwidth',
    name: 'Bandwidth Test',
    description: 'Bandbreite messen (iperf3)',
    icon: 'Gauge',
    category: 'network',
  },
  {
    id: 'whois',
    name: 'WHOIS',
    description: 'Domain-Informationen',
    icon: 'Search',
    category: 'lookup',
  },
  {
    id: 'ssl',
    name: 'SSL Checker',
    description: 'SSL-Zertifikate prüfen',
    icon: 'ShieldCheck',
    category: 'lookup',
  },
  {
    id: 'mac',
    name: 'MAC Formatter',
    description: 'MAC-Adressen & OUI',
    icon: 'Fingerprint',
    category: 'utilities',
    shortcut: 'Ctrl+7',
  },
  {
    id: 'hash',
    name: 'Hash Generator',
    description: 'Hash-Werte erzeugen',
    icon: 'Hash',
    category: 'utilities',
  },
  {
    id: 'password',
    name: 'Password Generator',
    description: 'Sichere Passwörter',
    icon: 'Key',
    category: 'utilities',
  },
  {
    id: 'api-tester',
    name: 'API Tester',
    description: 'HTTP-Requests testen',
    icon: 'Send',
    category: 'utilities',
  },
  {
    id: 'panos',
    name: 'PAN-OS Generator',
    description: 'Palo Alto Konfiguration',
    icon: 'Shield',
    category: 'integration',
  },
  {
    id: 'settings',
    name: 'Einstellungen',
    description: 'App konfigurieren',
    icon: 'Settings',
    category: 'settings',
    shortcut: 'Ctrl+,',
  },
]

export const TOOL_CATEGORIES = [
  { id: 'dashboard', name: 'Dashboard', order: 0 },
  { id: 'scanning', name: 'Scanning', order: 1 },
  { id: 'network', name: 'Netzwerk-Tools', order: 2 },
  { id: 'lookup', name: 'Lookup', order: 3 },
  { id: 'utilities', name: 'Utilities', order: 4 },
  { id: 'integration', name: 'Integrationen', order: 5 },
  { id: 'settings', name: 'Einstellungen', order: 6 },
] as const

export function getToolById(id: ToolId): Tool | undefined {
  return TOOLS.find(tool => tool.id === id)
}

export function getToolsByCategory(category: string): Tool[] {
  return TOOLS.filter(tool => tool.category === category)
}
