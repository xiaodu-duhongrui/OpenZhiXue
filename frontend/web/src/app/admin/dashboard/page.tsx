'use client'

import * as React from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, GraduationCap, UserCheck, UserPlus, FileText, Upload, BarChart3, TrendingUp, Loader2 } from 'lucide-react'
import { adminApi, DashboardStats, OperationLog } from '@/lib/admin-api'

const actionColors: Record<string, string> = {
  create: 'text-green-600 bg-green-100',
  update: 'text-blue-600 bg-blue-100',
  delete: 'text-red-600 bg-red-100',
  import: 'text-purple-600 bg-purple-100',
  login: 'text-gray-600 bg-gray-100',
}

const actionLabels: Record<string, string> = {
  create_user: '创建用户',
  update_user: '更新用户',
  delete_user: '删除用户',
  import: '批量导入',
  login: '登录系统',
}

export default function AdminDashboard() {
  const [stats, setStats] = React.useState<DashboardStats | null>(null)
  const [recentLogs, setRecentLogs] = React.useState<OperationLog[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [statsData, logsData] = await Promise.all([
          adminApi.getDashboardStats(),
          adminApi.getLogs({ pageSize: 5 }),
        ])
        setStats(statsData)
        setRecentLogs(logsData.items)
      } catch (err) {
        setError('加载数据失败，请稍后重试')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-red-500">{error}</p>
      </div>
    )
  }

  const statsData = stats || { studentCount: 0, parentCount: 0, teacherCount: 0, todayNewCount: 0, activeUserCount: 0, monthNewCount: 0, pendingCount: 0 }

  const statCards = [
    { title: '学生总数', value: statsData.studentCount, icon: GraduationCap, color: 'text-blue-600', bg: 'bg-blue-100', href: '/admin/users?role=student' },
    { title: '家长总数', value: statsData.parentCount, icon: Users, color: 'text-green-600', bg: 'bg-green-100', href: '/admin/users?role=parent' },
    { title: '教师总数', value: statsData.teacherCount, icon: UserCheck, color: 'text-purple-600', bg: 'bg-purple-100', href: '/admin/users?role=teacher' },
    { title: '今日新增', value: statsData.todayNewCount, icon: UserPlus, color: 'text-orange-600', bg: 'bg-orange-100', href: '/admin/users' },
  ]

  const quickActions = [
    { title: '用户管理', description: '管理系统用户账户', icon: Users, href: '/admin/users', color: 'bg-blue-500' },
    { title: '批量导入', description: '导入用户数据', icon: Upload, href: '/admin/import', color: 'bg-green-500' },
    { title: '操作日志', description: '查看系统操作记录', icon: FileText, href: '/admin/logs', color: 'bg-purple-500' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">管理仪表盘</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <TrendingUp className="w-4 h-4" />
          <span>系统运行正常</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Link key={stat.title} href={stat.href}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="flex items-center p-6">
                <div className={`p-3 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value.toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              用户统计
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">活跃用户</span>
                <span className="font-medium">{statsData.activeUserCount.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${Math.min((statsData.activeUserCount / (statsData.studentCount + statsData.parentCount + statsData.teacherCount)) * 100, 100)}%` }} />
              </div>
              
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-500">本月新增</span>
                <span className="font-medium text-green-600">+{statsData.monthNewCount}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${Math.min((statsData.monthNewCount / statsData.activeUserCount) * 100, 100)}%` }} />
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-500">待审核账户</span>
                <span className="font-medium text-orange-600">{statsData.pendingCount}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-orange-600 h-2 rounded-full" style={{ width: `${Math.min((statsData.pendingCount / 100) * 100, 100)}%` }} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">快捷操作</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {quickActions.map((action) => (
                <Link key={action.title} href={action.href}>
                  <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <action.icon className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">{action.title}</p>
                      <p className="text-xs text-gray-500">{action.description}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">最近操作日志</CardTitle>
          <Link href="/admin/logs">
            <Button variant="ghost" size="sm">查看全部</Button>
          </Link>
        </CardHeader>
        <CardContent>
          {recentLogs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">暂无操作记录</div>
          ) : (
            <div className="space-y-3">
              {recentLogs.map((log) => (
                <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${actionColors[log.action.split('_')[0]] || 'text-gray-600 bg-gray-100'}`}>
                      {actionLabels[log.action] || log.action}
                    </span>
                    <div>
                      <p className="text-sm">
                        <span className="font-medium">{log.adminName}</span>
                        <span className="text-gray-500 mx-1">操作了</span>
                        <span className="font-medium">{log.targetName || '-'}</span>
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400">{log.createdAt}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
