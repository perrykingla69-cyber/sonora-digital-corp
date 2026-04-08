import type { Metadata } from 'next'
import { getNichoConfig } from '@/lib/niche-config'
import NicheLanding from '@/components/landing/NicheLanding'
import { notFound } from 'next/navigation'

interface Props {
  params: {
    niche: string
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const niche = getNichoConfig(params.niche)
  if (!niche) return { title: 'No encontrado' }

  return {
    title: niche.seoTitle,
    description: niche.seoDescription,
    keywords: niche.seoKeywords,
    openGraph: {
      title: niche.seoTitle,
      description: niche.seoDescription,
      url: `https://hermes.app/${niche.id}`,
      siteName: 'HERMES',
      type: 'website',
      images: [
        {
          url: `https://hermes.app/og-${niche.id}.png`,
          width: 1200,
          height: 630,
        }
      ]
    },
    twitter: {
      card: 'summary_large_image',
      title: niche.seoTitle,
      description: niche.seoDescription
    }
  }
}

export default function NichePage({ params }: Props) {
  const niche = getNichoConfig(params.niche)

  if (!niche) {
    notFound()
  }

  return <NicheLanding niche={niche} />
}
