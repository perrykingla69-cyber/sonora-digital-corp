import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

/**
 * Create scroll trigger for reveal animation
 */
export function createScrollReveal(
  element: HTMLElement | string,
  options: gsap.TweenVars = {}
) {
  return gsap.fromTo(
    element,
    {
      opacity: 0,
      y: 40,
    },
    {
      opacity: 1,
      y: 0,
      duration: 0.8,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: element,
        start: 'top 80%',
        end: 'top 20%',
        toggleActions: 'play none none none',
        markers: false,
      },
      ...options,
    }
  )
}

/**
 * Create staggered scroll reveal for multiple elements
 */
export function createStaggerReveal(
  elements: string | NodeListOf<Element>,
  options: gsap.TweenVars = {}
) {
  return gsap.to(elements, {
    opacity: 1,
    y: 0,
    stagger: 0.2,
    duration: 0.8,
    ease: 'power2.out',
    scrollTrigger: {
      trigger: Array.isArray(elements) ? elements[0] : elements,
      start: 'top 80%',
      toggleActions: 'play none none none',
    },
    ...options,
  })
}

/**
 * Create count-up animation for numbers
 */
export function createCountUp(
  element: HTMLElement | string,
  endValue: number,
  duration: number = 2
) {
  const obj = { value: 0 }
  return gsap.to(obj, {
    value: endValue,
    duration,
    ease: 'power2.out',
    scrollTrigger: {
      trigger: element,
      start: 'top 80%',
      toggleActions: 'play none none none',
    },
    onUpdate() {
      if (typeof element === 'string') {
        const el = document.querySelector(element)
        if (el) el.textContent = Math.floor(obj.value).toLocaleString()
      } else {
        element.textContent = Math.floor(obj.value).toLocaleString()
      }
    },
  })
}

/**
 * Create clip-path scan animation
 */
export function createScanReveal(
  element: HTMLElement | string,
  options: gsap.TweenVars = {}
) {
  return gsap.fromTo(
    element,
    {
      clipPath: 'polygon(0 0, 0 0, 0 100%, 0 100%)',
    },
    {
      clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
      duration: 1.2,
      ease: 'power2.inOut',
      scrollTrigger: {
        trigger: element,
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
      ...options,
    }
  )
}

/**
 * Create parallax effect for scroll
 */
export function createParallax(
  element: HTMLElement | string,
  speed: number = 0.5
) {
  gsap.to(element, {
    y: (i, target) => {
      return -ScrollTrigger.getVelocity(target) * speed
    },
    ease: 'none',
    overwrite: 'auto',
    scrollTrigger: {
      trigger: element,
      onUpdate: (self) => {
        gsap.to(element, {
          y: -self.getVelocity() * speed,
          overwrite: 'auto',
          duration: 0.5,
        })
      },
    },
  })
}

/**
 * Create 3D light source follow effect
 */
export function create3DLightFollow(
  element: HTMLElement | string,
  intensity: number = 1
) {
  if (typeof window === 'undefined') return

  const el = typeof element === 'string'
    ? document.querySelector(element) as HTMLElement
    : element

  if (!el) return

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY
    const rotationY = (scrollY * 0.1) % 360

    gsap.to(el, {
      rotationY,
      duration: 0.5,
      ease: 'none',
      transformOrigin: '50% 50% 0',
      transformStyle: 'preserve-3d',
    })
  })
}

/**
 * Kill all scroll triggers (useful for cleanup)
 */
export function killAllScrollTriggers() {
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
}

/**
 * Refresh all scroll triggers after layout changes
 */
export function refreshScrollTriggers() {
  ScrollTrigger.refresh()
}
