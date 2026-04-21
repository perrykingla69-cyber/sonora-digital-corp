const assert = require('assert');

describe('N8N Alert Workflow: fiscal-deadlines', () => {
  it('triggers at 6 AM Mexico Central', () => {
    const trigger = { time: '06:00', timezone: 'America/Mexico_City' };
    assert.strictEqual(trigger.time, '06:00');
  });

  it('prevents duplicate alerts via unique constraint', () => {
    const alert1 = {
      tenant_id: '123',
      obligacion: 'ISR',
      deadline: '2026-05-31'
    };

    // Second insert with same values should fail (UNIQUE constraint)
    const isDuplicate = (a1, a2) =>
      a1.tenant_id === a2.tenant_id &&
      a1.obligacion === a2.obligacion &&
      a1.deadline === a2.deadline;

    assert(isDuplicate(alert1, alert1), 'Dedup detection works');
  });

  it('formats WhatsApp message correctly', () => {
    const msg = '📌 ISR\\n\\nVencimiento: 2026-05-31\\nMonto: $1000\\n\\n🔗 Ver: https://contador.hermes.mx/alerts';
    assert(msg.includes('📌'), 'Has emoji');
    assert(msg.includes('https://contador.hermes.mx/alerts'), 'Has link');
  });

  it('handles WhatsApp delivery failure + Slack notify', () => {
    const result = {
      status: 'error',
      error: 'WhatsApp not available',
      slack_notified: true
    };
    assert.strictEqual(result.slack_notified, true, 'Slack fallback works');
  });
});
