import React from 'react'
import { cn } from '@/lib/utils'
import { Copy, Check } from 'lucide-react'
import { copyToClipboard } from '@/lib/utils'

interface CopyButtonProps {
  text: string
  className?: string
}

export function CopyButton({ text, className }: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = async () => {
    await copyToClipboard(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className={cn(
        'p-1.5 rounded text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors',
        className
      )}
      title={copied ? 'Kopiert!' : 'Kopieren'}
    >
      {copied ? (
        <Check className="w-4 h-4 text-accent-green" />
      ) : (
        <Copy className="w-4 h-4" />
      )}
    </button>
  )
}

// Code block with copy functionality
interface CodeBlockProps {
  code: string
  language?: string
  showLineNumbers?: boolean
  className?: string
}

export function CodeBlock({ code, language, showLineNumbers = false, className }: CodeBlockProps) {
  const lines = code.split('\n')

  return (
    <div className={cn('relative group', className)}>
      <pre className="bg-bg-secondary rounded-lg p-4 overflow-x-auto">
        <code className="text-sm font-mono text-text-primary">
          {showLineNumbers ? (
            <table className="border-collapse">
              <tbody>
                {lines.map((line, i) => (
                  <tr key={i}>
                    <td className="pr-4 text-text-muted select-none text-right w-8">
                      {i + 1}
                    </td>
                    <td className="whitespace-pre">{line}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            code
          )}
        </code>
      </pre>
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <CopyButton text={code} />
      </div>
      {language && (
        <span className="absolute bottom-2 right-2 text-xs text-text-muted">
          {language}
        </span>
      )}
    </div>
  )
}
