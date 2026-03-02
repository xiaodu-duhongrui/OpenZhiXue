'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { AdminUser } from '@/store/admin'
import { adminApi, UserListParams } from '@/lib/admin-api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useToast } from '@/components/ui/use-toast'
import { Search, Plus, Edit, Trash2, Eye, ChevronLeft, ChevronRight, X, Download, Loader2 } from 'lucide-react'

const roleLabels: Record<string, string> = {
  student: '学生',
  parent: '家长',
  teacher: '教师',
  admin: '管理员',
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

export default function UsersPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  
  const [users, setUsers] = React.useState<AdminUser[]>([])
  const [loading, setLoading] = React.useState(true)
  const [selectedIds, setSelectedIds] = React.useState<string[]>([])
  const [total, setTotal] = React.useState(0)
  const [totalPages, setTotalPages] = React.useState(1)
  
  const [filters, setFilters] = React.useState({
    search: '',
    role: '',
    status: '',
    page: 1,
    pageSize: 10,
  })

  React.useEffect(() => {
    const role = searchParams.get('role')
    if (role) {
      setFilters(prev => ({ ...prev, role }))
    }
  }, [searchParams])

  const fetchUsers = React.useCallback(async () => {
    try {
      setLoading(true)
      const params: UserListParams = {
        search: filters.search || undefined,
        role: filters.role || undefined,
        status: filters.status || undefined,
        page: filters.page,
        pageSize: filters.pageSize,
      }
      const result = await adminApi.getUsers(params)
      setUsers(result.items)
      setTotal(result.total)
      setTotalPages(Math.ceil(result.total / filters.pageSize))
    } catch (err) {
      toast({ title: '加载失败', description: '获取用户列表失败', variant: 'destructive' })
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [filters, toast])

  React.useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters(prev => ({ ...prev, page: 1 }))
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除该用户吗？')) return
    
    try {
      await adminApi.deleteUser(id)
      toast({ title: '删除成功', description: '用户已删除' })
      fetchUsers()
    } catch (err) {
      toast({ title: '删除失败', description: '请稍后重试', variant: 'destructive' })
    }
  }

  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) return
    if (!confirm(`确定要删除选中的 ${selectedIds.length} 个用户吗？`)) return
    
    try {
      await adminApi.batchDeleteUsers(selectedIds)
      toast({ title: '删除成功', description: `已删除 ${selectedIds.length} 个用户` })
      setSelectedIds([])
      fetchUsers()
    } catch (err) {
      toast({ title: '删除失败', description: '请稍后重试', variant: 'destructive' })
    }
  }

  const handleExport = async () => {
    try {
      const blob = await adminApi.exportUsers({
        search: filters.search || undefined,
        role: filters.role || undefined,
        status: filters.status || undefined,
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `users_${new Date().toISOString().split('T')[0]}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      toast({ title: '导出失败', description: '请稍后重试', variant: 'destructive' })
    }
  }

  const toggleSelectAll = () => {
    if (selectedIds.length === users.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(users.map(u => u.id))
    }
  }

  const toggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id))
    } else {
      setSelectedIds([...selectedIds, id])
    }
  }

  const resetFilters = () => {
    setFilters({
      search: '',
      role: '',
      status: '',
      page: 1,
      pageSize: 10,
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">用户管理</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            导出
          </Button>
          <Link href="/admin/users/new">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              新建用户
            </Button>
          </Link>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">筛选条件</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="搜索用户名或姓名..."
                className="pl-10"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              />
            </div>
            
            <select
              className="px-3 py-2 border rounded-md text-sm"
              value={filters.role}
              onChange={(e) => setFilters({ ...filters, role: e.target.value, page: 1 })}
            >
              <option value="">全部角色</option>
              <option value="student">学生</option>
              <option value="parent">家长</option>
              <option value="teacher">教师</option>
            </select>
            
            <select
              className="px-3 py-2 border rounded-md text-sm"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
            >
              <option value="">全部状态</option>
              <option value="active">正常</option>
              <option value="inactive">未激活</option>
              <option value="suspended">已停用</option>
            </select>
            
            <Button type="submit" size="sm">
              <Search className="w-4 h-4 mr-1" />
              搜索
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={resetFilters}>
              <X className="w-4 h-4 mr-1" />
              重置
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {selectedIds.length > 0 && (
            <div className="flex items-center justify-between px-4 py-2 bg-blue-50 border-b">
              <span className="text-sm text-blue-700">
                已选择 {selectedIds.length} 项
              </span>
              <Button variant="destructive" size="sm" onClick={handleBatchDelete}>
                <Trash2 className="w-4 h-4 mr-1" />
                批量删除
              </Button>
            </div>
          )}
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              暂无数据
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === users.length && users.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded"
                    />
                  </TableHead>
                  <TableHead>用户名</TableHead>
                  <TableHead>姓名</TableHead>
                  <TableHead>角色</TableHead>
                  <TableHead>班级</TableHead>
                  <TableHead>联系方式</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="w-24">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(user.id)}
                        onChange={() => toggleSelect(user.id)}
                        className="rounded"
                      />
                    </TableCell>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.realName}</TableCell>
                    <TableCell>
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                        {roleLabels[user.role]}
                      </span>
                    </TableCell>
                    <TableCell>{user.className || '-'}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {user.email && <div>{user.email}</div>}
                        {user.phone && <div className="text-gray-500">{user.phone}</div>}
                        {!user.email && !user.phone && '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 text-xs rounded-full ${statusColors[user.status]}`}>
                        {statusLabels[user.status]}
                      </span>
                    </TableCell>
                    <TableCell className="text-gray-500 text-sm">{user.createdAt}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Link href={`/admin/users/${user.id}`}>
                          <Button variant="ghost" size="icon" title="查看">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </Link>
                        <Link href={`/admin/users/${user.id}`}>
                          <Button variant="ghost" size="icon" title="编辑">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="删除"
                          onClick={() => handleDelete(user.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t">
              <span className="text-sm text-gray-500">
                共 {total} 条记录，第 {filters.page} / {totalPages} 页
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={filters.page <= 1}
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={filters.page >= totalPages}
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
