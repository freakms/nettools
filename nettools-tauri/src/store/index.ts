import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ToolId } from '@/types/tools'
import type { Toast, AppSettings } from '@/types'

interface AppState {
  // Navigation
  activeTool: ToolId
  setActiveTool: (tool: ToolId) => void
  
  // Sidebar
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  
  // Favorites
  favorites: ToolId[]
  toggleFavorite: (toolId: ToolId) => void
  
  // Enabled Tools
  enabledTools: ToolId[]
  setEnabledTools: (tools: ToolId[]) => void
  toggleTool: (toolId: ToolId) => void
  
  // Toasts
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  
  // Settings
  settings: AppSettings
  updateSettings: (settings: Partial<AppSettings>) => void
}

const defaultEnabledTools: ToolId[] = [
  'scanner',
  'portscan',
  'dns',
  'traceroute',
  'arp',
  'subnet',
  'bandwidth',
  'whois',
  'ssl',
  'mac',
  'hash',
  'password',
  'api-tester',
  'panos',
]

const defaultSettings: AppSettings = {
  theme: 'dark',
  language: 'de',
  accentColor: '#007BFF',
  enabledTools: defaultEnabledTools,
  favorites: [],
  scanDefaults: {
    aggressiveness: 'medium',
    showOnlyResponding: false,
    resultsPerPage: 100,
  },
  shortcuts: {},
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Navigation
      activeTool: 'dashboard',
      setActiveTool: (tool) => set({ activeTool: tool }),
      
      // Sidebar
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      // Favorites
      favorites: [],
      toggleFavorite: (toolId) =>
        set((state) => ({
          favorites: state.favorites.includes(toolId)
            ? state.favorites.filter((id) => id !== toolId)
            : [...state.favorites, toolId],
        })),
      
      // Enabled Tools
      enabledTools: defaultEnabledTools,
      setEnabledTools: (tools) => set({ enabledTools: tools }),
      toggleTool: (toolId) =>
        set((state) => ({
          enabledTools: state.enabledTools.includes(toolId)
            ? state.enabledTools.filter((id) => id !== toolId)
            : [...state.enabledTools, toolId],
        })),
      
      // Toasts
      toasts: [],
      addToast: (toast) =>
        set((state) => ({
          toasts: [
            ...state.toasts,
            { ...toast, id: Math.random().toString(36).substring(7) },
          ],
        })),
      removeToast: (id) =>
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        })),
      
      // Settings
      settings: defaultSettings,
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
    }),
    {
      name: 'nettools-storage',
      partialize: (state) => ({
        favorites: state.favorites,
        enabledTools: state.enabledTools,
        sidebarCollapsed: state.sidebarCollapsed,
        settings: state.settings,
      }),
    }
  )
)

// Hook for toast notifications with auto-dismiss
export function useToast() {
  const { addToast, removeToast } = useStore()
  
  const toast = {
    success: (title: string, message?: string) => {
      const id = Math.random().toString(36).substring(7)
      addToast({ type: 'success', title, message })
      setTimeout(() => removeToast(id), 5000)
    },
    error: (title: string, message?: string) => {
      const id = Math.random().toString(36).substring(7)
      addToast({ type: 'error', title, message })
      setTimeout(() => removeToast(id), 8000)
    },
    warning: (title: string, message?: string) => {
      const id = Math.random().toString(36).substring(7)
      addToast({ type: 'warning', title, message })
      setTimeout(() => removeToast(id), 6000)
    },
    info: (title: string, message?: string) => {
      const id = Math.random().toString(36).substring(7)
      addToast({ type: 'info', title, message })
      setTimeout(() => removeToast(id), 5000)
    },
  }
  
  return toast
}
