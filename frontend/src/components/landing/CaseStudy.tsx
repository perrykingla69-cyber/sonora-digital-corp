'use client'

interface CaseStudyProps {
  title: string
  problem: string
  solution: string
  result: string
  metric: string
  variant?: 'contador' | 'artista'
}

export function CaseStudy({ title, problem, solution, result, metric, variant = 'contador' }: CaseStudyProps) {
  const bgColor = variant === 'contador' ? 'bg-blue-900/10 border-blue-400/20' : 'bg-purple-900/10 border-purple-400/20'
  const accentColor = variant === 'contador' ? 'text-blue-400' : 'text-purple-400'

  return (
    <section className="relative py-20 px-4 max-w-4xl mx-auto">
      <div className={`${bgColor} border rounded-3xl p-8 sm:p-12`}>
        <h2 className="text-3xl sm:text-4xl font-black mb-8">Caso de uso real</h2>

        <div className="grid sm:grid-cols-2 gap-8 mb-8">
          <div>
            <h3 className={`text-sm font-bold uppercase tracking-widest ${accentColor} mb-3`}>Problema</h3>
            <p className="text-white/70 leading-relaxed">{problem}</p>
          </div>
          <div>
            <h3 className={`text-sm font-bold uppercase tracking-widest ${accentColor} mb-3`}>Solución</h3>
            <p className="text-white/70 leading-relaxed">{solution}</p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8">
          <h3 className={`text-sm font-bold uppercase tracking-widest ${accentColor} mb-4`}>Resultado</h3>
          <p className="text-lg text-white/80 mb-6 leading-relaxed">{result}</p>
          <div className={`inline-block ${accentColor} text-2xl font-black`}>{metric}</div>
        </div>
      </div>
    </section>
  )
}
