import React from 'react'
import { cn } from '@/lib/utils'
import { AlertCircle, CheckCircle, AlertTriangle, Info } from 'lucide-react'

interface AlertProps {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info'
  title?: string
  children: React.ReactNode
  className?: string
}

const variants = {
  default: {
    container: 'bg-bg-tertiary border-border-default',
    icon: Info,
    iconColor: 'text-text-secondary',
  },
  success: {
    container: 'bg-accent-green/10 border-accent-green/30',
    icon: CheckCircle,
    iconColor: 'text-accent-green',
  },
  error: {
    container: 'bg-accent-red/10 border-accent-red/30',
    icon: AlertCircle,
    iconColor: 'text-accent-red',
  },
  warning: {
    container: 'bg-accent-yellow/10 border-accent-yellow/30',
    icon: AlertTriangle,
    iconColor: 'text-accent-yellow',
  },
  info: {
    container: 'bg-accent-blue/10 border-accent-blue/30',
    icon: Info,
    iconColor: 'text-accent-blue',
  },
}

export function Alert({ variant = 'default', title, children, className }: AlertProps) {
  const config = variants[variant]
  const Icon = config.icon

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg border',
        config.container,
        className
      )}
      role="alert"
    >
      <Icon className={cn('w-5 h-5 shrink-0 mt-0.5', config.iconColor)} />
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="text-sm font-medium text-text-primary mb-1">{title}</h4>
        )}
        <div className="text-sm text-text-secondary">{children}</div>
      </div>
    </div>
  )
}
