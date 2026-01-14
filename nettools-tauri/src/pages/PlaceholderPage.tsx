import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, Alert } from '@/components/ui'
import { Construction } from 'lucide-react'

interface PlaceholderPageProps {
  title: string
  description: string
  icon?: React.ReactNode
}

export function PlaceholderPage({ title, description, icon }: PlaceholderPageProps) {
  return (
    <div className="p-6 h-full flex items-center justify-center">
      <Card variant="bordered" className="max-w-md w-full">
        <CardContent className="p-8 text-center">
          <div className="flex justify-center mb-4">
            {icon || <Construction className="w-16 h-16 text-accent-yellow" />}
          </div>
          <h2 className="text-xl font-bold text-text-primary mb-2">{title}</h2>
          <p className="text-text-secondary mb-6">{description}</p>
          <Alert variant="info">
            Dieses Tool wird in einer zukünftigen Version implementiert.
          </Alert>
        </CardContent>
      </Card>
    </div>
  )
}
