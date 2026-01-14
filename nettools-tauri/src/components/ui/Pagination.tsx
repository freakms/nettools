import React from 'react'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import { Button } from './Button'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showFirstLast?: boolean
  className?: string
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  showFirstLast = true,
  className,
}: PaginationProps) {
  if (totalPages <= 1) return null

  const canGoPrevious = currentPage > 1
  const canGoNext = currentPage < totalPages

  return (
    <div className={cn('flex items-center justify-center gap-1', className)}>
      {showFirstLast && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(1)}
          disabled={!canGoPrevious}
          icon={<ChevronsLeft className="w-4 h-4" />}
        />
      )}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!canGoPrevious}
        icon={<ChevronLeft className="w-4 h-4" />}
      />
      
      <div className="flex items-center gap-1 px-2">
        <span className="text-sm text-text-primary font-medium">{currentPage}</span>
        <span className="text-sm text-text-muted">/</span>
        <span className="text-sm text-text-secondary">{totalPages}</span>
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!canGoNext}
        icon={<ChevronRight className="w-4 h-4" />}
      />
      {showFirstLast && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(totalPages)}
          disabled={!canGoNext}
          icon={<ChevronsRight className="w-4 h-4" />}
        />
      )}
    </div>
  )
}
