'use client'

import type { Metadata } from 'next'
import Link from 'next/link'
import {
  Music, BarChart3, Share2, Radio, TrendingUp,
  CheckCircle2, Zap, Globe
} from 'lucide-react'
import { Navigation } from '@/components/landing/Navigation'
import { Hero } from '@/components/landing/Hero'
import { Features } from '@/components/landing/Features'
import { CaseStudy } from '@/components/landing/CaseStudy'
import { Footer } from '@/components/landing/Footer'

const artistaFeatures = [
  {
    icon: Music,
    title: 'Gestión de Derechos Automática',
    description: 'Registra composiciones, publicaciones y regalías en un lugar. Sincronización con ASCAP, BMI y organismos MX.'
  },
  {
    icon: BarChart3,
    title: 'Cálculo de Regalías en Tiempo Real',
    description: 'Spotify, YouTube, Apple Music, Amazon Music. Ve cuánto ganas por stream sin esperar reportes mensuales.'
  },
  {
    icon: Share2,
    title: 'Promoción Automática en Redes',
    description: 'Publica tu música en Spotify, YouTube y TikTok desde HERMES. Sin tocar plataformas — automático cada semana.'
  },
  {
    icon: Radio,
    title: 'Distribuidor Digital Integrado',
    description: 'Sube una canción. HERMES la distribuye a 50+ plataformas digitales globales en 48 horas.'
  },
  {
    icon: TrendingUp,
    title: 'Analytics Unificados',
    description: 'Descubre qué región te escucha más, qué canción crece, en qué playlist estás. Una dashboard, todo visible.'
  },
  {
    icon: Zap,
    title: 'Monetización Acelerada',
    description: 'Acceso directo a programas de monetización. Negocia sponsors, sincronización de TV y cine desde HERMES.'
  },
]

export default function ArtistasLanding() {
  return (
    <div className="relative min-h-screen bg-[#0a0500] text-white overflow-x-hidden">
      <Navigation showHome={true} />

      <Hero
        badge="Para Músicos, Podcasters y Creadores"
        title={<>HERMES para<br /><span className="text-purple-400">Creadores</span></>}
        subtitle="Distribución + Monetización + Marketing automático. De demos a Spotify en 48 horas. Crece sin gestor."
        cta={{ text: 'Haz Crecer tu Arte', href: '/artistas/onboarding' }}
        variant="artista"
      />

      <Features
        features={artistaFeatures}
        variant="artista"
        title="Herramientas de creador independiente"
      />

      <CaseStudy
        variant="artista"
        title="Músico independiente"
        problem="Distribuir en Spotify es gratis pero tedioso. Calcular regalías imposible. Promocionar manualmente consume horas. Perder oportunidades de monetización por falta de contactos."
        solution="HERMES sube automático, calcula regalías en tiempo real, promueve a redes cada semana, y te conecta con oportunidades de sincronización (TV, podcast, publicidad)."
        result="Primera canción en Spotify 48h después de composición. 5,000 reproducciones al mes. Primeros ingresos a los 2 meses. Acceso a 10 oportunidades de sincronización/mes."
        metric="0 → 5K streams/mes en 2 meses"
      />

      <section className="relative py-20 px-4 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-black">Planes para cada etapa</h2>
          <p className="text-white/60 mt-3">Crece a tu ritmo. Aumenta features según necesites.</p>
        </div>

        <div className="grid sm:grid-cols-3 gap-6">
          {[
            {
              title: 'Iniciante',
              price: 'Gratis',
              songs: '5 canciones/mes',
              desc: 'Perfecta para probar. Una canción, un mes, todas las plataformas.'
            },
            {
              title: 'Emergente',
              price: '$99',
              songs: '∞ canciones/mes',
              desc: 'Todo lo que necesitas para crecer. Analytics + promoción automática.'
            },
            {
              title: 'Profesional',
              price: '$299',
              songs: '∞ canciones + featured',
              desc: 'Gestor virtual. Oportunidades de sincronización. Negociación de contratos.'
            },
          ].map(plan => (
            <div key={plan.title} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col">
              <h3 className="font-black text-xl mb-1 text-purple-400">{plan.title}</h3>
              <p className="text-2xl font-black mb-1">{plan.price}</p>
              <p className="text-sm text-white/60 mb-4">/{plan.songs}</p>
              <p className="text-white/70 flex-1 mb-4">{plan.desc}</p>
              <button
                onClick={() => window.location.href = '/artistas/onboarding'}
                className="w-full py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 font-semibold text-sm transition"
              >
                Comenzar
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="relative py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-black">Plataformas donde distribuis</h2>
          <p className="text-white/60 mt-3">HERMES te lleva a todas. Una subida, 50+ destinos.</p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
          {[
            'Spotify', 'Apple Music', 'YouTube Music', 'Amazon Music',
            'TikTok', 'Instagram', 'Deezer', 'iHeartRadio',
            'Bandcamp', 'SoundCloud', 'Tidal', 'Pandora'
          ].map(platform => (
            <div key={platform} className="flex items-center justify-center h-16 rounded-lg bg-white/5 border border-white/10 hover:border-purple-400/30 transition">
              <span className="font-semibold text-white/80">{platform}</span>
            </div>
          ))}
        </div>

        <p className="text-center text-white/40 text-sm mt-8">
          Agregamos 5 plataformas nuevas cada mes. Pedí las que te faltan.
        </p>
      </section>

      <section className="relative py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="grid sm:grid-cols-2 gap-8">
          <div>
            <h2 className="text-3xl sm:text-4xl font-black mb-6">Cómo funciona en 3 pasos</h2>
            <div className="space-y-6">
              {[
                { num: '1', title: 'Compone o sube demo', desc: 'Canta, toca, graba. Sube el audio (o HERMES genera arte de portada con IA).' },
                { num: '2', title: 'HERMES distribuye', desc: 'Un clic. 48 horas. Tu música está en Spotify, Apple Music, YouTube y más.' },
                { num: '3', title: 'Monetiza y crece', desc: 'Recibe regalías, ve analytics, promociona automático. Sin hacer nada más.' },
              ].map(step => (
                <div key={step.num} className="flex gap-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-500/20 border border-purple-400/40 flex items-center justify-center">
                    <span className="font-black text-purple-400">{step.num}</span>
                  </div>
                  <div>
                    <h4 className="font-bold mb-1">{step.title}</h4>
                    <p className="text-white/60 text-sm">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
            <h3 className="font-black text-xl mb-6 text-purple-400">Testimonio real</h3>
            <blockquote className="text-white/70 leading-relaxed mb-4">
              "Subí mi primer sencillo el lunes. Viernes ya estaba en 5 plataformas. Al mes tenía 2K escuchas. HERMES hizo en 2 meses lo que yo hubiera tardado un año haciendo clicks en cada plataforma."
            </blockquote>
            <p className="text-sm text-white/40">— Sofía García, Cantautora Indie 🇲🇽</p>
          </div>
        </div>
      </section>

      <section className="relative py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-black mb-6">Comienza gratis hoy</h2>
          <p className="text-white/60 mb-8 max-w-xl mx-auto">
            Primer mes gratis. Sube 5 canciones. Verás en Spotify dentro de 48 horas.
          </p>
          <button
            onClick={() => window.location.href = '/artistas/onboarding'}
            className="px-8 py-4 rounded-xl bg-purple-500 text-white font-bold hover:bg-purple-600 transition"
          >
            Haz Crecer tu Arte Ahora
          </button>
        </div>
      </section>

      <Footer />
    </div>
  )
}
