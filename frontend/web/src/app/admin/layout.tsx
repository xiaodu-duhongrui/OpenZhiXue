import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { verifyToken } from '@/lib/jwt'
import { AdminLayout } from '@/components/layout/AdminLayout'

export default async function AdminRootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get('token')?.value
    
    if (!token) {
      redirect('/admin/login')
    }
    
    const payload = await verifyToken(token)
    if (!payload) {
      redirect('/admin/login')
    }
    
    if (payload.role !== 'admin') {
      redirect(`/${payload.role}/dashboard`)
    }
    
    return <AdminLayout>{children}</AdminLayout>
  } catch {
    redirect('/admin/login')
  }
}
