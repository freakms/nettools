import React from 'react'
import { cn } from '@/lib/utils'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'

export interface ToastProps {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  onClose: (id: string) => void
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const colors = {
  success: 'border-l-accent-green',
  error: 'border-l-accent-red',
  warning: 'border-l-accent-yellow',
  info: 'border-l-accent-blue',
}

const iconColors = {
  success: 'text-accent-green',
  error: 'text-accent-red',
  warning: 'text-accent-yellow',
  info: 'text-accent-blue',
}

export function Toast({ id, type, title, message, onClose }: ToastProps) {
  const Icon = icons[type]
  
  return (
    <div
      className={cn(
        'flex items-start gap-3 bg-bg-card border border-border-default rounded-lg p-4 shadow-dropdown animate-slide-in',
        'border-l-4',
        colors[type]
      )}
      role="alert"
    >
      <Icon className={cn('w-5 h-5 shrink-0 mt-0.5', iconColors[type])} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">{title}</p>
        {message && (
          <p className="mt-1 text-sm text-text-secondary">{message}</p>
        )}
      </div>
      <button
        onClick={() => onClose(id)}
        className="shrink-0 text-text-muted hover:text-text-primary transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastProps[]
  onClose: (id: string) => void
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  )
}
