'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { GraduationCap, User, Lock, Mail, Phone, Eye, EyeOff } from 'lucide-react'

type TabType = 'login' | 'register'

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { login } = useAuthStore()
  const [activeTab, setActiveTab] = React.useState<TabType>('login')
  const [showPassword, setShowPassword] = React.useState(false)
  const [loading, setLoading] = React.useState(false)

  const [loginForm, setLoginForm] = React.useState({
    username: '',
    password: '',
  })

  const [registerForm, setRegisterForm] = React.useState({
    username: '',
    password: '',
    confirmPassword: '',
    realName: '',
    email: '',
    phone: '',
    role: 'student' as 'student' | 'parent' | 'teacher',
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!loginForm.username || !loginForm.password) {
      toast({ title: '错误', description: '请输入用户名和密码', variant: 'destructive' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      })

      const data = await response.json()

      if (response.ok) {
        login(data.user, data.token)
        toast({ title: '登录成功', description: '欢迎回来！' })
        router.push(`/${data.user.role}/dashboard`)
      } else {
        toast({ title: '登录失败', description: data.message || '用户名或密码错误', variant: 'destructive' })
      }
    } catch {
      toast({ title: '登录失败', description: '网络错误，请稍后重试', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!registerForm.username || !registerForm.password || !registerForm.realName) {
      toast({ title: '错误', description: '请填写必填信息', variant: 'destructive' })
      return
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      toast({ title: '错误', description: '两次输入的密码不一致', variant: 'destructive' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm),
      })

      const data = await response.json()

      if (response.ok) {
        toast({ title: '注册成功', description: '请登录您的账号' })
        setActiveTab('login')
        setLoginForm({ username: registerForm.username, password: '' })
      } else {
        toast({ title: '注册失败', description: data.message || '注册失败，请稍后重试', variant: 'destructive' })
      }
    } catch {
      toast({ title: '注册失败', description: '网络错误，请稍后重试', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-primary/10 rounded-full">
              <GraduationCap className="w-12 h-12 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl">开放智学</CardTitle>
          <CardDescription>智慧教育管理平台</CardDescription>
        </CardHeader>

        <CardContent>
          {/* Tab buttons */}
          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'login'
                  ? 'bg-white text-primary shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('login')}
            >
              登录
            </button>
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'register'
                  ? 'bg-white text-primary shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('register')}
            >
              注册
            </button>
          </div>

          {/* Login form */}
          {activeTab === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-username">用户名</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="login-username"
                    placeholder="请输入用户名"
                    className="pl-10"
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="login-password">密码</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="请输入密码"
                    className="pl-10 pr-10"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? '登录中...' : '登录'}
              </Button>
            </form>
          )}

          {/* Register form */}
          {activeTab === 'register' && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-username">用户名 *</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-username"
                    placeholder="请输入用户名"
                    className="pl-10"
                    value={registerForm.username}
                    onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-realName">真实姓名 *</Label>
                <Input
                  id="register-realName"
                  placeholder="请输入真实姓名"
                  value={registerForm.realName}
                  onChange={(e) => setRegisterForm({ ...registerForm, realName: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-password">密码 *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="请输入密码"
                    className="pl-10"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-confirmPassword">确认密码 *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-confirmPassword"
                    type="password"
                    placeholder="请再次输入密码"
                    className="pl-10"
                    value={registerForm.confirmPassword}
                    onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="register-email">邮箱</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="邮箱"
                      className="pl-10"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="register-phone">手机号</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="register-phone"
                      placeholder="手机号"
                      className="pl-10"
                      value={registerForm.phone}
                      onChange={(e) => setRegisterForm({ ...registerForm, phone: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>角色</Label>
                <div className="flex gap-4">
                  {[
                    { value: 'student', label: '学生' },
                    { value: 'parent', label: '家长' },
                    { value: 'teacher', label: '教师' },
                  ].map((role) => (
                    <label
                      key={role.value}
                      className={`flex-1 text-center py-2 px-4 rounded-lg border cursor-pointer transition-colors ${
                        registerForm.role === role.value
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="role"
                        value={role.value}
                        checked={registerForm.role === role.value}
                        onChange={(e) =>
                          setRegisterForm({
                            ...registerForm,
                            role: e.target.value as 'student' | 'parent' | 'teacher',
                          })
                        }
                        className="sr-only"
                      />
                      {role.label}
                    </label>
                  ))}
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? '注册中...' : '注册'}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
