'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BookOpen, Play, Clock, FileText, ChevronRight, X, CheckCircle, Lock, Loader2 } from 'lucide-react'
import { studentApi, Course } from '@/lib/api-services/student-api'

export default function CoursePage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)

  useEffect(() => {
    fetchCourses()
  }, [])

  async function fetchCourses() {
    try {
      setLoading(true)
      const data = await studentApi.getCourses()
      setCourses(data)
    } catch (err) {
      setError('加载课程列表失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getProgressPercentage = (course: Course) => {
    return Math.round((course.completedLessons / course.totalLessons) * 100)
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
        <h1 className="text-2xl font-bold">课程学习</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <BookOpen className="w-4 h-4" />
          <span>共 {courses.length} 门课程</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <Card
            key={course.id}
            className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => setSelectedCourse(course)}
          >
            <div className="relative h-40 bg-gray-200">
              <div
                className="w-full h-full bg-cover bg-center"
                style={{ backgroundImage: `url(${course.coverImage})` }}
              />
              <div className="absolute top-2 left-2">
                <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs font-medium">
                  {course.subject}
                </span>
              </div>
              <div className="absolute bottom-2 right-2">
                <span className="px-2 py-1 bg-black/60 text-white rounded text-xs">
                  {course.totalLessons} 课时
                </span>
              </div>
            </div>
            <CardContent className="p-4">
              <h3 className="font-semibold text-lg mb-2 line-clamp-1">{course.title}</h3>
              <p className="text-sm text-gray-500 mb-3">授课教师：{course.teacher}</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">学习进度</span>
                  <span className="font-medium">{getProgressPercentage(course)}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${getProgressPercentage(course)}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{course.completedLessons}/{course.totalLessons} 课时</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {course.duration}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedCourse && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-auto">
            <CardHeader className="flex flex-row items-center justify-between sticky top-0 bg-white z-10">
              <CardTitle>{selectedCourse.title}</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelectedCourse(null)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="relative h-48 bg-gray-200 rounded-lg overflow-hidden">
                <div
                  className="w-full h-full bg-cover bg-center"
                  style={{ backgroundImage: `url(${selectedCourse.coverImage})` }}
                />
                <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                  <Button size="lg" className="gap-2">
                    <Play className="w-5 h-5" />
                    继续学习
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-sm text-gray-500">科目</p>
                  <p className="font-semibold">{selectedCourse.subject}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-sm text-gray-500">授课教师</p>
                  <p className="font-semibold">{selectedCourse.teacher}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-sm text-gray-500">总课时</p>
                  <p className="font-semibold">{selectedCourse.totalLessons} 节</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-sm text-gray-500">总时长</p>
                  <p className="font-semibold">{selectedCourse.duration}</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">课程简介</h4>
                <p className="text-gray-600">{selectedCourse.description}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-4">课程大纲</h4>
                <div className="space-y-2">
                  {selectedCourse.outline.map((lesson) => (
                    <div
                      key={lesson.id}
                      className={`flex items-center justify-between p-3 rounded-lg border ${
                        lesson.locked
                          ? 'bg-gray-50 opacity-60 cursor-not-allowed'
                          : 'hover:bg-gray-50 cursor-pointer'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            lesson.completed
                              ? 'bg-green-100 text-green-600'
                              : lesson.locked
                              ? 'bg-gray-100 text-gray-400'
                              : 'bg-blue-100 text-blue-600'
                          }`}
                        >
                          {lesson.completed ? (
                            <CheckCircle className="w-4 h-4" />
                          ) : lesson.locked ? (
                            <Lock className="w-4 h-4" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                        </div>
                        <div>
                          <p className={`font-medium ${lesson.locked ? 'text-gray-400' : ''}`}>
                            {lesson.title}
                          </p>
                          <p className="text-xs text-gray-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {lesson.duration}
                          </p>
                        </div>
                      </div>
                      {!lesson.locked && (
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                <Button className="flex-1 gap-2">
                  <Play className="w-4 h-4" />
                  继续学习
                </Button>
                <Button variant="outline" className="gap-2">
                  <FileText className="w-4 h-4" />
                  课程资料
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
