export function HermesEyeLogo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
      <defs>
        <radialGradient id="eyeGold" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f0c842" />
          <stop offset="60%" stopColor="#D4AF37" />
          <stop offset="100%" stopColor="#8B7520" />
        </radialGradient>
        <radialGradient id="irisGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#1a0a00" />
          <stop offset="40%" stopColor="#3d1f00" />
          <stop offset="100%" stopColor="#D4AF37" />
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <polygon points="50,4 96,86 4,86" fill="none" stroke="url(#eyeGold)" strokeWidth="2.5" filter="url(#glow)" />
      <polygon points="50,28 76,74 24,74" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      <polygon points="50,72 74,28 26,28" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      <ellipse cx="50" cy="54" rx="16" ry="10" fill="none" stroke="url(#eyeGold)" strokeWidth="1.5" />
      <circle cx="50" cy="54" r="7" fill="url(#irisGrad)" />
      <circle cx="50" cy="54" r="3" fill="#0a0500" />
      <circle cx="52" cy="52" r="1" fill="#D4AF37" opacity="0.8" />
      <path d="M34,54 Q50,44 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
      <path d="M34,54 Q50,64 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
    </svg>
  )
}
