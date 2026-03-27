'use strict';

/**
 * sat-alerts.js — Módulo de alertas SAT para canal Telegram
 * HERMES / Sonora Digital Corp
 *
 * Uso:
 *   const { sendSATAlert, getSATAlertMessage, scheduleMonthlyAlerts } = require('./sat-alerts');
 */

// Logger estructurado
const log = {
  info:  (...a) => console.log('[INFO]', ...a),
  warn:  (...a) => console.warn('[WARN]', ...a),
  error: (...a) => console.error('[ERROR]', ...a),
};

// ── Mensajes preformateados por tipo ─────────────────────────────────────────

const SAT_MESSAGES = {
  /**
   * Día 17 — Declaración mensual de impuestos (ISR, IVA, IEPS)
   * El SAT exige presentar la declaración a más tardar el día 17 de cada mes.
   */
  dia_17: () => {
    const month = new Date().toLocaleString('es-MX', { month: 'long' });
    return (
      `📅 *Recordatorio: Declaración Mensual — Día 17*\n\n` +
      `Hoy vence el plazo para presentar tu declaración provisional de impuestos correspondiente al mes anterior.\n\n` +
      `*¿Qué debes presentar?*\n` +
      `• ISR provisional (personas físicas y morales)\n` +
      `• IVA mensual\n` +
      `• IEPS (si aplica a tu giro)\n\n` +
      `*¿Por qué importa?*\n` +
      `No presentar a tiempo genera actualizaciones, recargos y multas automáticas del SAT. Un día de retraso puede costarte cientos de pesos.\n\n` +
      `💡 _HERMES lo gestiona por ti — sonoradigitalcorp.com_`
    );
  },

  /**
   * DIOT — Declaración Informativa de Operaciones con Terceros
   * Vence el día 17 del mes siguiente al período declarado.
   */
  diot: () => {
    return (
      `📋 *Vencimiento DIOT — Declaración Informativa de Operaciones con Terceros*\n\n` +
      `La DIOT es la declaración donde informas al SAT todas las operaciones de IVA realizadas con tus proveedores durante el mes pasado.\n\n` +
      `*¿A quién aplica?*\n` +
      `• Personas morales del régimen general\n` +
      `• Personas físicas con actividad empresarial\n` +
      `• Importadores y exportadores\n\n` +
      `*¿Por qué importa?*\n` +
      `Errores u omisiones en la DIOT pueden generar cartas-invitación del SAT, auditorías o bloqueo de sellos digitales. Cada proveedor debe cuadrar con su RFC y monto real.\n\n` +
      `💡 _HERMES lo gestiona por ti — sonoradigitalcorp.com_`
    );
  },

  /**
   * CFDI — Verificación y conciliación de comprobantes fiscales
   */
  cfdi: () => {
    return (
      `🧾 *Recordatorio: Verificación de CFDIs del Mes*\n\n` +
      `Es momento de conciliar todos los Comprobantes Fiscales Digitales emitidos y recibidos durante el mes.\n\n` +
      `*¿Qué debes revisar?*\n` +
      `• CFDIs emitidos: que estén vigentes y sin errores\n` +
      `• CFDIs recibidos: que los RFCs sean válidos y los importes correctos\n` +
      `• Notas de crédito: cancelaciones correctamente aplicadas\n` +
      `• Complementos de pago: ligados a sus facturas originales\n\n` +
      `*¿Por qué importa?*\n` +
      `Un CFDI incorrecto no es deducible. El SAT cruza automáticamente lo que declaras con lo que tus proveedores y clientes reportan.\n\n` +
      `💡 _HERMES lo gestiona por ti — sonoradigitalcorp.com_`
    );
  },

  /**
   * Cierre mensual — Proceso de cierre contable
   */
  cierre: () => {
    const date = new Date();
    const month = date.toLocaleString('es-MX', { month: 'long' });
    const year = date.getFullYear();
    return (
      `🔒 *Cierre Mensual Próximo — Revisa tu Contabilidad*\n\n` +
      `El cierre contable de ${month} ${year} se aproxima. Es el momento de validar que todo esté cuadrado antes de declarar.\n\n` +
      `*Lista de cierre rápida:*\n` +
      `• ✅ Conciliar cuentas bancarias vs. libro mayor\n` +
      `• ✅ Revisar cuentas por cobrar y pagar\n` +
      `• ✅ Verificar nómina timbrada y IMSS pagado\n` +
      `• ✅ Confirmar inventario (si aplica)\n` +
      `• ✅ Registrar depreciaciones del período\n` +
      `• ✅ Validar saldo de IVA acreditable\n\n` +
      `*¿Por qué importa?*\n` +
      `Un cierre limpio garantiza que tus declaraciones sean exactas y reduce el riesgo de discrepancias ante el SAT.\n\n` +
      `💡 _HERMES lo gestiona por ti — sonoradigitalcorp.com_`
    );
  },

  /**
   * MVE — Módulo de Verificación de Existencia (importadores)
   * Obligatorio para quienes importan mercancías bajo pedimento.
   */
  mve: () => {
    return (
      `🚢 *Recordatorio MVE — Módulo de Verificación de Existencia*\n\n` +
      `Si tu empresa importa mercancías, el SAT requiere que verifiques la existencia física de los bienes registrados en tus pedimentos.\n\n` +
      `*¿Qué implica el MVE?*\n` +
      `• Corroborar que el inventario importado coincide con los pedimentos declarados\n` +
      `• Tener documentación de origen, tránsito y recepción\n` +
      `• Actualizar el registro en el portal del SAT si hubo variaciones\n\n` +
      `*¿A quién aplica?*\n` +
      `Importadores directos, empresas IMMEX, operadores de comercio exterior y sus agentes aduanales.\n\n` +
      `*¿Por qué importa?*\n` +
      `Discrepancias entre lo declarado y lo existente pueden resultar en embargo de mercancías, multas aduanales o cancelación del padrón de importadores.\n\n` +
      `💡 _HERMES lo gestiona por ti — sonoradigitalcorp.com_`
    );
  },
};

