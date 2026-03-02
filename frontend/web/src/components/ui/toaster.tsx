'use client'

import * as React from 'react'
import { ToastProvider, Toast, ToastTitle, ToastDescription, ToastAction, ToastViewport } from '@/components/ui/toast'
import { useToast } from '@/components/ui/use-toast'

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, action, ...props }) {
        return (
          <Toast key={id} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && <ToastDescription>{description}</ToastDescription>}
            </div>
            {action && <ToastAction altText={action.altText}>{action.label}</ToastAction>}
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
