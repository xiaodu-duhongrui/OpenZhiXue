'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BarChart3, TrendingUp, TrendingDown, Filter, Loader2 } from 'lucide-react'
import { studentApi, GradeRecord } from '@/lib/api-services/student-api'

const exams = ['全部考试', '期中考试', '月考一', '月考二']
const subjects = ['全部科目', '语文', '数学', '英语', '物理', '化学']

export default function GradePage() {
  const [grades, setGrades] = useState<GradeRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedExam, setSelectedExam] = useState('全部考试')
  const [selectedSubject, setSelectedSubject] = useState('全部科目')

  useEffect(() => {
    fetchGrades()
  }, [])

  async function fetchGrades() {
    try {
      setLoading(true)
      const response = await studentApi.getGrades()
      setGrades(response.items)
    } catch (err) {
      setError('加载成绩数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filteredGrades = grades.filter((grade) => {
    const matchesExam = selectedExam === '全部考试' || grade.examName === selectedExam
    const matchesSubject = selectedSubject === '全部科目' || grade.subject === selectedSubject
    return matchesExam && matchesSubject
  })

  const getScorePercentage = (score: number, fullScore: number) => {
    return Math.round((score / fullScore) * 100)
  }

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-500'
    if (percentage >= 80) return 'bg-blue-500'
    if (percentage >= 70) return 'bg-yellow-500'
    if (percentage >= 60) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getTrend = (subject: string) => {
    const subjectGrades = grades
      .filter((g) => g.subject === subject)
      .sort((a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime())
    if (subjectGrades.length < 2) return null
    const last = subjectGrades[subjectGrades.length - 1]
    const prev = subjectGrades[subjectGrades.length - 2]
    const lastPercent = getScorePercentage(last.score, last.fullScore)
    const prevPercent = getScorePercentage(prev.score, prev.fullScore)
    return lastPercent - prevPercent
  }

  const examList = [...new Set(grades.map((g) => g.examName))]
  const subjectList = [...new Set(grades.map((g) => g.subject))]

  const getSubjectGrades = (subject: string) => {
    return grades
      .filter((g) => g.subject === subject)
      .sort((a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime())
  }

  const getAverageScore = () => {
    if (filteredGrades.length === 0) return 0
    const totalPercent = filteredGrades.reduce((sum, g) => sum + getScorePercentage(g.score, g.fullScore), 0)
    return Math.round(totalPercent / filteredGrades.length)
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
        <h1 className="text-2xl font-bold">成绩查询</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <BarChart3 className="w-4 h-4" />
          <span>平均得分率：{getAverageScore()}%</span>
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-500">考试：</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {exams.map((exam) => (
                <Button
                  key={exam}
                  variant={selectedExam === exam ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedExam(exam)}
                >
                  {exam}
                </Button>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">科目：</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {subjects.map((subject) => (
                <Button
                  key={subject}
                  variant={selectedSubject === subject ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedSubject(subject)}
                >
                  {subject}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">成绩趋势</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {subjectList.map((subject) => {
                const subjectGrades = getSubjectGrades(subject)
                const trend = getTrend(subject)
                return (
                  <div key={subject} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{subject}</span>
                      <div className="flex items-center gap-2">
                        {trend !== null && (
                          <span className={`flex items-center text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {trend >= 0 ? (
                              <TrendingUp className="w-4 h-4 mr-1" />
                            ) : (
                              <TrendingDown className="w-4 h-4 mr-1" />
                            )}
                            {Math.abs(trend)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1 h-8">
                      {subjectGrades.map((grade, index) => {
                        const percentage = getScorePercentage(grade.score, grade.fullScore)
                        return (
                          <div
                            key={index}
                            className="flex-1 flex flex-col items-center"
                            title={`${grade.examName}: ${grade.score}/${grade.fullScore} (${percentage}%)`}
                          >
                            <div
                              className={`w-full rounded-t ${getScoreColor(percentage)}`}
                              style={{ height: `${percentage}%` }}
                            />
                            <span className="text-xs text-gray-400 mt-1 truncate w-full text-center">
                              {grade.examName.slice(0, 2)}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">科目成绩对比</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {subjectList.map((subject) => {
                const subjectGrades = getSubjectGrades(subject)
                const latestGrade = subjectGrades[subjectGrades.length - 1]
                if (!latestGrade) return null
                const percentage = getScorePercentage(latestGrade.score, latestGrade.fullScore)
                return (
                  <div key={subject} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span>{subject}</span>
                      <span className="font-medium">{latestGrade.score}/{latestGrade.fullScore}</span>
                    </div>
                    <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${getScoreColor(percentage)}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>得分率 {percentage}%</span>
                      <span>班级排名 {latestGrade.classRank}/{latestGrade.classTotal}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">详细成绩</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">考试</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">科目</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">成绩</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">得分率</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">班级排名</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">年级排名</th>
                </tr>
              </thead>
              <tbody>
                {filteredGrades.map((grade) => {
                  const percentage = getScorePercentage(grade.score, grade.fullScore)
                  return (
                    <tr key={grade.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium">{grade.examName}</p>
                          <p className="text-xs text-gray-400">{grade.examDate}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                          {grade.subject}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold">
                        {grade.score}/{grade.fullScore}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${getScoreColor(percentage)}`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="text-sm">{percentage}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={grade.classRank <= 10 ? 'text-green-600 font-medium' : ''}>
                          {grade.classRank}/{grade.classTotal}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={grade.gradeRank <= 30 ? 'text-green-600 font-medium' : ''}>
                          {grade.gradeRank}/{grade.gradeTotal}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {filteredGrades.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>暂无成绩记录</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
