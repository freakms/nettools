import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown } from 'lucide-react'

interface DropdownItem {
  id: string
  label: string
  icon?: React.ReactNode
  disabled?: boolean
  danger?: boolean
  divider?: boolean
}

interface DropdownProps {
  trigger: React.ReactNode
  items: DropdownItem[]
  onSelect: (id: string) => void
  align?: 'left' | 'right'
  className?: string
}

export function Dropdown({ trigger, items, onSelect, align = 'left', className }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={dropdownRef} className={cn('relative inline-block', className)}>
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>
      
      {isOpen && (
        <div
          className={cn(
            'absolute z-50 mt-1 min-w-[160px] py-1 bg-bg-card border border-border-default rounded-lg shadow-dropdown animate-fade-in',
            align === 'right' ? 'right-0' : 'left-0'
          )}
        >
          {items.map((item, index) => {
            if (item.divider) {
              return <div key={index} className="my-1 border-t border-border-default" />
            }
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (!item.disabled) {
                    onSelect(item.id)
                    setIsOpen(false)
                  }
                }}
                disabled={item.disabled}
                className={cn(
                  'w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors',
                  item.disabled && 'opacity-50 cursor-not-allowed',
                  item.danger 
                    ? 'text-accent-red hover:bg-accent-red/10' 
                    : 'text-text-primary hover:bg-bg-hover'
                )}
              >
                {item.icon && <span className="w-4 h-4 shrink-0">{item.icon}</span>}
                {item.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Simple dropdown button variant
interface DropdownButtonProps {
  label: string
  items: DropdownItem[]
  onSelect: (id: string) => void
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function DropdownButton({ 
  label, 
  items, 
  onSelect, 
  variant = 'secondary',
  size = 'md',
  className 
}: DropdownButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200'
  
  const variants = {
    primary: 'bg-accent-blue hover:bg-blue-600 text-white',
    secondary: 'bg-bg-tertiary hover:bg-bg-hover text-text-primary border border-border-default',
    ghost: 'bg-transparent hover:bg-bg-hover text-text-secondary hover:text-text-primary',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  return (
    <div ref={dropdownRef} className={cn('relative inline-block', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(baseStyles, variants[variant], sizes[size])}
      >
        {label}
        <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
      </button>
      
      {isOpen && (
        <div className="absolute z-50 mt-1 right-0 min-w-[160px] py-1 bg-bg-card border border-border-default rounded-lg shadow-dropdown animate-fade-in">
          {items.map((item, index) => {
            if (item.divider) {
              return <div key={index} className="my-1 border-t border-border-default" />
            }
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (!item.disabled) {
                    onSelect(item.id)
                    setIsOpen(false)
                  }
                }}
                disabled={item.disabled}
                className={cn(
                  'w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors',
                  item.disabled && 'opacity-50 cursor-not-allowed',
                  item.danger 
                    ? 'text-accent-red hover:bg-accent-red/10' 
                    : 'text-text-primary hover:bg-bg-hover'
                )}
              >
                {item.icon && <span className="w-4 h-4 shrink-0">{item.icon}</span>}
                {item.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
