'use client'

import { useEffect, useState } from 'react'

const TARGET = new Date('2026-04-01T00:00:00-07:00') // Hermosillo (MST)

function pad(n: number) {
  return String(n).padStart(2, '0')
}

export function Countdown() {
  const [diff, setDiff] = useState(0)

  useEffect(() => {
    const tick = () => setDiff(Math.max(0, TARGET.getTime() - Date.now()))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  const days = Math.floor(diff / 86_400_000)
  const hours = Math.floor((diff % 86_400_000) / 3_600_000)
  const mins = Math.floor((diff % 3_600_000) / 60_000)
  const secs = Math.floor((diff % 60_000) / 1_000)

  return (
    <div className="flex items-center gap-3 text-center">
      {[
        { v: days, l: 'días' },
        { v: hours, l: 'hrs' },
        { v: mins, l: 'min' },
        { v: secs, l: 'seg' },
      ].map(({ v, l }) => (
        <div key={l} className="flex flex-col items-center rounded-2xl border border-amber-400/30 bg-amber-400/10 px-3 py-2 min-w-[52px]">
          <span className="text-2xl font-bold tabular-nums text-amber-300">{pad(v)}</span>
          <span className="text-[10px] uppercase tracking-widest text-amber-400/70">{l}</span>
        </div>
      ))}
    </div>
  )
}
