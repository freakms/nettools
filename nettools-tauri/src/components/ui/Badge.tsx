import { cn } from '@/lib/utils'

interface BadgeProps {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info'
  children: React.ReactNode
  className?: string
}

const variants = {
  default: 'bg-bg-tertiary text-text-secondary',
  success: 'bg-accent-green/20 text-accent-green',
  error: 'bg-accent-red/20 text-accent-red',
  warning: 'bg-accent-yellow/20 text-accent-yellow',
  info: 'bg-accent-blue/20 text-accent-blue',
}

export function Badge({ variant = 'default', children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  )
}

// Status badge specifically for online/offline states
interface StatusBadgeProps {
  status: 'online' | 'offline' | 'timeout' | 'open' | 'closed' | 'filtered' | 'unknown'
  className?: string
}

const statusConfig = {
  online: { variant: 'success' as const, label: 'Online' },
  offline: { variant: 'error' as const, label: 'Offline' },
  timeout: { variant: 'warning' as const, label: 'Timeout' },
  open: { variant: 'success' as const, label: 'Offen' },
  closed: { variant: 'error' as const, label: 'Geschlossen' },
  filtered: { variant: 'warning' as const, label: 'Gefiltert' },
  unknown: { variant: 'default' as const, label: 'Unbekannt' },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.unknown
  return (
    <Badge variant={config.variant} className={className}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {config.label}
    </Badge>
  )
}
