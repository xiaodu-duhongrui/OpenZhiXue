'use client'

import { useState, useEffect, useRef } from 'react'
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
import { FileUp, Save, Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { teacherApi, GradeEntry, Exam, ClassInfo } from '@/lib/api-services/teacher-api'

export default function GradeEntryPage() {
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [exams, setExams] = useState<Exam[]>([])
  const [students, setStudents] = useState<GradeEntry[]>([])
  const [selectedClass, setSelectedClass] = useState('')
  const [selectedExam, setSelectedExam] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [importedData, setImportedData] = useState<GradeEntry[] | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchInitialData()
  }, [])

  async function fetchInitialData() {
    try {
      setLoading(true)
      const [classesData] = await Promise.all([
        teacherApi.getClasses(),
      ])
      setClasses(classesData)
      const mockExams: Exam[] = [
        { id: '1', name: '期中考试', className: '', date: '', duration: 0, participants: 0, avgScore: 0, passRate: 0, status: 'completed' },
        { id: '2', name: '月考一', className: '', date: '', duration: 0, participants: 0, avgScore: 0, passRate: 0, status: 'completed' },
        { id: '3', name: '单元测试', className: '', date: '', duration: 0, participants: 0, avgScore: 0, passRate: 0, status: 'completed' },
      ]
      setExams(mockExams)
    } catch (err) {
      setError('加载数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function fetchGradeEntryData() {
    if (!selectedClass || !selectedExam) return
    try {
      setLoading(true)
      const data = await teacherApi.getGradeEntryData(selectedClass, selectedExam)
      setStudents(data.students)
    } catch (err) {
      setError('加载学生数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedClass && selectedExam) {
      fetchGradeEntryData()
    }
  }, [selectedClass, selectedExam])

  const handleScoreChange = (studentId: string, score: string) => {
    setStudents(
      students.map((s) => (s.id === studentId ? { ...s, score } : s))
    )
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        const lines = text.split('\n').filter((line) => line.trim())
        
        if (lines.length > 1) {
          const data: GradeEntry[] = []
          
          for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map((v) => v.trim())
            if (values.length >= 3) {
              data.push({
                id: i.toString(),
                studentId: values[0],
                name: values[1],
                score: values[2],
              })
            }
          }
          
          setImportedData(data)
          setShowPreview(true)
        }
      }
      reader.readAsText(file)
    }
  }

  const handleConfirmImport = () => {
    if (importedData) {
      setStudents(importedData)
      setShowPreview(false)
      setImportedData(null)
    }
  }

  async function handleSave() {
    const validScores = students.filter((s) => s.score !== '').map(s => ({
      studentId: s.id,
      score: parseFloat(s.score),
    }))
    if (validScores.length === 0) {
      setError('请至少录入一个成绩')
      return
    }
    try {
      setSaving(true)
      await teacherApi.saveGrades(selectedClass, selectedExam, validScores)
      alert('成绩保存成功！')
    } catch (err) {
      setError('保存成绩失败')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const handleExportTemplate = () => {
    const csvContent = '学号,姓名,成绩\n' + students.map((s) => `${s.studentId},${s.name},`).join('\n')
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `成绩导入模板_${selectedClass || '班级'}.csv`
    link.click()
  }

  const getStatistics = () => {
    const validScores = students
      .filter((s) => s.score !== '')
      .map((s) => parseFloat(s.score))
    
    if (validScores.length === 0) {
      return { count: 0, avg: 0, max: 0, min: 0 }
    }
    
    return {
      count: validScores.length,
      avg: (validScores.reduce((a, b) => a + b, 0) / validScores.length).toFixed(1),
      max: Math.max(...validScores),
      min: Math.min(...validScores),
    }
  }

  const stats = getStatistics()

  if (loading && classes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">成绩录入</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">选择班级和考试</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="classSelect">班级</Label>
              <select
                id="classSelect"
                className="w-full h-10 px-3 border rounded-md"
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
              >
                <option value="">请选择班级</option>
                {classes.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="examSelect">考试</Label>
              <select
                id="examSelect"
                className="w-full h-10 px-3 border rounded-md"
                value={selectedExam}
                onChange={(e) => setSelectedExam(e.target.value)}
              >
                <option value="">请选择考试</option>
                {exams.map((exam) => (
                  <option key={exam.id} value={exam.id}>
                    {exam.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>&nbsp;</Label>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleExportTemplate}>
                  <Download className="w-4 h-4 mr-2" />
                  下载模板
                </Button>
                <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                  <FileUp className="w-4 h-4 mr-2" />
                  批量导入
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={handleFileUpload}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedClass && selectedExam && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-sm text-gray-500">已录入</p>
                <p className="text-2xl font-bold text-blue-600">{stats.count}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-sm text-gray-500">平均分</p>
                <p className="text-2xl font-bold text-green-600">{stats.avg}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-sm text-gray-500">最高分</p>
                <p className="text-2xl font-bold text-purple-600">{stats.max}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-sm text-gray-500">最低分</p>
                <p className="text-2xl font-bold text-red-600">{stats.min}</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">成绩录入表格</CardTitle>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                保存成绩
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">序号</TableHead>
                        <TableHead className="w-32">学号</TableHead>
                        <TableHead>姓名</TableHead>
                        <TableHead className="w-32">成绩</TableHead>
                        <TableHead className="w-24">状态</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {students.map((student, index) => (
                        <TableRow key={student.id}>
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>{student.studentId}</TableCell>
                          <TableCell>{student.name}</TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              min="0"
                              max="100"
                              value={student.score}
                              onChange={(e) => handleScoreChange(student.id, e.target.value)}
                              placeholder="0-100"
                              className="w-24"
                            />
                          </TableCell>
                          <TableCell>
                            {student.score !== '' ? (
                              <span className="flex items-center gap-1 text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                已录入
                              </span>
                            ) : (
                              <span className="flex items-center gap-1 text-gray-400">
                                <AlertCircle className="w-4 h-4" />
                                未录入
                              </span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {showPreview && importedData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>预览导入数据</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setShowPreview(false)}>
                ×
              </Button>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto">
              <p className="text-sm text-gray-500 mb-4">
                共 {importedData.length} 条记录，请确认后导入
              </p>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>学号</TableHead>
                      <TableHead>姓名</TableHead>
                      <TableHead>成绩</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {importedData.map((student) => (
                      <TableRow key={student.id}>
                        <TableCell>{student.studentId}</TableCell>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>{student.score}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <div className="flex gap-2 justify-end mt-4">
                <Button variant="outline" onClick={() => setShowPreview(false)}>
                  取消
                </Button>
                <Button onClick={handleConfirmImport}>确认导入</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
