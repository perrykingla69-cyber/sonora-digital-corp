// Configuración de nichos para landings
export interface NicheConfig {
  id: string
  name: string
  title: string
  subtitle: string
  description: string
  features: string[]
  cta: string
  color: string
  icon: string
  seoTitle: string
  seoDescription: string
  seoKeywords: string[]
}

export const NICHOS: Record<string, NicheConfig> = {
  restaurante: {
    id: 'restaurante',
    name: 'Restaurante',
    title: 'HERMES para Restaurantes y Bares',
    subtitle: 'Gestión automática de inventario, pedidos y contabilidad en tiempo real',
    description: 'Simplifica tu operación diaria: compra inteligente, inventario automático, facturas CFDI al instante, y análisis de márgenes por platillo. Sin papeleos, sin errores.',
    features: [
      'Inventario automático por receta y ingrediente',
      'Órdenes de compra inteligentes a proveedores',
      'Facturas CFDI en segundos',
      'Control de márgenes por platillo',
      'WhatsApp Bot para ordenes rápidas',
      'Reportes diarios de venta y ganancia'
    ],
    cta: 'Probar Gratis — 7 Días',
    color: 'from-red-600 to-orange-500',
    icon: '🍽️',
    seoTitle: 'HERMES: Software para Restaurantes | Contabilidad Automática',
    seoDescription: 'Gestiona inventario, facturas CFDI y contabilidad de tu restaurante con IA. Sin errores, sin papeleos, en tiempo real.',
    seoKeywords: ['software restaurantes', 'facturación CFDI', 'inventario restaurante', 'contabilidad bares', 'POS CFDI México']
  },
  contador: {
    id: 'contador',
    name: 'Contador',
    title: 'HERMES para Contadores',
    subtitle: 'Tu asistente fiscal IA que automatiza cierres, reportes y normatividad',
    description: 'Dedícate a tu negocio, no a papeles. HERMES cierra contabilidad automáticamente, genera reportes impositivos, alerta sobre normatividad SAT, y crea cedulas fiscales sin errores.',
    features: [
      'Cierre mensual automático',
      'Reportes RESICO, ISR, IVA automáticos',
      'Alertas de normatividad SAT en tiempo real',
      'Banco de datos de clientes y proveedores',
      'Cédulas y anexos generados automáticamente',
      'Dashboard de auditoría fiscal'
    ],
    cta: 'Acceder a Demo',
    color: 'from-blue-600 to-indigo-500',
    icon: '📊',
    seoTitle: 'HERMES Contadores: Software Fiscal | Cierre Automático',
    seoDescription: 'Software contable con IA: cierre automático, reportes fiscales RESICO, alertas SAT. Para contadores y despachos contables en México.',
    seoKeywords: ['software contable', 'cierre automático', 'reportes fiscales', 'RESICO', 'despacho contable México']
  },
  pastelero: {
    id: 'pastelero',
    name: 'Pastelería',
    title: 'HERMES para Panaderías y Pastelerías',
    subtitle: 'Control de recetas, costos y production scheduling automático',
    description: 'Recetas con costos precisos, cálculo automático de márgenes, compra de ingredientes planificada, facturas CFDI sin delays. Crece sin perder ganancia.',
    features: [
      'Recetas con costeo automático',
      'Planificación de producción semanal',
      'Alertas de ingredientes bajos',
      'Órdenes de compra automáticas',
      'Análisis de margen por producto',
      'Control de stock en tiempo real'
    ],
    cta: 'Empezar Ahora',
    color: 'from-amber-500 to-yellow-400',
    icon: '🎂',
    seoTitle: 'HERMES Panaderías: Gestión de Recetas y Costos',
    seoDescription: 'Software para panaderías: control de recetas, costos automáticos, inventario, facturas CFDI. Aumenta ganancias y reduce desperdicios.',
    seoKeywords: ['software pastelería', 'gestión recetas', 'costos producción', 'inventario panadería', 'facturas CFDI']
  },
  abogado: {
    id: 'abogado',
    name: 'Abogado',
    title: 'HERMES para Despachos de Abogados',
    subtitle: 'CRM de clientes, facturación de honorarios, y agenda de plazos automática',
    description: 'Administra clientes, casos, y honorarios sin pisar cortes. HERMES registra plazos críticos, genera facturas CFDI legales, y genera alertas antes de vencer términos procesales.',
    features: [
      'CRM especializado para clientes y casos',
      'Calendario automático de plazos procesales',
      'Alertas 48h antes de términos críticos',
      'Facturación de honorarios automática',
      'Expedientes digitales organizados',
      'Reportes mensuales de ingresos por área'
    ],
    cta: 'Solicitar Demo',
    color: 'from-purple-600 to-pink-500',
    icon: '⚖️',
    seoTitle: 'HERMES Abogados: CRM Despacho Legal | Gestión de Casos',
    seoDescription: 'Software CRM para despachos de abogados: gestión de casos, alertas de plazos procesales, facturación de honorarios. México.',
    seoKeywords: ['software abogados', 'CRM despacho legal', 'gestión de casos', 'alertas plazos', 'facturación honorarios']
  },
  fontanero: {
    id: 'fontanero',
    name: 'Fontanero',
    title: 'HERMES para Fontaneros y Servicios',
    subtitle: 'Agenda de trabajos, presupuestos automáticos, y facturación en sitio',
    description: 'Recibe trabajos vía WhatsApp, genera presupuestos al instante, factura CFDI en el sitio de la obra. Cobra más, pierde menos tiempo en papeleos.',
    features: [
      'WhatsApp Bot para solicitar trabajos',
      'Presupuestos con margen automático',
      'Calendario de trabajos por día',
      'Factura CFDI en sitio (app móvil)',
      'Historial de clientes y trabajos previos',
      'Reportes de ganancia por trabajo'
    ],
    cta: 'Probar Ahora',
    color: 'from-cyan-600 to-blue-500',
    icon: '🔧',
    seoTitle: 'HERMES Servicios: Agenda de Trabajos | Facturas CFDI Móvil',
    seoDescription: 'App para fontaneros y técnicos: agenda de trabajos, presupuestos automáticos, facturas CFDI móvil. Cobra rápido, sin papeles.',
    seoKeywords: ['app fontaneros', 'facturas CFDI móvil', 'gestión servicios', 'presupuestos automáticos', 'agenda trabajos']
  },
  consultor: {
    id: 'consultor',
    name: 'Consultor',
    title: 'HERMES para Consultores',
    subtitle: 'Gestión de proyectos, facturación por horas, y reportes de progreso automático',
    description: 'Registra horas de trabajo por cliente y proyecto, factura automáticamente con CFDI, y genera reportes de progreso sin esfuerzo. Enfócate en asesoría, no en administrativa.',
    features: [
      'Timesheet automático por cliente/proyecto',
      'Facturación por horas o deliverables',
      'Reportes de avance automáticos',
      'Control de presupuesto vs. real por proyecto',
      'Dashboard de rentabilidad por cliente',
      'Integración con Calendly/Google Calendar'
    ],
    cta: 'Acceder Ahora',
    color: 'from-green-600 to-emerald-500',
    icon: '💼',
    seoTitle: 'HERMES Consultores: Facturación de Proyectos | Timesheet IA',
    seoDescription: 'Software para consultores: gestión de proyectos, timesheet automático, facturación CFDI. Aumenta rentabilidad por cliente.',
    seoKeywords: ['software consultores', 'gestión proyectos', 'timesheet', 'facturación CFDI', 'control presupuesto']
  }
}

export function getNichoConfig(nichoId: string): NicheConfig | null {
  return NICHOS[nichoId] || null
}

export function getAllNichos(): NicheConfig[] {
  return Object.values(NICHOS)
}
