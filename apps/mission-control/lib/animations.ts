import gsap from 'gsap'

export function animateCountUp(
  element: HTMLElement,
  from: number,
  to: number,
  duration: number = 1
) {
  gsap.to(element, {
    innerHTML: Math.floor(to),
    duration,
    snap: { innerHTML: 1 },
    ease: 'power2.out',
  })
}

export function animateGlowEffect(element: HTMLElement) {
  gsap.to(element, {
    boxShadow: ['0 0 20px rgba(0, 217, 255, 0.3)', '0 0 40px rgba(0, 217, 255, 0.5)'],
    duration: 2,
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
  })
}

export function staggerElements(elements: HTMLElement[], stagger: number = 0.05) {
  gsap.from(elements, {
    opacity: 0,
    y: 20,
    stagger,
    duration: 0.5,
    ease: 'back.out',
  })
}

export function createScrollReveal(element: HTMLElement) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          gsap.from(entry.target, {
            opacity: 0,
            y: 30,
            duration: 0.6,
            ease: 'power3.out',
          })
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.1 }
  )

  observer.observe(element)
  return observer
}
