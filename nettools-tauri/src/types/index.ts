// Scan result types
export interface ScanResult {
  ip: string
  hostname: string | null
  status: 'online' | 'offline' | 'timeout'
  rtt: number | null
  mac?: string
  vendor?: string
  timestamp: string
}

export interface ScanProfile {
  id: string
  name: string
  target: string
  aggressiveness: 'low' | 'medium' | 'high'
  showOnlyResponding: boolean
  createdAt: string
  updatedAt: string
}

export interface ScanSession {
  id: string
  target: string
  startTime: string
  endTime: string | null
  totalHosts: number
  respondingHosts: number
  results: ScanResult[]
}

// Port scan types
export interface PortScanResult {
  port: number
  status: 'open' | 'closed' | 'filtered'
  service: string | null
  banner?: string
}

export interface PortScanSession {
  id: string
  target: string
  ports: string
  startTime: string
  endTime: string | null
  results: PortScanResult[]
}

// DNS types
export interface DNSRecord {
  type: string
  name: string
  value: string
  ttl: number
}

export interface DNSLookupResult {
  id: string
  domain: string
  records: DNSRecord[]
  timestamp: string
}

// Traceroute types
export interface TracerouteHop {
  hop: number
  ip: string | null
  hostname: string | null
  rtt1: number | null
  rtt2: number | null
  rtt3: number | null
}

export interface TracerouteResult {
  id: string
  target: string
  hops: TracerouteHop[]
  timestamp: string
}

// ARP types
export interface ARPEntry {
  ip: string
  mac: string
  interface: string
  type: string
}

// WHOIS types
export interface WhoisResult {
  domain: string
  registrar: string | null
  creationDate: string | null
  expirationDate: string | null
  nameServers: string[]
  status: string[]
  rawData: string
  timestamp: string
}

// SSL types
export interface SSLCertificate {
  subject: string
  issuer: string
  validFrom: string
  validTo: string
  serialNumber: string
  signatureAlgorithm: string
  isValid: boolean
  daysUntilExpiry: number
  chain: SSLCertificateChain[]
}

export interface SSLCertificateChain {
  subject: string
  issuer: string
  validFrom: string
  validTo: string
}

export interface SSLCheckResult {
  host: string
  port: number
  certificate: SSLCertificate | null
  error: string | null
  timestamp: string
}

// Subnet types
export interface SubnetInfo {
  network: string
  broadcast: string
  netmask: string
  wildcardMask: string
  firstHost: string
  lastHost: string
  totalHosts: number
  usableHosts: number
  cidr: number
  ipClass: string
  isPrivate: boolean
}

// Bandwidth types
export interface BandwidthResult {
  server: string
  port: number
  protocol: 'tcp' | 'udp'
  direction: 'upload' | 'download' | 'both'
  bandwidth: number
  jitter?: number
  packetLoss?: number
  duration: number
  timestamp: string
}

// Hash types
export interface HashResult {
  input: string
  inputType: 'text' | 'file'
  md5: string
  sha1: string
  sha256: string
  sha512: string
  timestamp: string
}

// API Tester types
export interface APIRequest {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS'
  url: string
  headers: Record<string, string>
  body?: string
  timeout: number
}

export interface APIResponse {
  statusCode: number
  statusText: string
  headers: Record<string, string>
  body: string
  duration: number
  size: number
  timestamp: string
}

// PAN-OS types
export interface PANOSConfig {
  hostname: string
  interfaces: PANOSInterface[]
  zones: PANOSZone[]
  policies: PANOSPolicy[]
}

export interface PANOSInterface {
  name: string
  ip: string
  netmask: string
  zone: string
  type: 'ethernet' | 'vlan' | 'loopback'
}

export interface PANOSZone {
  name: string
  type: 'layer3' | 'layer2' | 'virtual-wire'
  interfaces: string[]
}

export interface PANOSPolicy {
  name: string
  sourceZone: string[]
  destinationZone: string[]
  source: string[]
  destination: string[]
  application: string[]
  service: string[]
  action: 'allow' | 'deny' | 'drop'
}

// App settings
export interface AppSettings {
  theme: 'dark' | 'light' | 'system'
  language: 'de' | 'en'
  accentColor: string
  enabledTools: string[]
  favorites: string[]
  scanDefaults: {
    aggressiveness: 'low' | 'medium' | 'high'
    showOnlyResponding: boolean
    resultsPerPage: number
  }
  shortcuts: Record<string, string>
}

// Toast notification types
export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}
