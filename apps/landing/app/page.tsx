'use client'

import { useEffect } from 'react'
import { Navbar } from '@/components/Navbar'
import { Hero } from '@/components/Hero'
import { VisionStatement } from '@/components/VisionStatement'
import { CasosDeUso } from '@/components/CasosDeUso'
import { Pilares } from '@/components/Pilares'
import { Stats } from '@/components/Stats'
import { DemoChat } from '@/components/DemoChat'
import { Testimonios } from '@/components/Testimonios'
import { Footer } from '@/components/Footer'
import { refreshScrollTriggers } from '@/lib/animations'

export default function Home() {
  useEffect(() => {
    // Refresh scroll triggers on mount
    const timeout = setTimeout(() => {
      refreshScrollTriggers()
    }, 100)

    // Refresh on window resize
    const handleResize = () => {
      refreshScrollTriggers()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      clearTimeout(timeout)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <main className="w-full overflow-hidden">
      <Navbar />
      <Hero />
      <VisionStatement />
      <CasosDeUso />
      <Pilares />
      <Stats />
      <DemoChat />
      <Testimonios />
      <Footer />
    </main>
  )
}
