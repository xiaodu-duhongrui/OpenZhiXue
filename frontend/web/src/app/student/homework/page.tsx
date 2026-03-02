'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { BookOpen, Calendar, Filter, Search, X, Download, Upload, FileText, Clock, Loader2 } from 'lucide-react'
import { studentApi, Homework } from '@/lib/api-services/student-api'

const subjects = ['全部', '数学', '语文', '英语', '物理', '化学', '历史']
const statuses = [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待完成' },
  { value: 'completed', label: '已完成' },
  { value: 'expired', label: '已过期' },
]

export default function HomeworkPage() {
  const [homework, setHomework] = useState<Homework[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedSubject, setSelectedSubject] = useState('全部')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null)
  const [comment, setComment] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchHomework()
  }, [])

  async function fetchHomework() {
    try {
      setLoading(true)
      const response = await studentApi.getHomeworkList()
      setHomework(response.items)
    } catch (err) {
      setError('加载作业列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmitHomework() {
    if (!selectedHomework) return
    try {
      setSubmitting(true)
      await studentApi.submitHomework({
        homeworkId: selectedHomework.id,
        files,
        comment,
      })
      setSelectedHomework(null)
      setComment('')
      setFiles([])
      fetchHomework()
    } catch (err) {
      setError('提交作业失败')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const filteredHomework = homework.filter((hw) => {
    const matchesSubject = selectedSubject === '全部' || hw.subject === selectedSubject
    const matchesStatus = selectedStatus === 'all' || hw.status === selectedStatus
    const matchesSearch = hw.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      hw.subject.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSubject && matchesStatus && matchesSearch
  })

  const getStatusBadge = (status: Homework['status']) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-600',
      completed: 'bg-green-100 text-green-600',
      expired: 'bg-red-100 text-red-600',
    }
    const labels = {
      pending: '待完成',
      completed: '已完成',
      expired: '已过期',
    }
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    )
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
        <h1 className="text-2xl font-bold">作业列表</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <BookOpen className="w-4 h-4" />
          <span>共 {filteredHomework.length} 项作业</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="搜索作业..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <Filter className="w-4 h-4 text-gray-400 self-center mr-2" />
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
          <div className="flex gap-2 mt-4">
            {statuses.map((status) => (
              <Button
                key={status.value}
                variant={selectedStatus === status.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedStatus(status.value)}
              >
                {status.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {filteredHomework.map((hw) => (
          <Card
            key={hw.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => setSelectedHomework(hw)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                      {hw.subject}
                    </span>
                    {getStatusBadge(hw.status)}
                  </div>
                  <h3 className="font-semibold text-lg mb-1">{hw.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>截止：{hw.deadline}</span>
                    </div>
                    {hw.attachments.length > 0 && (
                      <div className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        <span>{hw.attachments.length} 个附件</span>
                      </div>
                    )}
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  查看详情
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredHomework.length === 0 && (
          <Card>
            <CardContent className="p-8 text-center text-gray-500">
              <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>暂无符合条件的作业</p>
            </CardContent>
          </Card>
        )}
      </div>

      {selectedHomework && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-auto">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>作业详情</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelectedHomework(null)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                    {selectedHomework.subject}
                  </span>
                  {getStatusBadge(selectedHomework.status)}
                </div>
                <h2 className="text-xl font-bold">{selectedHomework.title}</h2>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>截止时间：{selectedHomework.deadline}</span>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">题目要求</h4>
                <p className="text-gray-600 bg-gray-50 p-4 rounded-lg">
                  {selectedHomework.description}
                </p>
              </div>

              {selectedHomework.attachments.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">附件下载</h4>
                  <div className="space-y-2">
                    {selectedHomework.attachments.map((attachment, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <span>{attachment.name}</span>
                        </div>
                        <Button variant="outline" size="sm" asChild>
                          <a href={attachment.url} download>
                            <Download className="w-4 h-4 mr-1" />
                            下载
                          </a>
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedHomework.status !== 'completed' && selectedHomework.status !== 'expired' && (
                <div>
                  <h4 className="font-semibold mb-2">提交作业</h4>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="file-upload">上传文件</Label>
                      <div className="mt-2 border-2 border-dashed border-gray-200 rounded-lg p-6 text-center">
                        <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                        <p className="text-sm text-gray-500">点击或拖拽文件到此处上传</p>
                        <Input
                          ref={fileInputRef}
                          id="file-upload"
                          type="file"
                          multiple
                          className="hidden"
                          onChange={(e) => {
                            const fileList = e.target.files
                            if (fileList) {
                              setFiles(Array.from(fileList))
                            }
                          }}
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-2"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          选择文件
                        </Button>
                        {files.length > 0 && (
                          <div className="mt-2 text-sm text-gray-600">
                            已选择 {files.length} 个文件
                          </div>
                        )}
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="comment">备注说明</Label>
                      <Input
                        id="comment"
                        placeholder="输入备注说明（可选）"
                        className="mt-2"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                      />
                    </div>
                    <Button
                      className="w-full"
                      onClick={handleSubmitHomework}
                      disabled={submitting}
                    >
                      {submitting ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : null}
                      提交作业
                    </Button>
                  </div>
                </div>
              )}

              {selectedHomework.status === 'completed' && (
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-green-600 font-medium">此作业已完成提交</p>
                </div>
              )}

              {selectedHomework.status === 'expired' && (
                <div className="bg-red-50 p-4 rounded-lg text-center">
                  <p className="text-red-600 font-medium">此作业已过期，无法提交</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
