import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const minutes = Math.floor(ms / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  return `${minutes}m ${seconds}s`
}

export function formatDate(date: Date | string): string {
  const d = new Date(date)
  return d.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function isValidIPv4(ip: string): boolean {
  const pattern = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!pattern.test(ip)) return false
  const parts = ip.split('.')
  return parts.every(part => {
    const num = parseInt(part, 10)
    return num >= 0 && num <= 255
  })
}

export function isValidCIDR(cidr: string): boolean {
  const parts = cidr.split('/')
  if (parts.length !== 2) return false
  if (!isValidIPv4(parts[0])) return false
  const prefix = parseInt(parts[1], 10)
  return prefix >= 0 && prefix <= 32
}

export function isValidHostname(hostname: string): boolean {
  const pattern = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
  return pattern.test(hostname)
}

export function isValidPort(port: number | string): boolean {
  const p = typeof port === 'string' ? parseInt(port, 10) : port
  return !isNaN(p) && p >= 1 && p <= 65535
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 11)
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text)
}

export function downloadFile(content: string, filename: string, mimeType = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function parsePortRange(range: string): number[] {
  const ports: number[] = []
  const parts = range.split(',').map(p => p.trim())
  
  for (const part of parts) {
    if (part.includes('-')) {
      const [start, end] = part.split('-').map(p => parseInt(p.trim(), 10))
      if (!isNaN(start) && !isNaN(end) && start <= end) {
        for (let i = start; i <= end && i <= 65535; i++) {
          if (i >= 1) ports.push(i)
        }
      }
    } else {
      const port = parseInt(part, 10)
      if (isValidPort(port)) ports.push(port)
    }
  }
  
  return [...new Set(ports)].sort((a, b) => a - b)
}

export function ipToNumber(ip: string): number {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0
}

export function numberToIp(num: number): string {
  return [
    (num >>> 24) & 255,
    (num >>> 16) & 255,
    (num >>> 8) & 255,
    num & 255,
  ].join('.')
}

export function getNetworkRange(cidr: string): { start: string; end: string; count: number } {
  const [ip, prefixStr] = cidr.split('/')
  const prefix = parseInt(prefixStr, 10)
  const ipNum = ipToNumber(ip)
  const mask = ~((1 << (32 - prefix)) - 1) >>> 0
  const network = (ipNum & mask) >>> 0
  const broadcast = (network | ~mask) >>> 0
  
  return {
    start: numberToIp(network + 1),
    end: numberToIp(broadcast - 1),
    count: Math.pow(2, 32 - prefix) - 2,
  }
}
