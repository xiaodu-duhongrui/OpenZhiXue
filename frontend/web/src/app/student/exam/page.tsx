'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText, Clock, Calendar, ChevronRight, AlertCircle, CheckCircle, XCircle, Timer, Loader2 } from 'lucide-react'
import { studentApi, Exam } from '@/lib/api-services/student-api'

export default function ExamPage() {
  const [exams, setExams] = useState<Exam[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'upcoming' | 'history'>('upcoming')
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null)

  useEffect(() => {
    fetchExams()
  }, [])

  async function fetchExams() {
    try {
      setLoading(true)
      const response = await studentApi.getExams()
      setExams(response.items)
    } catch (err) {
      setError('加载考试列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const upcomingExams = exams.filter((e) => e.status === 'upcoming' || e.status === 'ongoing')
  const historyExams = exams.filter((e) => e.status === 'completed' || e.status === 'missed')

  const getStatusBadge = (status: Exam['status']) => {
    const configs = {
      upcoming: { label: '即将开始', color: 'bg-blue-100 text-blue-600', icon: Clock },
      ongoing: { label: '进行中', color: 'bg-green-100 text-green-600', icon: AlertCircle },
      completed: { label: '已完成', color: 'bg-gray-100 text-gray-600', icon: CheckCircle },
      missed: { label: '已错过', color: 'bg-red-100 text-red-600', icon: XCircle },
    }
    const config = configs[status]
    const Icon = config.icon
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    )
  }

  const getDaysUntil = (dateStr: string) => {
    const examDate = new Date(dateStr)
    const today = new Date()
    const diffTime = examDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">考试中心</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <FileText className="w-4 h-4" />
          <span>{upcomingExams.length} 场待参加考试</span>
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          variant={activeTab === 'upcoming' ? 'default' : 'outline'}
          onClick={() => setActiveTab('upcoming')}
          className="gap-2"
        >
          <Clock className="w-4 h-4" />
          即将到来 ({upcomingExams.length})
        </Button>
        <Button
          variant={activeTab === 'history' ? 'default' : 'outline'}
          onClick={() => setActiveTab('history')}
          className="gap-2"
        >
          <FileText className="w-4 h-4" />
          历史记录 ({historyExams.length})
        </Button>
      </div>

      {activeTab === 'upcoming' && (
        <div className="grid gap-4">
          {upcomingExams.map((exam) => {
            const daysUntil = getDaysUntil(exam.date)
            return (
              <Card
                key={exam.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedExam(exam)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                          {exam.subject}
                        </span>
                        {getStatusBadge(exam.status)}
                      </div>
                      <h3 className="font-semibold text-lg mb-2">{exam.title}</h3>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>{exam.date} {exam.startTime}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Timer className="w-4 h-4" />
                          <span>{exam.duration}分钟</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FileText className="w-4 h-4" />
                          <span>{exam.totalQuestions}题</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="font-medium text-gray-700">{exam.totalScore}分</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      {daysUntil > 0 && (
                        <div className="bg-orange-50 text-orange-600 px-3 py-2 rounded-lg">
                          <p className="text-2xl font-bold">{daysUntil}</p>
                          <p className="text-xs">天后开始</p>
                        </div>
                      )}
                      {daysUntil === 0 && (
                        <div className="bg-green-50 text-green-600 px-3 py-2 rounded-lg">
                          <p className="text-sm font-medium">今天</p>
                          <p className="text-xs">{exam.startTime}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
          {upcomingExams.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>暂无即将到来的考试</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">考试名称</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">科目</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">考试时间</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">成绩</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">班级排名</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">状态</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {historyExams.map((exam) => (
                    <tr key={exam.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <p className="font-medium">{exam.title}</p>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                          {exam.subject}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-500">{exam.date}</td>
                      <td className="py-3 px-4">
                        {exam.status === 'completed' ? (
                          <span className={`font-semibold ${exam.myScore! >= 60 ? 'text-green-600' : 'text-red-600'}`}>
                            {exam.myScore}/{exam.totalScore}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {exam.classRank ? (
                          <span>{exam.classRank}/{exam.classTotal}</span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4">{getStatusBadge(exam.status)}</td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedExam(exam)}
                        >
                          查看详情
                          <ChevronRight className="w-4 h-4 ml-1" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {historyExams.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>暂无历史考试记录</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedExam && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-auto">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>考试详情</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelectedExam(null)}>
                <XCircle className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                    {selectedExam.subject}
                  </span>
                  {getStatusBadge(selectedExam.status)}
                </div>
                <h2 className="text-xl font-bold">{selectedExam.title}</h2>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">考试日期</span>
                  </div>
                  <p className="font-semibold">{selectedExam.date}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">开始时间</span>
                  </div>
                  <p className="font-semibold">{selectedExam.startTime}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <Timer className="w-4 h-4" />
                    <span className="text-sm">考试时长</span>
                  </div>
                  <p className="font-semibold">{selectedExam.duration}分钟</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <FileText className="w-4 h-4" />
                    <span className="text-sm">题目数量</span>
                  </div>
                  <p className="font-semibold">{selectedExam.totalQuestions}题</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">考试说明</h4>
                <p className="text-gray-600 bg-gray-50 p-4 rounded-lg">
                  {selectedExam.description}
                </p>
              </div>

              {selectedExam.rules && selectedExam.rules.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">考试规则</h4>
                  <ul className="space-y-2">
                    {selectedExam.rules.map((rule, index) => (
                      <li key={index} className="flex items-start gap-2 text-gray-600">
                        <AlertCircle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                        <span>{rule}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedExam.status === 'completed' && selectedExam.myScore !== undefined && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">我的成绩</p>
                      <p className="text-3xl font-bold text-green-600">
                        {selectedExam.myScore}
                        <span className="text-lg text-gray-400">/{selectedExam.totalScore}</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">班级排名</p>
                      <p className="text-xl font-semibold">
                        {selectedExam.classRank}/{selectedExam.classTotal}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {selectedExam.status === 'missed' && (
                <div className="bg-red-50 p-4 rounded-lg text-center">
                  <p className="text-red-600 font-medium">您已错过此考试，无法补考</p>
                </div>
              )}

              {selectedExam.status === 'upcoming' && (
                <div className="flex gap-4">
                  <Button className="flex-1">进入考场</Button>
                  <Button variant="outline">模拟练习</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
