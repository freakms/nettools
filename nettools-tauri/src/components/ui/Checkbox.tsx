import React from 'react'
import { cn } from '@/lib/utils'

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, ...props }, ref) => {
    const id = props.id || props.name || Math.random().toString(36).substring(7)
    
    return (
      <div className="flex items-center gap-2">
        <div className="relative">
          <input
            ref={ref}
            id={id}
            type="checkbox"
            className={cn(
              'peer h-4 w-4 shrink-0 rounded border border-border-default bg-bg-tertiary',
              'appearance-none cursor-pointer',
              'transition-colors duration-200',
              'checked:bg-accent-blue checked:border-accent-blue',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              className
            )}
            {...props}
          />
          <svg
            className="absolute top-0 left-0 h-4 w-4 text-white pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M13 4L6 11L3 8"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        {label && (
          <label 
            htmlFor={id}
            className="text-sm text-text-primary cursor-pointer select-none"
          >
            {label}
          </label>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'

export { Checkbox }
