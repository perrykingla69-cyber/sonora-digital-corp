import Sidebar from '@/components/layout/Sidebar'
import AuthGuard from '@/components/layout/AuthGuard'
import BrainWidget from '@/components/ui/BrainWidget'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 ml-0 md:ml-56 p-4 md:p-8">
          {children}
        </main>
        <BrainWidget />
      </div>
    </AuthGuard>
  )
}
