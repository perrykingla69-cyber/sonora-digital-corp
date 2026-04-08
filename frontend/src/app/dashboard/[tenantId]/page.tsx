'use client'

import { ClientDashboard } from '@/components/dashboards'
import { useParams } from 'next/navigation'

export default function ClientDashboardPage() {
  const params = useParams()
  const tenantId = params.tenantId as string

  return <ClientDashboard tenantId={tenantId} />
}
