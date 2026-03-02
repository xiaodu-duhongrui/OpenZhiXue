'use client'

import * as React from 'react'
import { Button } from '@/components/ui/button'
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
import { Upload, Download, FileSpreadsheet, CheckCircle, XCircle, AlertCircle, X } from 'lucide-react'

interface PreviewUser {
  row: number
  username: string
  realName: string
  role: string
  email?: string
  phone?: string
  className?: string
  valid: boolean
  errors?: string[]
}

export default function ImportPage() {
  const { toast } = useToast()
  const [file, setFile] = React.useState<File | null>(null)
  const [previewData, setPreviewData] = React.useState<PreviewUser[]>([])
  const [importing, setImporting] = React.useState(false)
  const [importProgress, setImportProgress] = React.useState(0)
  const [importResult, setImportResult] = React.useState<{
    total: number
    success: number
    failed: number
    errors: Array<{ row: number; message: string }>
  } | null>(null)
  const [dragActive, setDragActive] = React.useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = (selectedFile: File) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv',
    ]
    
    if (!validTypes.includes(selectedFile.type)) {
      toast({
        title: '文件格式错误',
        description: '请上传 Excel 或 CSV 文件',
        variant: 'destructive',
      })
      return
    }
    
    setFile(selectedFile)
    setImportResult(null)
    
    const mockPreview: PreviewUser[] = [
      { row: 2, username: 'newstudent1', realName: '新学生1', role: 'student', className: '高二3班', valid: true },
      { row: 3, username: 'newstudent2', realName: '新学生2', role: 'student', className: '高二3班', valid: true },
      { row: 4, username: 'newparent1', realName: '新家长1', role: 'parent', phone: '13800138000', valid: true },
      { row: 5, username: 'ab', realName: '测试', role: 'student', valid: false, errors: ['用户名至少3个字符'] },
      { row: 6, username: 'newteacher1', realName: '新教师1', role: 'teacher', email: 'teacher@example.com', valid: true },
      { row: 7, username: 'newstudent3', realName: '新学生3', role: 'student', className: '高二4班', valid: true },
    ]
    
    setPreviewData(mockPreview)
  }

  const handleDownloadTemplate = () => {
    toast({ title: '下载模板', description: '模板下载已开始' })
  }

  const handleImport = async () => {
    if (previewData.length === 0) return
    
    setImporting(true)
    setImportProgress(0)
    
    const validCount = previewData.filter((d) => d.valid).length
    
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      setImportProgress(i)
    }
    
    setImportResult({
      total: previewData.length,
      success: validCount,
      failed: previewData.length - validCount,
      errors: previewData
        .filter((d) => !d.valid)
        .flatMap((d) => (d.errors || []).map((e) => ({ row: d.row, message: e }))),
    })
    
    setImporting(false)
    toast({ title: '导入完成', description: `成功导入 ${validCount} 条记录` })
  }

  const handleReset = () => {
    setFile(null)
    setPreviewData([])
    setImportResult(null)
    setImportProgress(0)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">批量导入</h1>
        <Button variant="outline" onClick={handleDownloadTemplate}>
          <Download className="w-4 h-4 mr-2" />
          下载模板
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>上传文件</CardTitle>
        </CardHeader>
        <CardContent>
          {!file ? (
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="flex flex-col items-center">
                <div className="p-4 bg-blue-100 rounded-full mb-4">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
                <p className="text-lg font-medium mb-2">拖拽文件到此处上传</p>
                <p className="text-sm text-gray-500 mb-4">或点击下方按钮选择文件</p>
                <label>
                  <input
                    type="file"
                    className="hidden"
                    accept=".xlsx,.xls,.csv"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                  />
                  <Button variant="outline" asChild>
                    <span>选择文件</span>
                  </Button>
                </label>
                <p className="text-xs text-gray-400 mt-4">
                  支持 Excel (.xlsx, .xls) 和 CSV 格式，单次最多导入 1000 条
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-8 h-8 text-green-600" />
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={handleReset}>
                <X className="w-5 h-5" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {previewData.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>数据预览</CardTitle>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-green-600">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                有效: {previewData.filter((d) => d.valid).length}
              </span>
              <span className="text-red-600">
                <XCircle className="w-4 h-4 inline mr-1" />
                无效: {previewData.filter((d) => !d.valid).length}
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">行号</TableHead>
                  <TableHead>用户名</TableHead>
                  <TableHead>姓名</TableHead>
                  <TableHead>角色</TableHead>
                  <TableHead>班级</TableHead>
                  <TableHead>邮箱</TableHead>
                  <TableHead>手机号</TableHead>
                  <TableHead>状态</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {previewData.map((user) => (
                  <TableRow key={user.row} className={!user.valid ? 'bg-red-50' : ''}>
                    <TableCell>{user.row}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.realName}</TableCell>
                    <TableCell>{user.role}</TableCell>
                    <TableCell>{user.className || '-'}</TableCell>
                    <TableCell>{user.email || '-'}</TableCell>
                    <TableCell>{user.phone || '-'}</TableCell>
                    <TableCell>
                      {user.valid ? (
                        <span className="flex items-center text-green-600">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          有效
                        </span>
                      ) : (
                        <span className="flex items-center text-red-600">
                          <XCircle className="w-4 h-4 mr-1" />
                          {user.errors?.join(', ')}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {importing && (
        <Card>
          <CardHeader>
            <CardTitle>导入进度</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                  style={{ width: `${importProgress}%` }}
                />
              </div>
              <p className="text-center text-sm text-gray-500">
                正在导入... {importProgress}%
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {importResult && (
        <Card>
          <CardHeader>
            <CardTitle>导入结果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-6 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-3xl font-bold">{importResult.total}</p>
                <p className="text-sm text-gray-500">总记录数</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-3xl font-bold text-green-600">{importResult.success}</p>
                <p className="text-sm text-gray-500">成功导入</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-3xl font-bold text-red-600">{importResult.failed}</p>
                <p className="text-sm text-gray-500">导入失败</p>
              </div>
            </div>
            
            {importResult.errors.length > 0 && (
              <div className="space-y-2">
                <p className="font-medium text-red-600 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  错误详情
                </p>
                <div className="bg-red-50 rounded-lg p-4 max-h-40 overflow-y-auto">
                  {importResult.errors.map((error, index) => (
                    <p key={index} className="text-sm text-red-600">
                      第 {error.row} 行: {error.message}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {previewData.length > 0 && !importing && !importResult && (
        <div className="flex gap-4">
          <Button onClick={handleImport} disabled={previewData.filter((d) => d.valid).length === 0}>
            <Upload className="w-4 h-4 mr-2" />
            开始导入
          </Button>
          <Button variant="outline" onClick={handleReset}>
            取消
          </Button>
        </div>
      )}

      {importResult && (
        <Button onClick={handleReset}>
          继续导入
        </Button>
      )}
    </div>
  )
}
