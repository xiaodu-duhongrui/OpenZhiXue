import { requireRole } from '@/lib/auth'
import { MainLayout } from '@/components/layout/MainLayout'

export default async function StudentLayout({
  children,
}: {
  children: React.ReactNode
}) {
  await requireRole('student')
  return <MainLayout>{children}</MainLayout>
}
