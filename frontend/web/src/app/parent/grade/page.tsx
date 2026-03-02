'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Award,
  ChevronDown,
  Users,
  Target,
  Loader2
} from 'lucide-react'
import { parentApi, Child, ChildGradeData } from '@/lib/api-services/parent-api'

export default function GradePage() {
  const [childrenList, setChildrenList] = useState<Child[]>([])
  const [gradeDataMap, setGradeDataMap] = useState<Record<string, ChildGradeData>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null)
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const children = await parentApi.getChildren()
      setChildrenList(children)
      if (children.length > 0) {
        setSelectedChildId(children[0].id)
        const gradeDataPromises = children.map(child => 
          parentApi.getChildGrades(child.id).then(data => ({ id: child.id, data }))
        )
        const gradeDataResults = await Promise.all(gradeDataPromises)
        const gradeMap: Record<string, ChildGradeData> = {}
        gradeDataResults.forEach(({ id, data }) => {
          gradeMap[id] = data
        })
        setGradeDataMap(gradeMap)
      }
    } catch (err) {
      setError('加载数据失败')
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

  if (!selectedChildId || childrenList.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">成绩查看</h1>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-gray-500">请先绑定孩子</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const selectedChild = childrenList.find(c => c.id === selectedChildId)!
  const data = gradeDataMap[selectedChildId]

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 60) return 'text-orange-600'
    return 'text-red-600'
  }

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-500" />
    return <span className="w-4 h-4 text-gray-400 text-xs flex items-center">—</span>
  }

  const maxRank = data ? Math.max(...data.rankHistory.map(h => h.rank)) : 1

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">成绩查看</h1>
        
        <div className="relative">
          <Button
            variant="outline"
            onClick={() => setShowDropdown(!showDropdown)}
            className="min-w-[200px] justify-between"
          >
            <div className="flex items-center gap-2">
              <Avatar className="w-6 h-6">
                <AvatarFallback className="text-xs">{selectedChild.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <span>{selectedChild.name}</span>
            </div>
            <ChevronDown className="w-4 h-4" />
          </Button>
          
          {showDropdown && (
            <div className="absolute top-full mt-1 w-full bg-white border rounded-lg shadow-lg z-10">
              {childrenList.map((child) => (
                <button
                  key={child.id}
                  onClick={() => {
                    setSelectedChildId(child.id)
                    setShowDropdown(false)
                  }}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2 first:rounded-t-lg last:rounded-b-lg ${
                    child.id === selectedChildId ? 'bg-primary/5' : ''
                  }`}
                >
                  <Avatar className="w-6 h-6">
                    <AvatarFallback className="text-xs">{child.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{child.name}</p>
                    <p className="text-xs text-gray-500">{child.grade}{child.class}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">平均分</p>
                <p className={`text-3xl font-bold ${getScoreColor(data.overview.avgScore)}`}>
                  {data.overview.avgScore}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              {getTrendIcon(data.overview.trend)}
              <span className="text-sm text-gray-500">
                {data.overview.trend === 'up' ? '较上次进步' : data.overview.trend === 'down' ? '较上次退步' : '保持稳定'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">年级排名</p>
                <p className="text-3xl font-bold text-primary">
                  {data.overview.rank}
                  <span className="text-sm font-normal text-gray-400">/{data.overview.totalStudents}</span>
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Award className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-500">
                前 {((data.overview.rank / data.overview.totalStudents) * 100).toFixed(1)}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">最佳科目</p>
                <p className="text-3xl font-bold text-green-600">
                  {data.subjects.reduce((best, curr) => curr.score > best.score ? curr : best).name}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <Target className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              得分 {data.subjects.reduce((best, curr) => curr.score > best.score ? curr : best).score} 分
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">各科成绩</CardTitle>
            <CardDescription>点击查看详细对比</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.subjects.map((subject) => (
                <div key={subject.name} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{subject.name}</span>
                    <div className="flex items-center gap-2">
                      {getTrendIcon(subject.trend)}
                      <span className={`text-lg font-bold ${getScoreColor(subject.score)}`}>
                        {subject.score}
                      </span>
                    </div>
                  </div>
                  <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="absolute h-full bg-primary rounded-full"
                      style={{ width: `${subject.score}%` }}
                    />
                    <div 
                      className="absolute h-full bg-gray-400 rounded-full opacity-50"
                      style={{ width: `${subject.classAvg}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1 text-xs text-gray-500">
                    <span>班级平均: {subject.classAvg}</span>
                    <span>排名: 第{subject.rank}名</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">排名趋势</CardTitle>
            <CardDescription>近期考试排名变化</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-end justify-between h-40 px-4">
                {data.rankHistory.map((item, index) => (
                  <div key={item.exam} className="flex flex-col items-center gap-2">
                    <div 
                      className="w-12 bg-primary/20 rounded-t relative"
                      style={{ 
                        height: `${(item.rank / maxRank) * 100}%`,
                        backgroundColor: index === data.rankHistory.length - 1 ? 'hsl(var(--primary))' : 'hsl(var(--primary) / 0.3)'
                      }}
                    >
                      <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-sm font-bold">
                        {item.rank}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 whitespace-nowrap">{item.exam}</span>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-500">进步科目</p>
                  <p className="text-xl font-bold text-green-600">
                    {data.subjects.filter(s => s.trend === 'up').length}
                  </p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-sm text-gray-500">需关注科目</p>
                  <p className="text-xl font-bold text-orange-600">
                    {data.subjects.filter(s => s.trend === 'down').length}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">成绩对比分析</CardTitle>
          <CardDescription>与班级平均分对比</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">科目</th>
                  <th className="text-center py-3 px-4">学生分数</th>
                  <th className="text-center py-3 px-4">班级平均</th>
                  <th className="text-center py-3 px-4">差距</th>
                  <th className="text-center py-3 px-4">年级排名</th>
                  <th className="text-center py-3 px-4">趋势</th>
                </tr>
              </thead>
              <tbody>
                {data.subjects.map((subject) => {
                  const diff = subject.score - subject.classAvg
                  return (
                    <tr key={subject.name} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{subject.name}</td>
                      <td className="text-center py-3 px-4">
                        <span className={`font-bold ${getScoreColor(subject.score)}`}>
                          {subject.score}
                        </span>
                      </td>
                      <td className="text-center py-3 px-4 text-gray-500">{subject.classAvg}</td>
                      <td className="text-center py-3 px-4">
                        <span className={diff >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {diff >= 0 ? '+' : ''}{diff}
                        </span>
                      </td>
                      <td className="text-center py-3 px-4">第 {subject.rank} 名</td>
                      <td className="text-center py-3 px-4">
                        {getTrendIcon(subject.trend)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
