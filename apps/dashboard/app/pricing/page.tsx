import PricingTable from '@/components/PricingTable'
import Link from 'next/link'

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-dark-950 py-16 px-4">
      {/* Header */}
      <div className="text-center mb-12">
        <Link href="/" className="inline-flex items-center gap-2 mb-8">
          <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
            <span className="text-white font-bold">S</span>
          </div>
          <span className="text-xl font-bold text-white">Sonora Digital</span>
        </Link>
        <h1 className="text-4xl font-bold text-white mb-4">
          Planes simples y transparentes
        </h1>
        <p className="text-white/50 max-w-xl mx-auto">
          Automatiza tu negocio desde el día uno. Sin contratos, sin sorpresas.
          Cancela cuando quieras.
        </p>
      </div>

      <PricingTable />

      {/* FAQ simple */}
      <div className="max-w-2xl mx-auto mt-16">
        <h2 className="text-xl font-bold text-white text-center mb-8">Preguntas frecuentes</h2>
        <div className="space-y-4">
          {[
            {
              q: '¿Qué es un "agente"?',
              a: 'Un agente es un bot IA entrenado para tu negocio que responde automáticamente a tus clientes en Telegram, WhatsApp u otros canales.',
            },
            {
              q: '¿Puedo cambiar de plan después?',
              a: 'Sí, puedes subir o bajar de plan en cualquier momento. Los cambios aplican en tu siguiente ciclo de facturación.',
            },
            {
              q: '¿Qué pasa si supero el límite de mensajes?',
              a: 'Tu agente sigue funcionando pero te avisamos para que actualices tu plan. No hay cortes sorpresivos.',
            },
            {
              q: '¿Los precios incluyen IVA?',
              a: 'Los precios mostrados son antes de IVA. Para facturas, escríbenos a sonoradigitalcorp@gmail.com.',
            },
          ].map(item => (
            <div key={item.q} className="glass rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-2">{item.q}</h3>
              <p className="text-sm text-white/50">{item.a}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="text-center mt-12">
        <p className="text-white/40 text-sm">
          ¿Preguntas? Escríbenos:{' '}
          <a href="mailto:sonoradigitalcorp@gmail.com" className="text-brand-400 hover:text-brand-300">
            sonoradigitalcorp@gmail.com
          </a>{' '}
          · {' '}
          <a href="tel:+526623538272" className="text-brand-400 hover:text-brand-300">
            662-353-8272
          </a>
        </p>
      </div>
    </div>
  )
}
