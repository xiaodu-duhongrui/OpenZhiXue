'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Users, UserPlus, UserMinus, BarChart3, ArrowLeft, X, Loader2 } from 'lucide-react'
import { teacherApi, ClassInfo, ClassStats, Student } from '@/lib/api-services/teacher-api'

export default function ClassManagementPage() {
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedClass, setSelectedClass] = useState<ClassInfo | null>(null)
  const [classStats, setClassStats] = useState<ClassStats | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const [showAddStudent, setShowAddStudent] = useState(false)
  const [newStudentName, setNewStudentName] = useState('')
  const [newStudentId, setNewStudentId] = useState('')
  const [adding, setAdding] = useState(false)
  const [removingId, setRemovingId] = useState<string | null>(null)

  useEffect(() => {
    fetchClasses()
  }, [])

  async function fetchClasses() {
    try {
      setLoading(true)
      const data = await teacherApi.getClasses()
      setClasses(data)
    } catch (err) {
      setError('加载班级列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function fetchClassDetail(classId: string) {
    try {
      setLoading(true)
      const data = await teacherApi.getClassDetail(classId)
      setClassStats(data.stats)
      setStudents(data.students)
    } catch (err) {
      setError('加载班级详情失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddStudent() {
    if (!selectedClass || !newStudentName || !newStudentId) return
    try {
      setAdding(true)
      const newStudent = await teacherApi.addStudent(selectedClass.id, {
        name: newStudentName,
        studentId: newStudentId,
      })
      setStudents([...students, newStudent])
      setNewStudentName('')
      setNewStudentId('')
      setShowAddStudent(false)
    } catch (err) {
      setError('添加学生失败')
      console.error(err)
    } finally {
      setAdding(false)
    }
  }

  async function handleRemoveStudent(studentId: string) {
    if (!selectedClass) return
    try {
      setRemovingId(studentId)
      await teacherApi.removeStudent(selectedClass.id, studentId)
      setStudents(students.filter((s) => s.id !== studentId))
    } catch (err) {
      setError('移除学生失败')
      console.error(err)
    } finally {
      setRemovingId(null)
    }
  }

  if (loading && !selectedClass) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (selectedClass) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => {
            setSelectedClass(null)
            setClassStats(null)
            setStudents([])
          }}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{selectedClass.name}</h1>
            <p className="text-gray-500">{selectedClass.subject}</p>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center min-h-[200px]">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">学生人数</p>
                  <p className="text-2xl font-bold text-blue-600">{classStats?.totalStudents || 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">平均分</p>
                  <p className="text-2xl font-bold text-green-600">{classStats?.avgScore || 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">最高分</p>
                  <p className="text-2xl font-bold text-purple-600">{classStats?.highestScore || 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">最低分</p>
                  <p className="text-2xl font-bold text-red-600">{classStats?.lowestScore || 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">及格率</p>
                  <p className="text-2xl font-bold text-orange-600">{classStats?.passRate || 0}%</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-gray-500">优秀率</p>
                  <p className="text-2xl font-bold text-teal-600">{classStats?.excellentRate || 0}%</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg">学生列表</CardTitle>
                <Button onClick={() => setShowAddStudent(true)}>
                  <UserPlus className="w-4 h-4 mr-2" />
                  添加学生
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {students.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">暂无学生</p>
                  ) : (
                    students.map((student) => (
                      <div
                        key={student.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback>{student.name[0]}</AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-sm text-gray-500">学号: {student.studentId}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-sm text-gray-500">成绩排名</p>
                            <p className="font-bold text-blue-600">第 {student.rank} 名</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleRemoveStudent(student.id)}
                            disabled={removingId === student.id}
                          >
                            {removingId === student.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <UserMinus className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {showAddStudent && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>添加学生</CardTitle>
                <Button variant="ghost" size="icon" onClick={() => setShowAddStudent(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="studentName">学生姓名</Label>
                  <Input
                    id="studentName"
                    value={newStudentName}
                    onChange={(e) => setNewStudentName(e.target.value)}
                    placeholder="请输入学生姓名"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="studentId">学号</Label>
                  <Input
                    id="studentId"
                    value={newStudentId}
                    onChange={(e) => setNewStudentId(e.target.value)}
                    placeholder="请输入学号"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setShowAddStudent(false)}>
                    取消
                  </Button>
                  <Button onClick={handleAddStudent} disabled={adding}>
                    {adding ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    确认添加
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
        <h1 className="text-2xl font-bold">班级管理</h1>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((cls) => (
          <Card
            key={cls.id}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => {
              setSelectedClass(cls)
              fetchClassDetail(cls.id)
            }}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                {cls.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">学生人数</span>
                  <span className="font-medium">{cls.students} 人</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">任教科目</span>
                  <span className="font-medium">{cls.subject}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">班级平均分</span>
                  <div className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4 text-green-500" />
                    <span className="font-bold text-green-600">{cls.avgScore}</span>
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
  )
}
