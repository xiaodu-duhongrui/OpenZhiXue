'use client'

import * as React from 'react'
import { Bell, X, Check, Info, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useNotificationStore } from '@/store'
import { cn } from '@/lib/utils'

const mockNotifications = [
  {
    id: '1',
    title: '作业提醒',
    message: '数学作业将于明天截止，请及时完成',
    type: 'warning' as const,
    read: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: '2',
    title: '成绩发布',
    message: '您的语文测试成绩已发布：92分',
    type: 'success' as const,
    read: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: '3',
    title: '系统通知',
    message: '系统将于今晚 22:00 进行维护升级',
    type: 'info' as const,
    read: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    id: '4',
    title: '考试提醒',
    message: '物理单元测试将于下周一进行',
    type: 'info' as const,
    read: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
  },
]

function getNotificationIcon(type: string) {
  switch (type) {
    case 'success':
      return <CheckCircle className="w-5 h-5 text-green-500" />
    case 'warning':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />
    case 'error':
      return <XCircle className="w-5 h-5 text-red-500" />
    default:
      return <Info className="w-5 h-5 text-blue-500" />
  }
}

function formatTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

export function NotificationDropdown() {
  const [open, setOpen] = React.useState(false)
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotificationStore()

  React.useEffect(() => {
    if (notifications.length === 0) {
      mockNotifications.forEach((n) => {
        useNotificationStore.getState().addNotification(n)
      })
    }
  }, [])

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        onClick={() => setOpen(!open)}
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </Button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <Card className="absolute right-0 top-full mt-2 w-80 z-50 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-sm font-medium">消息通知</CardTitle>
              {unreadCount > 0 && (
                <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                  全部已读
                </Button>
              )}
            </CardHeader>
            <CardContent className="p-0 max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500">暂无通知</div>
              ) : (
                <div className="divide-y">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={cn(
                        'p-3 hover:bg-gray-50 cursor-pointer transition-colors',
                        !notification.read && 'bg-blue-50/50'
                      )}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start gap-3">
                        {getNotificationIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm">{notification.title}</p>
                          <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatTime(notification.createdAt)}
                          </p>
                        </div>
                        {!notification.read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
