'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, BookOpen, FileText, BarChart3, Loader2 } from 'lucide-react'
import { teacherApi, TeacherStats, ClassInfo } from '@/lib/api-services/teacher-api'

interface PendingTask {
  id: string
  type: 'homework' | 'exam'
  title: string
  count: number
  deadline: string
}

export default function TeacherDashboard() {
  const [stats, setStats] = useState<TeacherStats | null>(null)
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [pendingTasks, setPendingTasks] = useState<PendingTask[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const [statsData, classesData] = await Promise.all([
        teacherApi.getStats(),
        teacherApi.getClasses(),
      ])
      setStats(statsData)
      setClasses(classesData)
      const tasks: PendingTask[] = []
      classesData.forEach(cls => {
        tasks.push({
          id: `${cls.id}-homework`,
          type: 'homework',
          title: `${cls.name}作业`,
          count: Math.floor(Math.random() * 20) + 5,
          deadline: '今天',
        })
      })
      setPendingTasks(tasks.slice(0, 3))
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
    { title: '管理班级', value: stats.classCount, icon: Users, color: 'text-blue-600', bg: 'bg-blue-100' },
    { title: '待批作业', value: stats.pendingHomework, icon: BookOpen, color: 'text-orange-600', bg: 'bg-orange-100' },
    { title: '待阅试卷', value: stats.pendingExams, icon: FileText, color: 'text-purple-600', bg: 'bg-purple-100' },
    { title: '班级平均分', value: stats.avgScore.toFixed(1), icon: BarChart3, color: 'text-green-600', bg: 'bg-green-100' },
  ] : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">教师首页</h1>

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
            <CardTitle className="text-lg">我的班级</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {classes.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无管理的班级</p>
              ) : (
                classes.map((cls) => (
                  <div
                    key={cls.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{cls.name}</p>
                      <p className="text-sm text-gray-500">{cls.students} 名学生</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">平均分</p>
                      <p className="text-lg font-bold text-green-600">{cls.avgScore}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">待处理任务</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingTasks.length === 0 ? (
                <p className="text-center text-gray-500 py-4">暂无待处理任务</p>
              ) : (
                pendingTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          task.type === 'homework' ? 'bg-orange-500' : 'bg-purple-500'
                        }`}
                      />
                      <div>
                        <p className="font-medium">{task.title}</p>
                        <p className="text-sm text-gray-500">{task.count} 份待处理</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-400">{task.deadline}</span>
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
