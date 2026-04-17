// =============================================================================
// ScannerPage.tsx – Änderungen (gezielt, nicht komplette Datei)
// =============================================================================

// -----------------------------------------------------------------------------
// 1) Imports ergänzen (oben in der Datei)
// -----------------------------------------------------------------------------

// ALT:
import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'

// NEU – listen für Progress-Events hinzufügen:
import { useState, useEffect, useRef } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import { AlertTriangle } from 'lucide-react'  // zum vorhandenen lucide-import hinzufügen

// -----------------------------------------------------------------------------
// 2) Interface PingResult – mac/vendor entfernen (existieren im Backend nicht)
// -----------------------------------------------------------------------------

// ALT:
interface PingResult {
  ip: string
  hostname: string | null
  mac: string | null       // ← entfernen
  vendor: string | null    // ← entfernen
  status: string
  rtt: number | null
  ttl: number | null
}

// NEU:
interface PingResult {
  ip: string
  hostname: string | null
  status: string
  rtt: number | null
  ttl: number | null
}

// -----------------------------------------------------------------------------
// 3) Interface ScanResult – warning Feld hinzufügen
// -----------------------------------------------------------------------------

// ALT:
interface ScanResult {
  results: PingResult[]
  total_hosts: number
  responding_hosts: number
  duration_ms: number
}

// NEU:
interface ScanResult {
  results: PingResult[]
  total_hosts: number
  responding_hosts: number
  duration_ms: number
  warning: string | null   // ← neu: Warnung bei großen Netzen
}

// Neues Interface für Progress-Events:
interface ScanProgress {
  completed: number
  total: number
  latest: PingResult | null
}

// -----------------------------------------------------------------------------
// 4) State-Ergänzungen (innerhalb der ScannerPage Komponente)
// -----------------------------------------------------------------------------

// Diese Zeilen zu den bestehenden useState-Deklarationen hinzufügen:
const [scanWarning, setScanWarning] = useState<string | null>(null)
const [progress, setProgress] = useState<ScanProgress | null>(null)
const unlistenRef = useRef<(() => void) | null>(null)

// -----------------------------------------------------------------------------
// 5) startScan Funktion – komplett ersetzen
// -----------------------------------------------------------------------------

// ALT (die gesamte startScan Funktion):
const startScan = async () => {
  setIsScanning(true)
  setError(null)
  setResults(null)
  setComparison(null)
  setCurrentPage(1)
  try {
    const result = await invoke<ScanResult>('scan_network', { target, timeoutMs: parseInt(timeout), onlyResponding: false })
    setResults(result)
    // ... hostname resolution ...
  } catch (e) { setError(String(e)) } finally { setIsScanning(false) }
}

// NEU:
const startScan = async () => {
  setIsScanning(true)
  setError(null)
  setResults(null)
  setComparison(null)
  setScanWarning(null)
  setProgress(null)
  setCurrentPage(1)

  // Progress-Events abonnieren
  const unlisten = await listen<ScanProgress>('scan-progress', (event) => {
    setProgress(event.payload)
  })
  unlistenRef.current = unlisten

  try {
    const result = await invoke<ScanResult>('scan_network', {
      target,
      timeoutMs: parseInt(timeout),
      onlyResponding: false,
    })

    // Warnung aus dem Backend anzeigen (großes Netz etc.)
    if (result.warning) {
      setScanWarning(result.warning)
    }

    setResults(result)

    // Hostnames für Online-Hosts nachladen (optional, non-blocking)
    const onlineIps = result.results
      .filter(r => r.status === 'online' && !r.hostname)
      .map(r => r.ip)

    if (onlineIps.length > 0 && onlineIps.length <= 200) {
      // Nur bei überschaubarer Anzahl automatisch auflösen
      invoke<[string, string | null][]>('resolve_hostnames_batch', { ips: onlineIps })
        .then(resolved => {
          const hostnameMap = new Map(resolved)
          setResults(prev => {
            if (!prev) return prev
            return {
              ...prev,
              results: prev.results.map(r => ({
                ...r,
                hostname: hostnameMap.get(r.ip) ?? r.hostname,
              })),
            }
          })
        })
        .catch(() => { /* Hostname-Auflösung ist optional */ })
    }
  } catch (e) {
    setError(String(e))
  } finally {
    setIsScanning(false)
    setProgress(null)
    // Event-Listener aufräumen
    if (unlistenRef.current) {
      unlistenRef.current()
      unlistenRef.current = null
    }
  }
}

// cancelScan anpassen – auch unlisten aufräumen:
const cancelScan = () => {
  setIsScanning(false)
  if (unlistenRef.current) {
    unlistenRef.current()
    unlistenRef.current = null
  }
}

// useEffect für Cleanup beim Unmount ergänzen:
useEffect(() => {
  return () => {
    if (unlistenRef.current) {
      unlistenRef.current()
    }
  }
}, [])

// -----------------------------------------------------------------------------
// 6) JSX – Warnung und Progress-Bar anzeigen
// -----------------------------------------------------------------------------
// Diese Blöcke direkt VOR dem bestehenden {error && <Alert ...>} einfügen:

{scanWarning && !isScanning && (
  <Alert variant="warning" title="Hinweis">
    <div className="flex items-center gap-2">
      <AlertTriangle className="w-4 h-4" />
      {scanWarning}
    </div>
  </Alert>
)}

{isScanning && progress && (
  <div className="space-y-1">
    <div className="flex justify-between text-sm text-text-secondary">
      <span>Scanne… {progress.completed} / {progress.total} Hosts</span>
      <span>{Math.round((progress.completed / progress.total) * 100)}%</span>
    </div>
    <div className="w-full bg-bg-secondary rounded-full h-2">
      <div
        className="bg-accent-blue h-2 rounded-full transition-all duration-200"
        style={{ width: `${(progress.completed / progress.total) * 100}%` }}
      />
    </div>
    {progress.latest && progress.latest.status === 'online' && (
      <p className="text-xs text-accent-green">
        ✓ {progress.latest.ip}
        {progress.latest.hostname ? ` (${progress.latest.hostname})` : ''}
        {progress.latest.rtt ? ` – ${progress.latest.rtt.toFixed(1)} ms` : ''}
      </p>
    )}
  </div>
)}
