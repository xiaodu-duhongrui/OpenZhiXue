'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  MessageSquare, 
  Send, 
  Plus, 
  Bell, 
  Search,
  ChevronRight,
  Clock,
  X,
  Loader2
} from 'lucide-react'
import { parentApi, Conversation, Notification, Teacher } from '@/lib/api-services/parent-api'

type ViewType = 'list' | 'conversation' | 'notifications' | 'new'

export default function MessagePage() {
  const [view, setView] = useState<ViewType>('list')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null)
  const [newConversationContent, setNewConversationContent] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const [convs, notifs, teachs] = await Promise.all([
        parentApi.getConversations(),
        parentApi.getNotifications(),
        parentApi.getTeachers(),
      ])
      setConversations(convs)
      setNotifications(notifs.items)
      setTeachers(teachs)
    } catch (err) {
      setError('加载数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleSendMessage() {
    if (!newMessage.trim() || !selectedConversation) return
    try {
      setSending(true)
      await parentApi.sendMessage(selectedConversation.id, newMessage)
      const updatedConversation = {
        ...selectedConversation,
        messages: [
          ...selectedConversation.messages,
          {
            id: Date.now().toString(),
            sender: 'parent' as const,
            content: newMessage,
            time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          }
        ],
        lastMessage: newMessage,
        lastTime: '刚刚'
      }
      setSelectedConversation(updatedConversation)
      setConversations(conversations.map(c => 
        c.id === selectedConversation.id ? updatedConversation : c
      ))
      setNewMessage('')
    } catch (err) {
      setError('发送消息失败')
      console.error(err)
    } finally {
      setSending(false)
    }
  }

  async function handleStartNewConversation() {
    if (!selectedTeacher || !newConversationContent.trim()) return
    try {
      setSending(true)
      const newConv = await parentApi.startConversation(selectedTeacher.id, newConversationContent)
      setConversations([newConv, ...conversations])
      setSelectedConversation(newConv)
      setView('conversation')
      setSelectedTeacher(null)
      setNewConversationContent('')
    } catch (err) {
      setError('发送消息失败')
      console.error(err)
    } finally {
      setSending(false)
    }
  }

  async function handleMarkNotificationRead(id: string) {
    try {
      await parentApi.markNotificationRead(id)
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, read: true } : n
      ))
    } catch (err) {
      console.error(err)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'grade': return '📊'
      case 'notice': return '📢'
      case 'meeting': return '👥'
      case 'homework': return '📝'
      default: return '📌'
    }
  }

  const filteredConversations = conversations.filter(c => 
    c.teacherName.includes(searchQuery) || c.teacherSubject.includes(searchQuery)
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (view === 'conversation' && selectedConversation) {
    return (
      <div className="space-y-4 h-[calc(100vh-12rem)] flex flex-col">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setView('list')}>
            <ChevronRight className="w-5 h-5 rotate-180" />
          </Button>
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback>{selectedConversation.teacherName.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <h2 className="font-bold">{selectedConversation.teacherName}</h2>
              <p className="text-sm text-gray-500">{selectedConversation.teacherSubject}老师</p>
            </div>
          </div>
        </div>

        <Card className="flex-1 overflow-hidden flex flex-col">
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {selectedConversation.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'parent' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] p-3 rounded-lg ${
                    message.sender === 'parent'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-gray-100'
                  }`}
                >
                  <p>{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender === 'parent' ? 'text-primary-foreground/70' : 'text-gray-400'
                  }`}>
                    {message.time}
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                placeholder="输入消息..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <Button onClick={handleSendMessage} disabled={sending}>
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  if (view === 'notifications') {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setView('list')}>
            <ChevronRight className="w-5 h-5 rotate-180" />
          </Button>
          <h1 className="text-2xl font-bold">通知公告</h1>
        </div>

        <div className="space-y-4">
          {notifications.map((notification) => (
            <Card 
              key={notification.id}
              className={`cursor-pointer transition-colors ${!notification.read ? 'border-l-4 border-l-primary' : ''}`}
              onClick={() => handleMarkNotificationRead(notification.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{getNotificationIcon(notification.type)}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">{notification.title}</h3>
                      {!notification.read && (
                        <span className="w-2 h-2 bg-primary rounded-full" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{notification.content}</p>
                    <p className="text-xs text-gray-400 mt-2">{notification.date}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (view === 'new') {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setView('list')}>
            <ChevronRight className="w-5 h-5 rotate-180" />
          </Button>
          <h1 className="text-2xl font-bold">发起新对话</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">选择教师</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {teachers.map((teacher) => (
                <button
                  key={teacher.id}
                  onClick={() => setSelectedTeacher(teacher)}
                  className={`p-4 rounded-lg border text-center transition-colors ${
                    selectedTeacher?.id === teacher.id
                      ? 'border-primary bg-primary/5'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Avatar className="w-12 h-12 mx-auto mb-2">
                    <AvatarFallback>{teacher.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <p className="font-medium">{teacher.name}</p>
                  <p className="text-sm text-gray-500">{teacher.subject}</p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {selectedTeacher && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">发送消息给 {selectedTeacher.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                className="w-full h-32 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="请输入消息内容..."
                value={newConversationContent}
                onChange={(e) => setNewConversationContent(e.target.value)}
              />
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setView('list')}>
                  取消
                </Button>
                <Button 
                  onClick={handleStartNewConversation}
                  disabled={!newConversationContent.trim() || sending}
                >
                  {sending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  发送消息
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">家校沟通</h1>
        <Button onClick={() => setView('new')}>
          <Plus className="w-4 h-4 mr-2" />
          新对话
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="搜索对话..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="space-y-3">
            {filteredConversations.map((conversation) => (
              <Card
                key={conversation.id}
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => {
                  setSelectedConversation(conversation)
                  setView('conversation')
                  setConversations(conversations.map(c =>
                    c.id === conversation.id ? { ...c, unread: 0 } : c
                  ))
                }}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    <Avatar className="w-12 h-12">
                      <AvatarFallback>{conversation.teacherName.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{conversation.teacherName}</h3>
                          <span className="text-xs text-gray-500">{conversation.teacherSubject}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{conversation.lastTime}</span>
                          {conversation.unread > 0 && (
                            <span className="w-5 h-5 bg-primary text-primary-foreground text-xs rounded-full flex items-center justify-center">
                              {conversation.unread}
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 truncate mt-1">
                        {conversation.lastMessage}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <Card className="cursor-pointer hover:bg-gray-50 transition-colors" onClick={() => setView('notifications')}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  通知公告
                </CardTitle>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {notifications.slice(0, 3).map((notification) => (
                  <div
                    key={notification.id}
                    className="flex items-start gap-2 p-2 rounded-lg hover:bg-gray-100"
                  >
                    <span className="text-lg">{getNotificationIcon(notification.type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium truncate">{notification.title}</p>
                        {!notification.read && (
                          <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-xs text-gray-400">{notification.date}</p>
                    </div>
                  </div>
                ))}
              </div>
              {notifications.filter(n => !n.read).length > 0 && (
                <p className="text-sm text-primary mt-3">
                  {notifications.filter(n => !n.read).length} 条未读通知
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="w-5 h-5" />
                常用联系人
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {teachers.slice(0, 4).map((teacher) => (
                  <button
                    key={teacher.id}
                    className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    onClick={() => {
                      setSelectedTeacher(teacher)
                      setView('new')
                    }}
                  >
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="text-xs">{teacher.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="text-left">
                      <p className="text-sm font-medium">{teacher.name}</p>
                      <p className="text-xs text-gray-500">{teacher.subject}</p>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