// ── Función pública: obtener mensaje por tipo ─────────────────────────────────

/**
 * Retorna el mensaje de alerta SAT formateado en Markdown para Telegram.
 * @param {'dia_17'|'diot'|'cfdi'|'cierre'|'mve'} type
 * @returns {string}
 */
function getSATAlertMessage(type) {
  const generator = SAT_MESSAGES[type];
  if (!generator) {
    throw new Error(`Tipo de alerta SAT no reconocido: "${type}". Tipos válidos: dia_17, diot, cfdi, cierre, mve`);
  }
  return generator();
}

// ── Función pública: enviar alerta a un canal ─────────────────────────────────

/**
 * Envía una alerta SAT formateada a un canal de Telegram.
 * @param {import('telegraf').Telegraf} bot   - Instancia activa de Telegraf
 * @param {string|number}              channelId  - ID o username del canal (e.g. "@HermesFiscalMX")
 * @param {{ tipo: string, extra?: string }} alertData
 * @returns {Promise<void>}
 */
async function sendSATAlert(bot, channelId, alertData) {
  const { tipo, extra } = alertData;

  let mensaje = getSATAlertMessage(tipo);
  if (extra) {
    mensaje += `\n\n📌 _${extra}_`;
  }

  try {
    await bot.telegram.sendMessage(channelId, mensaje, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
    });
    log.info(`[SAT Alerts] ✅ Alerta "${tipo}" enviada a ${channelId}`);
  } catch (err) {
    log.error(`[SAT Alerts] ❌ Error enviando alerta "${tipo}" a ${channelId}:`, err.message);
    throw err;
  }
}

// ── Función pública: programar alertas mensuales ──────────────────────────────

/**
 * Programa las alertas SAT recurrentes usando node-cron (si está disponible)
 * con fallback a setTimeout para el mismo día.
 *
 * Calendario fiscal mexicano cubierto:
 *   Día  1  → Alerta cierre del mes anterior (inicio de cierre)
 *   Día 10  → Recordatorio CFDI + DIOT (una semana antes del vencimiento)
 *   Día 16  → Pre-alerta Día 17 (mañana vence)
 *   Día 17  → Alerta declaración mensual + DIOT
 *   Día 20  → Recordatorio MVE para importadores
 *   Día 25  → Recordatorio cierre del mes en curso
 *
 * @param {import('telegraf').Telegraf} bot
 * @param {string|number} channelId
 * @returns {void}
 */
