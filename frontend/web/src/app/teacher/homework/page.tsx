'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  BookOpen,
  Plus,
  CheckCircle,
  Clock,
  XCircle,
  ArrowLeft,
  FileText,
  Star,
  X,
  Loader2,
} from 'lucide-react'
import { teacherApi, Homework, Submission } from '@/lib/api-services/teacher-api'

export default function HomeworkManagementPage() {
  const [homeworks, setHomeworks] = useState<Homework[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [showCreateHomework, setShowCreateHomework] = useState(false)
  const [gradingStudent, setGradingStudent] = useState<Submission | null>(null)
  const [score, setScore] = useState('')
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const [newHomework, setNewHomework] = useState({
    title: '',
    classId: '',
    deadline: '',
    content: '',
  })

  useEffect(() => {
    fetchHomeworks()
  }, [])

  async function fetchHomeworks() {
    try {
      setLoading(true)
      const response = await teacherApi.getHomeworkList()
      setHomeworks(response.items)
    } catch (err) {
      setError('加载作业列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function fetchHomeworkDetail(homeworkId: string) {
    try {
      setLoading(true)
      const data = await teacherApi.getHomeworkDetail(homeworkId)
      setSubmissions(data.submissions)
    } catch (err) {
      setError('加载作业详情失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateHomework() {
    try {
      setSubmitting(true)
      await teacherApi.createHomework(newHomework)
      setShowCreateHomework(false)
      setNewHomework({ title: '', classId: '', deadline: '', content: '' })
      fetchHomeworks()
    } catch (err) {
      setError('创建作业失败')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleGrade() {
    if (!gradingStudent || !selectedHomework || !score) return
    try {
      setSubmitting(true)
      await teacherApi.gradeSubmission(selectedHomework.id, gradingStudent.id, {
        score: parseInt(score),
        comment,
      })
      setSubmissions(
        submissions.map((s) =>
          s.id === gradingStudent.id
            ? { ...s, status: 'graded', score: parseInt(score), comment }
            : s
        )
      )
      setGradingStudent(null)
      setScore('')
      setComment('')
    } catch (err) {
      setError('批改失败')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'submitted':
        return (
          <span className="flex items-center gap-1 text-blue-600 bg-blue-100 px-2 py-1 rounded-full text-xs">
            <Clock className="w-3 h-3" />
            待批改
          </span>
        )
      case 'graded':
        return (
          <span className="flex items-center gap-1 text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs">
            <CheckCircle className="w-3 h-3" />
            已批改
          </span>
        )
      case 'late':
        return (
          <span className="flex items-center gap-1 text-orange-600 bg-orange-100 px-2 py-1 rounded-full text-xs">
            <Clock className="w-3 h-3" />
            迟交
          </span>
        )
      case 'not_submitted':
        return (
          <span className="flex items-center gap-1 text-red-600 bg-red-100 px-2 py-1 rounded-full text-xs">
            <XCircle className="w-3 h-3" />
            未提交
          </span>
        )
      default:
        return null
    }
  }

  const groupedHomeworks = homeworks.reduce(
    (acc, hw) => {
      if (!acc[hw.className]) {
        acc[hw.className] = []
      }
      acc[hw.className].push(hw)
      return acc
    },
    {} as Record<string, Homework[]>
  )

  if (loading && !selectedHomework) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (selectedHomework) {
    const pendingSubmissions = submissions.filter((s) => s.status === 'submitted')
    const gradedSubmissions = submissions.filter((s) => s.status === 'graded' || s.status === 'late')

    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => {
            setSelectedHomework(null)
            setSubmissions([])
          }}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{selectedHomework.title}</h1>
            <p className="text-gray-500">
              {selectedHomework.className} · 截止日期: {selectedHomework.deadline}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center min-h-[200px]">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">总人数</p>
                  <p className="text-2xl font-bold">{selectedHomework.total}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">已提交</p>
                  <p className="text-2xl font-bold text-blue-600">{selectedHomework.submitted}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">已批改</p>
                  <p className="text-2xl font-bold text-green-600">{selectedHomework.graded}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">待批改</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {selectedHomework.submitted - selectedHomework.graded}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-500" />
                  待批改列表 ({pendingSubmissions.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {pendingSubmissions.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">暂无待批改作业</p>
                ) : (
                  <div className="space-y-3">
                    {pendingSubmissions.map((submission) => (
                      <div
                        key={submission.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback>{submission.studentName[0]}</AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{submission.studentName}</p>
                            <p className="text-sm text-gray-500">提交时间: {submission.submitTime}</p>
                          </div>
                        </div>
                        <Button onClick={() => setGradingStudent(submission)}>批改</Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  已批改列表 ({gradedSubmissions.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {gradedSubmissions.map((submission) => (
                    <div
                      key={submission.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback>{submission.studentName[0]}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{submission.studentName}</p>
                          <p className="text-sm text-gray-500">{submission.submitTime || '未提交'}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {getStatusBadge(submission.status)}
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="font-bold">{submission.score}</span>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setGradingStudent(submission)
                            setScore(submission.score?.toString() || '')
                            setComment(submission.comment)
                          }}
                        >
                          重新批改
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {gradingStudent && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-lg mx-4">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>批改作业 - {gradingStudent.studentName}</CardTitle>
                <Button variant="ghost" size="icon" onClick={() => setGradingStudent(null)}>
                  <X className="w-4 h-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-2">学生提交内容</p>
                  <p className="text-gray-700">
                    这里是学生提交的作业内容预览区域。实际应用中可以显示图片、文档或文本内容。
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="score">分数</Label>
                  <Input
                    id="score"
                    type="number"
                    min="0"
                    max="100"
                    value={score}
                    onChange={(e) => setScore(e.target.value)}
                    placeholder="请输入分数 (0-100)"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="comment">评语</Label>
                  <textarea
                    id="comment"
                    className="w-full h-24 p-3 border rounded-md resize-none"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="请输入评语（可选）"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setGradingStudent(null)}>
                    取消
                  </Button>
                  <Button onClick={handleGrade} disabled={submitting}>
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    确认批改
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">作业管理</h1>
        <Button onClick={() => setShowCreateHomework(true)}>
          <Plus className="w-4 h-4 mr-2" />
          发布新作业
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      {Object.entries(groupedHomeworks).map(([className, homeworks]) => (
        <div key={className} className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-700">{className}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {homeworks.map((hw) => (
              <Card
                key={hw.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => {
                  setSelectedHomework(hw)
                  fetchHomeworkDetail(hw.id)
                }}
              >
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <BookOpen className="w-4 h-4 text-purple-600" />
                    </div>
                    {hw.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">截止日期</span>
                      <span>{hw.deadline}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">提交情况</span>
                      <span>
                        {hw.submitted}/{hw.total}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">批改进度</span>
                      <span>
                        {hw.graded}/{hw.submitted}
                      </span>
                    </div>
                    <div className="mt-3">
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 rounded-full transition-all"
                          style={{ width: `${(hw.graded / hw.total) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    查看详情
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}

      {showCreateHomework && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>发布新作业</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setShowCreateHomework(false)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="hwTitle">作业标题</Label>
                <Input
                  id="hwTitle"
                  value={newHomework.title}
                  onChange={(e) => setNewHomework({ ...newHomework, title: e.target.value })}
                  placeholder="请输入作业标题"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="hwClass">选择班级</Label>
                <select
                  id="hwClass"
                  className="w-full h-10 px-3 border rounded-md"
                  value={newHomework.classId}
                  onChange={(e) => setNewHomework({ ...newHomework, classId: e.target.value })}
                >
                  <option value="">请选择班级</option>
                  <option value="1">高二3班</option>
                  <option value="2">高二4班</option>
                  <option value="3">高二5班</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="hwDeadline">截止日期</Label>
                <Input
                  id="hwDeadline"
                  type="date"
                  value={newHomework.deadline}
                  onChange={(e) => setNewHomework({ ...newHomework, deadline: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="hwContent">作业内容</Label>
                <textarea
                  id="hwContent"
                  className="w-full h-24 p-3 border rounded-md resize-none"
                  value={newHomework.content}
                  onChange={(e) => setNewHomework({ ...newHomework, content: e.target.value })}
                  placeholder="请输入作业内容和要求"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowCreateHomework(false)}>
                  取消
                </Button>
                <Button onClick={handleCreateHomework} disabled={submitting}>
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  发布作业
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
