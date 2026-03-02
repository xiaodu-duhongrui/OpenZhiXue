'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  UserPlus, 
  UserMinus, 
  BookOpen, 
  Trophy, 
  Clock, 
  MessageSquare,
  CheckCircle,
  XCircle,
  TrendingUp,
  Calendar,
  Loader2
} from 'lucide-react'
import { parentApi, Child, ChildDetail } from '@/lib/api-services/parent-api'

export default function ChildrenPage() {
  const [children, setChildren] = useState<ChildDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [bindCode, setBindCode] = useState('')
  const [binding, setBinding] = useState(false)
  const [unbindingId, setUnbindingId] = useState<string | null>(null)

  useEffect(() => {
    fetchChildren()
  }, [])

  async function fetchChildren() {
    try {
      setLoading(true)
      const data = await parentApi.getChildren()
      const childDetails = await Promise.all(
        data.map(child => parentApi.getChildDetail(child.id))
      )
      setChildren(childDetails)
    } catch (err) {
      setError('加载孩子数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddChild() {
    if (!bindCode.trim()) return
    try {
      setBinding(true)
      await parentApi.bindChild(bindCode)
      setShowAddModal(false)
      setBindCode('')
      fetchChildren()
    } catch (err) {
      setError('绑定失败，请检查绑定码是否正确')
      console.error(err)
    } finally {
      setBinding(false)
    }
  }

  async function handleUnbindChild(childId: string) {
    if (!confirm('确定要解绑该孩子吗？')) return
    try {
      setUnbindingId(childId)
      await parentApi.unbindChild(childId)
      setChildren(children.filter(c => c.id !== childId))
    } catch (err) {
      setError('解绑失败')
      console.error(err)
    } finally {
      setUnbindingId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">孩子动态</h1>
        <Button onClick={() => setShowAddModal(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          添加孩子
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      {children.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <UserPlus className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-500 mb-4">暂无绑定的孩子</p>
            <Button onClick={() => setShowAddModal(true)}>添加孩子</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {children.map((child) => (
            <Card key={child.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Avatar className="w-16 h-16">
                      <AvatarImage src={child.avatar} />
                      <AvatarFallback className="text-xl">{child.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle>{child.name}</CardTitle>
                      <CardDescription>{child.school} · {child.grade}{child.class}</CardDescription>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleUnbindChild(child.id)}
                    disabled={unbindingId === child.id}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    {unbindingId === child.id ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-1" />
                    ) : (
                      <UserMinus className="w-4 h-4 mr-1" />
                    )}
                    解绑
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <BookOpen className="w-5 h-5 text-blue-600" />
                      <span className="text-sm text-gray-600">今日作业</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-blue-600">
                        {child.todayHomework.completed}/{child.todayHomework.total}
                      </span>
                      {child.todayHomework.completed === child.todayHomework.total && child.todayHomework.total > 0 ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <XCircle className="w-5 h-5 text-orange-500" />
                      )}
                    </div>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Trophy className="w-5 h-5 text-green-600" />
                      <span className="text-sm text-gray-600">最近考试</span>
                    </div>
                    {child.recentExams.length > 0 ? (
                      <div>
                        <span className="text-2xl font-bold text-green-600">
                          {child.recentExams[0].score}
                        </span>
                        <span className="text-sm text-gray-500 ml-1">分</span>
                        <p className="text-xs text-gray-500">{child.recentExams[0].subject}</p>
                      </div>
                    ) : (
                      <span className="text-gray-400">暂无</span>
                    )}
                  </div>

                  <div className="p-4 bg-purple-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-5 h-5 text-purple-600" />
                      <span className="text-sm text-gray-600">学习时长</span>
                    </div>
                    <div>
                      <span className="text-2xl font-bold text-purple-600">{child.studyHours.today}</span>
                      <span className="text-sm text-gray-500 ml-1">小时/今日</span>
                    </div>
                    <p className="text-xs text-gray-500">本周 {child.studyHours.week} 小时</p>
                  </div>

                  <div className="p-4 bg-orange-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-5 h-5 text-orange-600" />
                      <span className="text-sm text-gray-600">学习趋势</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-green-600 font-medium">进步中</span>
                    </div>
                    <p className="text-xs text-gray-500">较上周提升 5%</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      最近考试成绩
                    </h4>
                    <div className="space-y-2">
                      {child.recentExams.length > 0 ? (
                        child.recentExams.map((exam, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="font-medium">{exam.subject}</span>
                            <div className="text-right">
                              <span className={`text-lg font-bold ${
                                exam.score >= 90 ? 'text-green-600' : 
                                exam.score >= 60 ? 'text-blue-600' : 'text-red-600'
                              }`}>
                                {exam.score}
                              </span>
                              <span className="text-sm text-gray-500 ml-1">分</span>
                              <p className="text-xs text-gray-400">{exam.date}</p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">暂无考试记录</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" />
                      教师评语
                    </h4>
                    <div className="space-y-2">
                      {child.teacherComments.length > 0 ? (
                        child.teacherComments.map((comment, index) => (
                          <div key={index} className="p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium text-primary">{comment.teacher}</span>
                              <span className="text-xs text-gray-400">{comment.date}</span>
                            </div>
                            <p className="text-sm text-gray-600">{comment.content}</p>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">暂无评语</p>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>添加孩子</CardTitle>
              <CardDescription>请输入孩子的绑定码完成绑定</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bindCode">绑定码</Label>
                <Input
                  id="bindCode"
                  placeholder="请输入6位绑定码"
                  value={bindCode}
                  onChange={(e) => setBindCode(e.target.value)}
                  maxLength={6}
                />
              </div>
              <p className="text-sm text-gray-500">
                绑定码可从孩子的账号设置中获取，或联系班主任获取
              </p>
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => {
                    setShowAddModal(false)
                    setBindCode('')
                  }}
                >
                  取消
                </Button>
                <Button 
                  className="flex-1"
                  onClick={handleAddChild}
                  disabled={!bindCode.trim() || binding}
                >
                  {binding ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  确认绑定
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