function scheduleMonthlyAlerts(bot, channelId) {
  let cron;
  try {
    cron = require('node-cron');
  } catch {
    cron = null;
  }

  if (cron) {
    // ── Programación con node-cron ──────────────────────────────────────────
    // Formato: segundo(opc) minuto hora día_mes mes día_semana

    // Día 1 — Inicio de cierre del mes anterior (8:00 AM)
    cron.schedule('0 8 1 * *', () => {
      sendSATAlert(bot, channelId, { tipo: 'cierre' })
        .catch(e => log.error('[SAT Cron] cierre:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 10 — Recordatorio CFDI (7 días antes del vencimiento)
    cron.schedule('0 8 10 * *', () => {
      sendSATAlert(bot, channelId, {
        tipo: 'cfdi',
        extra: 'Faltan 7 días para el vencimiento del día 17. Revisa tus CFDIs ahora.',
      }).catch(e => log.error('[SAT Cron] cfdi:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 14 — Recordatorio DIOT (3 días antes)
    cron.schedule('0 8 14 * *', () => {
      sendSATAlert(bot, channelId, {
        tipo: 'diot',
        extra: 'Faltan 3 días para presentar la DIOT. Verifica tus proveedores.',
      }).catch(e => log.error('[SAT Cron] diot:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 16 — Pre-alerta Día 17 (mañana vence)
    cron.schedule('0 8 16 * *', () => {
      sendSATAlert(bot, channelId, {
        tipo: 'dia_17',
        extra: '⚡ Mañana es el último día. No esperes hasta el final.',
      }).catch(e => log.error('[SAT Cron] dia_17 pre:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 17 — Alerta principal de declaración mensual (8:00 AM)
    cron.schedule('0 8 17 * *', () => {
      sendSATAlert(bot, channelId, { tipo: 'dia_17' })
        .catch(e => log.error('[SAT Cron] dia_17:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 17 — DIOT (mismo día) (9:00 AM, escalonado)
    cron.schedule('0 9 17 * *', () => {
      sendSATAlert(bot, channelId, { tipo: 'diot' })
        .catch(e => log.error('[SAT Cron] diot dia17:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 20 — MVE para importadores (8:00 AM)
    cron.schedule('0 8 20 * *', () => {
      sendSATAlert(bot, channelId, { tipo: 'mve' })
        .catch(e => log.error('[SAT Cron] mve:', e.message));
    }, { timezone: 'America/Mexico_City' });

    // Día 25 — Recordatorio cierre del mes en curso (8:00 AM)
    cron.schedule('0 8 25 * *', () => {
      sendSATAlert(bot, channelId, {
        tipo: 'cierre',
        extra: 'Quedan 6 días para terminar el mes. Revisa que todo esté al corriente.',
      }).catch(e => log.error('[SAT Cron] cierre 25:', e.message));
    }, { timezone: 'America/Mexico_City' });

    log.info('[SAT Alerts] Alertas mensuales programadas con node-cron (timezone: America/Mexico_City)');

  } else {
    // ── Fallback: setTimeout para disparar hoy si corresponde ──────────────
    log.warn('[SAT Alerts] node-cron no disponible. Usando fallback de setTimeout para el día actual.');

    const ahora = new Date();
    const dia = ahora.getDate();

    const todayAlerts = [];

    if (dia === 1)  todayAlerts.push({ tipo: 'cierre' });
    if (dia === 10) todayAlerts.push({ tipo: 'cfdi', extra: 'Faltan 7 días para el vencimiento del día 17.' });
    if (dia === 14) todayAlerts.push({ tipo: 'diot', extra: 'Faltan 3 días para presentar la DIOT.' });
    if (dia === 16) todayAlerts.push({ tipo: 'dia_17', extra: '⚡ Mañana es el último día.' });
    if (dia === 17) todayAlerts.push({ tipo: 'dia_17' }, { tipo: 'diot' });
    if (dia === 20) todayAlerts.push({ tipo: 'mve' });
    if (dia === 25) todayAlerts.push({ tipo: 'cierre', extra: 'Quedan 6 días para terminar el mes.' });

    todayAlerts.forEach((alertData, i) => {
      // Escalonar 60 segundos entre cada alerta para no saturar
      setTimeout(() => {
        sendSATAlert(bot, channelId, alertData)
          .catch(e => log.error('[SAT Timeout] error:', e.message));
      }, i * 60_000);
    });

    if (todayAlerts.length > 0) {
      log.info(`[SAT Alerts] ${todayAlerts.length} alerta(s) programadas para hoy (día ${dia}).`);
    } else {
      log.info(`[SAT Alerts] Sin alertas para hoy (día ${dia}). node-cron recomendado para cobertura completa.`);
    }
  }
}

// ── Exports ───────────────────────────────────────────────────────────────────

module.exports = {
  getSATAlertMessage,
  sendSATAlert,
  scheduleMonthlyAlerts,
};
