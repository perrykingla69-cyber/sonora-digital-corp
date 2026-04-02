import SovereignShell from '@/components/layout/SovereignShell'
import AuthGuard from '@/components/layout/AuthGuard'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <SovereignShell>
        {children}
      </SovereignShell>
    </AuthGuard>
  )
}
