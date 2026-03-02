'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  FileText,
  Plus,
  Users,
  BarChart3,
  TrendingUp,
  ArrowLeft,
  Calendar,
  Clock,
  X,
  Trash2,
  Loader2,
} from 'lucide-react'
import { teacherApi, Exam, ExamDetail, ExamQuestion, ClassInfo } from '@/lib/api-services/teacher-api'

export default function ExamManagementPage() {
  const [exams, setExams] = useState<Exam[]>([])
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null)
  const [examDetail, setExamDetail] = useState<ExamDetail | null>(null)
  const [showCreateExam, setShowCreateExam] = useState(false)
  const [creating, setCreating] = useState(false)
  const [questions, setQuestions] = useState<Omit<ExamQuestion, 'id'>[]>([])
  const [newQuestion, setNewQuestion] = useState({ type: '选择题' as const, content: '', score: '' })

  const [newExam, setNewExam] = useState({
    name: '',
    classId: '',
    date: '',
    duration: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const [examsData, classesData] = await Promise.all([
        teacherApi.getExams(),
        teacherApi.getClasses(),
      ])
      setExams(examsData.items)
      setClasses(classesData)
    } catch (err) {
      setError('加载考试列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function fetchExamDetail(examId: string) {
    try {
      setLoading(true)
      const data = await teacherApi.getExamDetail(examId)
      setExamDetail(data)
    } catch (err) {
      setError('加载考试详情失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateExam() {
    try {
      setCreating(true)
      await teacherApi.createExam({
        name: newExam.name,
        classId: newExam.classId,
        date: newExam.date,
        duration: parseInt(newExam.duration),
        questions,
      })
      setShowCreateExam(false)
      setNewExam({ name: '', classId: '', date: '', duration: '' })
      setQuestions([])
      fetchData()
    } catch (err) {
      setError('创建考试失败')
      console.error(err)
    } finally {
      setCreating(false)
    }
  }

  const handleAddQuestion = () => {
    if (newQuestion.content && newQuestion.score) {
      setQuestions([
        ...questions,
        {
          type: newQuestion.type,
          content: newQuestion.content,
          score: parseInt(newQuestion.score),
        },
      ])
      setNewQuestion({ type: '选择题', content: '', score: '' })
    }
  }

  const handleRemoveQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index))
  }

  const getTotalScore = () => {
    return questions.reduce((sum, q) => sum + q.score, 0)
  }

  if (loading && exams.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (selectedExam && examDetail) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => {
            setSelectedExam(null)
            setExamDetail(null)
          }}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{selectedExam.name}</h1>
            <p className="text-gray-500">
              {selectedExam.className} · {selectedExam.date}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">参与人数</p>
              <p className="text-2xl font-bold text-blue-600">{selectedExam.participants}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">平均分</p>
              <p className="text-2xl font-bold text-green-600">{selectedExam.avgScore}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">及格率</p>
              <p className="text-2xl font-bold text-purple-600">{selectedExam.passRate}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">考试时长</p>
              <p className="text-2xl font-bold text-orange-600">{selectedExam.duration}分钟</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-500" />
                成绩分布
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {examDetail.scoreDistribution.map((item) => (
                  <div key={item.range} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{item.range}分</span>
                      <span>
                        {item.count}人 ({item.percentage}%)
                      </span>
                    </div>
                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                题目分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>题目</TableHead>
                      <TableHead className="text-right">正确率</TableHead>
                      <TableHead className="text-right">平均得分</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {examDetail.questionAnalysis.map((q) => (
                      <TableRow key={q.id}>
                        <TableCell>{q.content}</TableCell>
                        <TableCell className="text-right">
                          <span
                            className={`font-medium ${
                              q.correctRate >= 70
                                ? 'text-green-600'
                                : q.correctRate >= 50
                                  ? 'text-orange-600'
                                  : 'text-red-600'
                            }`}
                          >
                            {q.correctRate}%
                          </span>
                        </TableCell>
                        <TableCell className="text-right">{q.avgScore}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">试卷题目</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">序号</TableHead>
                    <TableHead className="w-24">类型</TableHead>
                    <TableHead>题目内容</TableHead>
                    <TableHead className="w-24 text-right">分值</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {examDetail.questions.map((q, index) => (
                    <TableRow key={q.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            q.type === '选择题'
                              ? 'bg-blue-100 text-blue-700'
                              : q.type === '填空题'
                                ? 'bg-green-100 text-green-700'
                                : 'bg-purple-100 text-purple-700'
                          }`}
                        >
                          {q.type}
                        </span>
                      </TableCell>
                      <TableCell>{q.content}</TableCell>
                      <TableCell className="text-right font-medium">{q.score}分</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <div className="mt-4 text-right">
              <span className="text-gray-500">总分：</span>
              <span className="text-xl font-bold text-blue-600">
                {examDetail.questions.reduce((sum, q) => sum + q.score, 0)}分
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">考试管理</h1>
        <Button onClick={() => setShowCreateExam(true)}>
          <Plus className="w-4 h-4 mr-2" />
          创建新考试
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {exams.map((exam) => (
          <Card
            key={exam.id}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => {
              setSelectedExam(exam)
              fetchExamDetail(exam.id)
            }}
          >
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <FileText className="w-4 h-4 text-indigo-600" />
                </div>
                {exam.name}
                {exam.status === 'upcoming' && (
                  <span className="ml-auto text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                    即将开始
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Users className="w-4 h-4" />
                  <span>{exam.className}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="w-4 h-4" />
                  <span>{exam.date}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>{exam.duration}分钟</span>
                </div>
                {exam.status === 'completed' && (
                  <>
                    <div className="flex justify-between items-center pt-2 border-t mt-2">
                      <span className="text-sm text-gray-500">参与人数</span>
                      <span className="font-medium">{exam.participants}人</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">平均分</span>
                      <span className="font-bold text-green-600">{exam.avgScore}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">及格率</span>
                      <span className="font-medium text-purple-600">{exam.passRate}%</span>
                    </div>
                  </>
                )}
              </div>
              <Button className="w-full mt-4" variant="outline">
                {exam.status === 'completed' ? '查看详情' : '编辑考试'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {showCreateExam && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto py-8">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>创建新考试</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setShowCreateExam(false)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-6 max-h-[70vh] overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="examName">考试名称</Label>
                  <Input
                    id="examName"
                    value={newExam.name}
                    onChange={(e) => setNewExam({ ...newExam, name: e.target.value })}
                    placeholder="请输入考试名称"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="examClass">选择班级</Label>
                  <select
                    id="examClass"
                    className="w-full h-10 px-3 border rounded-md"
                    value={newExam.classId}
                    onChange={(e) => setNewExam({ ...newExam, classId: e.target.value })}
                  >
                    <option value="">请选择班级</option>
                    {classes.map((cls) => (
                      <option key={cls.id} value={cls.id}>{cls.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="examDate">考试日期</Label>
                  <Input
                    id="examDate"
                    type="date"
                    value={newExam.date}
                    onChange={(e) => setNewExam({ ...newExam, date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="examDuration">考试时长（分钟）</Label>
                  <Input
                    id="examDuration"
                    type="number"
                    value={newExam.duration}
                    onChange={(e) => setNewExam({ ...newExam, duration: e.target.value })}
                    placeholder="请输入考试时长"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>题目列表</Label>
                  <span className="text-sm text-gray-500">总分: {getTotalScore()}分</span>
                </div>
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">序号</TableHead>
                        <TableHead className="w-28">类型</TableHead>
                        <TableHead>题目内容</TableHead>
                        <TableHead className="w-20 text-right">分值</TableHead>
                        <TableHead className="w-16"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {questions.map((q, index) => (
                        <TableRow key={index}>
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>{q.type}</TableCell>
                          <TableCell className="max-w-xs truncate">{q.content}</TableCell>
                          <TableCell className="text-right">{q.score}</TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-500 hover:text-red-700"
                              onClick={() => handleRemoveQuestion(index)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg space-y-3">
                  <p className="text-sm font-medium">添加题目</p>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <select
                      className="h-10 px-3 border rounded-md"
                      value={newQuestion.type}
                      onChange={(e) => setNewQuestion({ ...newQuestion, type: e.target.value as '选择题' | '填空题' | '解答题' })}
                    >
                      <option value="选择题">选择题</option>
                      <option value="填空题">填空题</option>
                      <option value="解答题">解答题</option>
                    </select>
                    <Input
                      placeholder="题目内容"
                      value={newQuestion.content}
                      onChange={(e) => setNewQuestion({ ...newQuestion, content: e.target.value })}
                      className="md:col-span-2"
                    />
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        placeholder="分值"
                        value={newQuestion.score}
                        onChange={(e) => setNewQuestion({ ...newQuestion, score: e.target.value })}
                      />
                      <Button onClick={handleAddQuestion}>添加</Button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowCreateExam(false)}>
                  取消
                </Button>
                <Button onClick={handleCreateExam} disabled={creating}>
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  创建考试
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
