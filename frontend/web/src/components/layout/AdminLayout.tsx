'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore, useAppStore } from '@/store'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Home,
  Users,
  Upload,
  FileText,
  Menu,
  X,
  Bell,
  LogOut,
  Shield,
  Settings,
} from 'lucide-react'

interface NavItem {
  title: string
  href: string
  icon: React.ElementType
}

const adminNavItems: NavItem[] = [
  { title: '仪表盘', href: '/admin/dashboard', icon: Home },
  { title: '用户管理', href: '/admin/users', icon: Users },
  { title: '批量导入', href: '/admin/import', icon: Upload },
  { title: '操作日志', href: '/admin/logs', icon: FileText },
]

export function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar, isMobile, setMobile } = useAppStore()

  React.useEffect(() => {
    const handleResize = () => {
      setMobile(window.innerWidth < 768)
    }
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [setMobile])

  const handleLogout = () => {
    logout()
    window.location.href = '/admin/login'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {isMobile && !sidebarCollapsed && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full bg-slate-900 border-r border-slate-800 transition-all duration-300',
          sidebarCollapsed ? 'w-16' : 'w-64',
          isMobile && !sidebarCollapsed ? 'translate-x-0' : '',
          isMobile && sidebarCollapsed ? '-translate-x-full' : ''
        )}
      >
        <div className="flex items-center h-16 px-4 border-b border-slate-800">
          {!sidebarCollapsed && (
            <Link href="/admin/dashboard" className="flex items-center gap-2">
              <Shield className="w-8 h-8 text-blue-400" />
              <span className="font-bold text-lg text-white">管理后台</span>
            </Link>
          )}
          {sidebarCollapsed && (
            <Shield className="w-8 h-8 text-blue-400 mx-auto" />
          )}
        </div>

        <nav className="p-4 space-y-2">
          {adminNavItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-slate-800 text-slate-300',
                  sidebarCollapsed && 'justify-center'
                )}
                title={sidebarCollapsed ? item.title : undefined}
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {!sidebarCollapsed && <span>{item.title}</span>}
              </Link>
            )
          })}
        </nav>

        {!sidebarCollapsed && (
          <div className="absolute bottom-4 left-4 right-4">
            <Link
              href="/admin/settings"
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-300 transition-colors"
            >
              <Settings className="w-5 h-5" />
              <span>系统设置</span>
            </Link>
          </div>
        )}
      </aside>

      <div
        className={cn(
          'transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64',
          isMobile && 'ml-0'
        )}
      >
        <header className="sticky top-0 z-30 h-16 bg-white border-b shadow-sm">
          <div className="flex items-center justify-between h-full px-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                {sidebarCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
              </Button>
              <span className="text-sm text-gray-500">管理员控制台</span>
            </div>

            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </Button>

              <div className="flex items-center gap-2">
                <Avatar className="w-8 h-8">
                  <AvatarImage src={user?.avatar} />
                  <AvatarFallback>{user?.realName?.charAt(0) || 'A'}</AvatarFallback>
                </Avatar>
                {!sidebarCollapsed && (
                  <div className="hidden md:block">
                    <p className="text-sm font-medium">{user?.realName || '管理员'}</p>
                    <p className="text-xs text-gray-500">{user?.username}</p>
                  </div>
                )}
                <Button variant="ghost" size="icon" onClick={handleLogout}>
                  <LogOut className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
