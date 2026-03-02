'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, BarChart3, FileText, Clock, Loader2 } from 'lucide-react'
import { parentApi, ParentStats, Child } from '@/lib/api-services/parent-api'

interface RecentActivity {
  id: string
  child: string
  action: string
  time: string
}

export default function ParentDashboard() {
  const [stats, setStats] = useState<ParentStats | null>(null)
  const [children, setChildren] = useState<Child[]>([])
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const [statsData, childrenData] = await Promise.all([
        parentApi.getStats(),
        parentApi.getChildren(),
      ])
      setStats(statsData)
      setChildren(childrenData)
      const activities: RecentActivity[] = childrenData.flatMap(child => [
        { id: `${child.id}-1`, child: child.name, action: '完成作业', time: '今天' },
        { id: `${child.id}-2`, child: child.name, action: `考试成绩：${child.avgScore}分`, time: '昨天' },
      ]).slice(0, 5)
      setRecentActivities(activities)
    } catch (err) {
      setError('加载数据失败，请稍后重试')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

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

  const statsItems = stats ? [
    { title: '绑定孩子', value: stats.childrenCount, icon: Users, color: 'text-blue-600', bg: 'bg-blue-100' },
    { title: '平均成绩', value: stats.avgScore.toFixed(1), icon: BarChart3, color: 'text-green-600', bg: 'bg-green-100' },
    { title: '学习报告', value: stats.reportsCount, icon: FileText, color: 'text-orange-600', bg: 'bg-orange-100' },
    { title: '本周学习', value: `${stats.weeklyStudyHours}h`, icon: Clock, color: 'text-purple-600', bg: 'bg-purple-100' },
  ] : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">家长首页</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsItems.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="flex items-center p-6">
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">{stat.title}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">我的孩子</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {children.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无绑定的孩子</p>
              ) : (
                children.map((child) => (
                  <div
                    key={child.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{child.name}</p>
                      <p className="text-sm text-gray-500">
                        {child.grade} {child.class}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">平均分</p>
                      <p className="text-lg font-bold text-green-600">{child.avgScore}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">最近动态</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无动态</p>
              ) : (
                recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium">
                      {activity.child.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium">{activity.child}</p>
                      <p className="text-sm text-gray-500">{activity.action}</p>
                      <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
