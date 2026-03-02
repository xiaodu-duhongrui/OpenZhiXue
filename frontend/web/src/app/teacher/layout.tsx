import { requireRole } from '@/lib/auth'
import { MainLayout } from '@/components/layout/MainLayout'

export default async function TeacherLayout({
  children,
}: {
  children: React.ReactNode
}) {
  await requireRole('teacher')
  return <MainLayout>{children}</MainLayout>
}
