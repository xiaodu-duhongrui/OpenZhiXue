import { requireRole } from '@/lib/auth'
import { MainLayout } from '@/components/layout/MainLayout'

export default async function ParentLayout({
  children,
}: {
  children: React.ReactNode
}) {
  await requireRole('parent')
  return <MainLayout>{children}</MainLayout>
}
