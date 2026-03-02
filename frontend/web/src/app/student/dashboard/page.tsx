'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, FileText, BarChart3, Clock, Loader2 } from 'lucide-react'
import { studentApi, StudentStats, RecentHomework, RecentExam } from '@/lib/api-services/student-api'

export default function StudentDashboard() {
  const [stats, setStats] = useState<StudentStats | null>(null)
  const [recentHomework, setRecentHomework] = useState<RecentHomework[]>([])
  const [recentExams, setRecentExams] = useState<RecentExam[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [statsData, homeworkData, examsData] = await Promise.all([
          studentApi.getStats(),
          studentApi.getRecentHomework(),
          studentApi.getRecentExams(),
        ])
        setStats(statsData)
        setRecentHomework(homeworkData)
        setRecentExams(examsData)
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

  const statsItems = stats ? [
    { title: '待完成作业', value: stats.pendingHomework, icon: BookOpen, color: 'text-blue-600', bg: 'bg-blue-100' },
    { title: '待参加考试', value: stats.pendingExams, icon: FileText, color: 'text-orange-600', bg: 'bg-orange-100' },
    { title: '平均成绩', value: stats.avgScore.toFixed(1), icon: BarChart3, color: 'text-green-600', bg: 'bg-green-100' },
    { title: '学习时长', value: `${stats.studyHours}h`, icon: Clock, color: 'text-purple-600', bg: 'bg-purple-100' },
  ] : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">学生首页</h1>

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
            <CardTitle className="text-lg">最近作业</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentHomework.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无作业</p>
              ) : (
                recentHomework.map((hw) => (
                  <div
                    key={hw.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{hw.title}</p>
                      <p className="text-sm text-gray-500">{hw.subject}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">截止：{hw.deadline}</p>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          hw.status === 'completed'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-yellow-100 text-yellow-600'
                        }`}
                      >
                        {hw.status === 'completed' ? '已完成' : '待完成'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">即将到来的考试</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentExams.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无考试安排</p>
              ) : (
                recentExams.map((exam) => (
                  <div
                    key={exam.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{exam.title}</p>
                      <p className="text-sm text-gray-500">{exam.subject}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">{exam.date}</p>
                      <p className="text-xs text-gray-400">{exam.duration}</p>
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
