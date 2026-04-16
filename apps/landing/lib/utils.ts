/**
 * Utility functions for the landing page
 */

/**
 * Combine class names safely
 */
export function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(' ')
}

/**
 * Format number with thousands separator
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('es-MX')
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

/**
 * Check if element is in viewport
 */
export function isInViewport(element: HTMLElement): boolean {
  const rect = element.getBoundingClientRect()
  return (
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.bottom >= 0
  )
}

/**
 * Animate value change
 */
export function animateValue(
  element: HTMLElement,
  start: number,
  end: number,
  duration: number = 1000
) {
  const range = end - start
  const increment = (range / duration) * 16 // 60fps
  let current = start
  let elapsed = 0

  const timer = setInterval(() => {
    elapsed += 16
    current += increment

    if (elapsed >= duration) {
      current = end
      clearInterval(timer)
    }

    element.textContent = Math.floor(current).toLocaleString('es-MX')
  }, 16)
}
