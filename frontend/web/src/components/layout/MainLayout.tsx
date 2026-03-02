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
  BookOpen,
  FileText,
  BarChart3,
  User,
  Users,
  GraduationCap,
  ClipboardList,
  Menu,
  X,
  Bell,
  LogOut,
  ChevronDown,
} from 'lucide-react'

interface NavItem {
  title: string
  href: string
  icon: React.ElementType
}

const studentNavItems: NavItem[] = [
  { title: '首页', href: '/student/dashboard', icon: Home },
  { title: '作业', href: '/student/homework', icon: BookOpen },
  { title: '考试', href: '/student/exam', icon: FileText },
  { title: '成绩', href: '/student/grade', icon: BarChart3 },
  { title: '个人中心', href: '/student/profile', icon: User },
]

const parentNavItems: NavItem[] = [
  { title: '首页', href: '/parent/dashboard', icon: Home },
  { title: '孩子管理', href: '/parent/children', icon: Users },
  { title: '成绩查看', href: '/parent/grade', icon: BarChart3 },
  { title: '学习报告', href: '/parent/report', icon: FileText },
]

const teacherNavItems: NavItem[] = [
  { title: '首页', href: '/teacher/dashboard', icon: Home },
  { title: '作业管理', href: '/teacher/homework', icon: ClipboardList },
  { title: '考试管理', href: '/teacher/exam', icon: FileText },
  { title: '成绩管理', href: '/teacher/grade', icon: BarChart3 },
  { title: '班级管理', href: '/teacher/class', icon: GraduationCap },
]

function getNavItems(role: string): NavItem[] {
  switch (role) {
    case 'student':
      return studentNavItems
    case 'parent':
      return parentNavItems
    case 'teacher':
      return teacherNavItems
    default:
      return []
  }
}

function getRoleName(role: string): string {
  switch (role) {
    case 'student':
      return '学生端'
    case 'parent':
      return '家长端'
    case 'teacher':
      return '教师端'
    default:
      return ''
  }
}

export function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar, isMobile, setMobile } = useAppStore()
  const navItems = getNavItems(user?.role || '')

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
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile overlay */}
      {isMobile && !sidebarCollapsed && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full bg-white border-r shadow-sm transition-all duration-300',
          sidebarCollapsed ? 'w-16' : 'w-64',
          isMobile && !sidebarCollapsed ? 'translate-x-0' : '',
          isMobile && sidebarCollapsed ? '-translate-x-full' : ''
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b">
          {!sidebarCollapsed && (
            <Link href={`/${user?.role}/dashboard`} className="flex items-center gap-2">
              <GraduationCap className="w-8 h-8 text-primary" />
              <span className="font-bold text-lg">开放智学</span>
            </Link>
          )}
          {sidebarCollapsed && (
            <GraduationCap className="w-8 h-8 text-primary mx-auto" />
          )}
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-gray-100 text-gray-700',
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
      </aside>

      {/* Main content */}
      <div
        className={cn(
          'transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64',
          isMobile && 'ml-0'
        )}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b shadow-sm">
          <div className="flex items-center justify-between h-full px-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                {sidebarCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
              </Button>
              <span className="text-sm text-gray-500">{getRoleName(user?.role || '')}</span>
            </div>

            <div className="flex items-center gap-4">
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </Button>

              {/* User menu */}
              <div className="flex items-center gap-2">
                <Avatar className="w-8 h-8">
                  <AvatarImage src={user?.avatar} />
                  <AvatarFallback>{user?.realName?.charAt(0)}</AvatarFallback>
                </Avatar>
                {!sidebarCollapsed && (
                  <div className="hidden md:block">
                    <p className="text-sm font-medium">{user?.realName}</p>
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

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
