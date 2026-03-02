'use client'

import * as React from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { AdminUser } from '@/store/admin'
import { adminApi, UpdateUserParams } from '@/lib/admin-api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { ArrowLeft, Save, User, Lock, Mail, Phone, GraduationCap, Calendar, Clock, Loader2 } from 'lucide-react'

const roleLabels: Record<string, string> = {
  student: '学生',
  parent: '家长',
  teacher: '教师',
}

const statusLabels: Record<string, string> = {
  active: '正常',
  inactive: '未激活',
  suspended: '已停用',
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  suspended: 'bg-red-100 text-red-800',
}

interface ClassInfo {
  id: string
  name: string
}

export default function UserDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  const [isEditing, setIsEditing] = React.useState(false)
  const [user, setUser] = React.useState<AdminUser | null>(null)
  const [classes, setClasses] = React.useState<ClassInfo[]>([])
  
  const [form, setForm] = React.useState({
    realName: '',
    email: '',
    phone: '',
    status: 'active' as 'active' | 'inactive' | 'suspended',
    classId: '',
    password: '',
  })

  const [errors, setErrors] = React.useState<Record<string, string>>({})

  React.useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [userData, usersData] = await Promise.all([
          adminApi.getUser(params.id as string),
          adminApi.getUsers({ role: 'teacher', pageSize: 100 }),
        ])
        setUser(userData)
        setForm({
          realName: userData.realName,
          email: userData.email || '',
          phone: userData.phone || '',
          status: userData.status,
          classId: userData.classId || '',
          password: '',
        })
        
        const classSet = new Map<string, string>()
        usersData.items.forEach(u => {
          if (u.classId && u.className) {
            classSet.set(u.classId, u.className)
          }
        })
        setClasses(Array.from(classSet.entries()).map(([id, name]) => ({ id, name })))
      } catch (err) {
        toast({ title: '加载失败', description: '获取用户信息失败', variant: 'destructive' })
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    
    if (params.id) {
      fetchData()
    }
  }, [params.id, toast])

  const validate = () => {
    const newErrors: Record<string, string> = {}
    
    if (!form.realName) {
      newErrors.realName = '请输入真实姓名'
    }
    
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = '请输入有效的邮箱地址'
    }
    
    if (form.phone && !/^1[3-9]\d{9}$/.test(form.phone)) {
      newErrors.phone = '请输入有效的手机号'
    }
    
    if (form.password && form.password.length < 6) {
      newErrors.password = '密码至少6个字符'
    }
    
    if (user?.role === 'student' && !form.classId) {
      newErrors.classId = '请选择班级'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validate()) return
    
    setSaving(true)
    try {
      const updateData: UpdateUserParams = {
        realName: form.realName,
        email: form.email || undefined,
        phone: form.phone || undefined,
        status: form.status,
        classId: user?.role === 'student' ? form.classId : undefined,
        password: form.password || undefined,
      }
      const updatedUser = await adminApi.updateUser(params.id as string, updateData)
      setUser(updatedUser)
      toast({ title: '更新成功', description: '用户信息已更新' })
      setIsEditing(false)
    } catch (err) {
      toast({ title: '更新失败', description: '请稍后重试', variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">用户不存在</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/admin/users">
              <ArrowLeft className="w-5 h-5" />
            </Link>
          </Button>
          <h1 className="text-2xl font-bold">用户详情</h1>
        </div>
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)}>
            编辑用户
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>基本信息</CardTitle>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>用户名</Label>
                    <Input value={user.username} disabled className="bg-gray-50" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="realName">真实姓名 *</Label>
                    <Input
                      id="realName"
                      placeholder="请输入真实姓名"
                      className={errors.realName ? 'border-red-500' : ''}
                      value={form.realName}
                      onChange={(e) => setForm({ ...form, realName: e.target.value })}
                    />
                    {errors.realName && (
                      <p className="text-sm text-red-500">{errors.realName}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">邮箱</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="请输入邮箱"
                        className={`pl-10 ${errors.email ? 'border-red-500' : ''}`}
                        value={form.email}
                        onChange={(e) => setForm({ ...form, email: e.target.value })}
                      />
                    </div>
                    {errors.email && (
                      <p className="text-sm text-red-500">{errors.email}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">手机号</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="phone"
                        placeholder="请输入手机号"
                        className={`pl-10 ${errors.phone ? 'border-red-500' : ''}`}
                        value={form.phone}
                        onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      />
                    </div>
                    {errors.phone && (
                      <p className="text-sm text-red-500">{errors.phone}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="status">状态</Label>
                    <select
                      id="status"
                      className="w-full px-3 py-2 border rounded-md"
                      value={form.status}
                      onChange={(e) => setForm({ ...form, status: e.target.value as 'active' | 'inactive' | 'suspended' })}
                    >
                      <option value="active">正常</option>
                      <option value="inactive">未激活</option>
                      <option value="suspended">已停用</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">重置密码</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="留空则不修改"
                        className={`pl-10 ${errors.password ? 'border-red-500' : ''}`}
                        value={form.password}
                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                      />
                    </div>
                    {errors.password && (
                      <p className="text-sm text-red-500">{errors.password}</p>
                    )}
                  </div>
                </div>

                {user.role === 'student' && (
                  <div className="space-y-2">
                    <Label htmlFor="classId">班级 *</Label>
                    <div className="relative">
                      <GraduationCap className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <select
                        id="classId"
                        className={`w-full pl-10 pr-4 py-2 border rounded-md ${errors.classId ? 'border-red-500' : ''}`}
                        value={form.classId}
                        onChange={(e) => setForm({ ...form, classId: e.target.value })}
                      >
                        <option value="">请选择班级</option>
                        {classes.map((cls) => (
                          <option key={cls.id} value={cls.id}>
                            {cls.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    {errors.classId && (
                      <p className="text-sm text-red-500">{errors.classId}</p>
                    )}
                  </div>
                )}

                <div className="flex gap-4 pt-4">
                  <Button type="submit" disabled={saving}>
                    {saving ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        保存中...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        保存
                      </>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                    取消
                  </Button>
                </div>
              </form>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">用户名</p>
                    <p className="font-medium">{user.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">真实姓名</p>
                    <p className="font-medium">{user.realName}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">角色</p>
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {roleLabels[user.role]}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">状态</p>
                    <span className={`px-2 py-1 text-xs rounded-full ${statusColors[user.status]}`}>
                      {statusLabels[user.status]}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">邮箱</p>
                    <p className="font-medium">{user.email || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">手机号</p>
                    <p className="font-medium">{user.phone || '-'}</p>
                  </div>
                </div>

                {user.role === 'student' && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">班级</p>
                    <p className="font-medium">{user.className || '-'}</p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">账户信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="w-4 h-4 text-gray-400" />
                <div>
                  <p className="text-gray-500">创建时间</p>
                  <p className="font-medium">{user.createdAt}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Clock className="w-4 h-4 text-gray-400" />
                <div>
                  <p className="text-gray-500">更新时间</p>
                  <p className="font-medium">{user.updatedAt}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">用户头像</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center mb-4">
                <User className="w-12 h-12 text-blue-600" />
              </div>
              <Button variant="outline" size="sm">
                上传头像
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
