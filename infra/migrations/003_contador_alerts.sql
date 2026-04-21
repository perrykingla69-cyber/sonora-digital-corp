-- Migration: 003 - Contador Fiscal Alerts

-- Table for tracking sent alerts (prevent duplicates)
CREATE TABLE IF NOT EXISTS alerts_sent (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  obligacion VARCHAR(255) NOT NULL,
  deadline DATE NOT NULL,
  sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
  status VARCHAR(50) DEFAULT 'sent',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Composite index for deduplication
CREATE UNIQUE INDEX IF NOT EXISTS idx_alerts_sent_unique
  ON alerts_sent(tenant_id, obligacion, deadline);

-- Index for cleanup queries
CREATE INDEX IF NOT EXISTS idx_alerts_sent_timestamp
  ON alerts_sent(sent_at);

-- Table for obligaciones by tenant
CREATE TABLE IF NOT EXISTS obligaciones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre VARCHAR(255) NOT NULL,
  vencimiento DATE NOT NULL,
  régimen VARCHAR(100) NOT NULL,
  completada BOOLEAN DEFAULT FALSE,
  monto NUMERIC(12, 2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index para búsquedas por tenant y vencimiento
CREATE INDEX IF NOT EXISTS idx_obligaciones_tenant_vencimiento
  ON obligaciones(tenant_id, vencimiento);

-- RLS policy for alerts_sent
ALTER TABLE alerts_sent ENABLE ROW LEVEL SECURITY;
CREATE POLICY alerts_sent_tenant_isolation ON alerts_sent
  USING (tenant_id = COALESCE(current_setting('app.current_tenant_id')::UUID, '00000000-0000-0000-0000-000000000000'));

-- RLS policy for obligaciones
ALTER TABLE obligaciones ENABLE ROW LEVEL SECURITY;
CREATE POLICY obligaciones_tenant_isolation ON obligaciones
  USING (tenant_id = COALESCE(current_setting('app.current_tenant_id')::UUID, '00000000-0000-0000-0000-000000000000'));
