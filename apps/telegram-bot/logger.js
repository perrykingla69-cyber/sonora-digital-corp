'use strict';

// Logger estructurado compartido — HERMES Telegram Bot
// Centraliza formato, nivel y transporte. Importar con: const log = require('./logger')
const log = {
  info:  (...a) => console.log('[INFO]',  ...a),
  warn:  (...a) => console.warn('[WARN]',  ...a),
  error: (...a) => console.error('[ERROR]', ...a),
};

module.exports = log;
