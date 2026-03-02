import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'

export default async function Home() {
  const session = await getServerSession()
  
  if (session) {
    redirect(`/${session.user.role}/dashboard`)
  }
  
  redirect('/login')
}
