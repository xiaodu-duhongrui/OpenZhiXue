'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { adminApi, CreateUserParams } from '@/lib/admin-api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { ArrowLeft, Save, User, Lock, Mail, Phone, GraduationCap, Loader2 } from 'lucide-react'

const roleLabels: Record<string, string> = {
  student: '学生',
  parent: '家长',
  teacher: '教师',
}

interface ClassInfo {
  id: string
  name: string
}

export default function NewUserPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [loading, setLoading] = React.useState(false)
  const [classes, setClasses] = React.useState<ClassInfo[]>([])
  
  const [form, setForm] = React.useState({
    username: '',
    password: '',
    confirmPassword: '',
    realName: '',
    role: 'student' as 'student' | 'parent' | 'teacher',
    email: '',
    phone: '',
    classId: '',
  })

  const [errors, setErrors] = React.useState<Record<string, string>>({})

  React.useEffect(() => {
    async function fetchClasses() {
      try {
        const result = await adminApi.getUsers({ role: 'teacher', pageSize: 100 })
        const classSet = new Map<string, string>()
        result.items.forEach(user => {
          if (user.classId && user.className) {
            classSet.set(user.classId, user.className)
          }
        })
        setClasses(Array.from(classSet.entries()).map(([id, name]) => ({ id, name })))
      } catch (err) {
        console.error('Failed to fetch classes:', err)
      }
    }
    fetchClasses()
  }, [])

  const validate = () => {
    const newErrors: Record<string, string> = {}
    
    if (!form.username) {
      newErrors.username = '请输入用户名'
    } else if (form.username.length < 3) {
      newErrors.username = '用户名至少3个字符'
    }
    
    if (!form.password) {
      newErrors.password = '请输入密码'
    } else if (form.password.length < 6) {
      newErrors.password = '密码至少6个字符'
    }
    
    if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致'
    }
    
    if (!form.realName) {
      newErrors.realName = '请输入真实姓名'
    }
    
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = '请输入有效的邮箱地址'
    }
    
    if (form.phone && !/^1[3-9]\d{9}$/.test(form.phone)) {
      newErrors.phone = '请输入有效的手机号'
    }
    
    if (form.role === 'student' && !form.classId) {
      newErrors.classId = '请选择班级'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validate()) return
    
    setLoading(true)
    try {
      const params: CreateUserParams = {
        username: form.username,
        password: form.password,
        realName: form.realName,
        role: form.role,
        email: form.email || undefined,
        phone: form.phone || undefined,
        classId: form.role === 'student' ? form.classId : undefined,
      }
      await adminApi.createUser(params)
      toast({ title: '创建成功', description: '用户已创建' })
      router.push('/admin/users')
    } catch (err) {
      toast({ title: '创建失败', description: '请稍后重试', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h1 className="text-2xl font-bold">新建用户</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>用户信息</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">用户名 *</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="username"
                    placeholder="请输入用户名"
                    className={`pl-10 ${errors.username ? 'border-red-500' : ''}`}
                    value={form.username}
                    onChange={(e) => setForm({ ...form, username: e.target.value })}
                  />
                </div>
                {errors.username && (
                  <p className="text-sm text-red-500">{errors.username}</p>
                )}
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
                <Label htmlFor="password">密码 *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="请输入密码"
                    className={`pl-10 ${errors.password ? 'border-red-500' : ''}`}
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                  />
                </div>
                {errors.password && (
                  <p className="text-sm text-red-500">{errors.password}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">确认密码 *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="请再次输入密码"
                    className={`pl-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="text-sm text-red-500">{errors.confirmPassword}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>角色 *</Label>
              <div className="flex gap-4">
                {Object.entries(roleLabels).map(([value, label]) => (
                  <label
                    key={value}
                    className={`flex-1 text-center py-2 px-4 rounded-lg border cursor-pointer transition-colors ${
                      form.role === value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={value}
                      checked={form.role === value}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          role: e.target.value as 'student' | 'parent' | 'teacher',
                          classId: e.target.value !== 'student' ? '' : form.classId,
                        })
                      }
                      className="sr-only"
                    />
                    {label}
                  </label>
                ))}
              </div>
            </div>

            {form.role === 'student' && (
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

            <div className="flex gap-4 pt-4">
              <Button type="submit" disabled={loading}>
                {loading ? (
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
              <Button type="button" variant="outline" onClick={() => router.back()}>
                取消
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
