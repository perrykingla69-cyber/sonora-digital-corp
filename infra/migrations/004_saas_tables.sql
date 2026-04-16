-- ================================================================
-- Migración 004: SaaS Tables — Fase 1
-- Plataforma SaaS de Automatizaciones Sonora Digital Corp
-- ================================================================

-- ── Extender users table ─────────────────────────────────────
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS company_name       VARCHAR(255),
    ADD COLUMN IF NOT EXISTS subscription_plan  VARCHAR(20) NOT NULL DEFAULT 'free'
        CHECK (subscription_plan IN ('free', 'pro', 'enterprise')),
    ADD COLUMN IF NOT EXISTS api_key            VARCHAR(64) UNIQUE,
    ADD COLUMN IF NOT EXISTS api_key_hash       VARCHAR(255),
    ADD COLUMN IF NOT EXISTS api_key_created_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS api_key_last_used  TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS last_login         TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_active          BOOLEAN NOT NULL DEFAULT true;

-- ── plans ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plans (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(50) UNIQUE NOT NULL,  -- free, pro, enterprise
    price               DECIMAL(10,2) NOT NULL DEFAULT 0,
    requests_per_month  INTEGER NOT NULL DEFAULT 100,
    concurrent_bots     INTEGER NOT NULL DEFAULT 1,
    storage_gb          INTEGER NOT NULL DEFAULT 1,
    features            JSONB NOT NULL DEFAULT '[]',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO plans (name, price, requests_per_month, concurrent_bots, storage_gb, features) VALUES
    ('free',       0,    100,   1, 1,  '["1 agente", "100 mensajes/mes", "Soporte email"]'),
    ('pro',        499,  5000,  5, 10, '["5 agentes", "5,000 mensajes/mes", "Canales Telegram+WhatsApp", "Soporte prioritario"]'),
    ('enterprise', 1999, 0,    -1, 100,'["Agentes ilimitados", "Mensajes ilimitados", "Todos los canales", "SLA 99.9%", "Soporte dedicado"]')
ON CONFLICT (name) DO NOTHING;

-- ── subscriptions ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id               UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    plan                    VARCHAR(20) NOT NULL DEFAULT 'free'
        CHECK (plan IN ('free', 'pro', 'enterprise')),
    status                  VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'cancelled', 'expired', 'trialing')),
    current_period_start    DATE NOT NULL DEFAULT CURRENT_DATE,
    current_period_end      DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '30 days'),
    stripe_subscription_id  VARCHAR(255),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user   ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON subscriptions;
CREATE POLICY tenant_isolation ON subscriptions
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── agent_deployments ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_deployments (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    agent_type          VARCHAR(50) NOT NULL DEFAULT 'chat'
        CHECK (agent_type IN ('chat', 'task', 'data-processor', 'webhook')),
    model               VARCHAR(50) NOT NULL DEFAULT 'gemini-flash'
        CHECK (model IN ('gemini-flash', 'claude-code', 'n8n-workflow')),
    status              VARCHAR(20) NOT NULL DEFAULT 'creating'
        CHECK (status IN ('creating', 'active', 'failed', 'destroying', 'stopped')),
    progress            INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    verticales          TEXT[] DEFAULT '{}',
    config              JSONB NOT NULL DEFAULT '{}',
    container_id        VARCHAR(255),
    docker_compose_id   VARCHAR(255),
    deployment_url      VARCHAR(2048),
    error_message       TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX IF NOT EXISTS idx_agents_user   ON agent_deployments(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_tenant ON agent_deployments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agent_deployments(status);

ALTER TABLE agent_deployments ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON agent_deployments;
CREATE POLICY tenant_isolation ON agent_deployments
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_agents_updated_at
    BEFORE UPDATE ON agent_deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── bots ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bots (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_deployment_id UUID REFERENCES agent_deployments(id) ON DELETE SET NULL,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name                VARCHAR(255),
    channel             VARCHAR(20) NOT NULL
        CHECK (channel IN ('telegram', 'whatsapp', 'discord')),
    channel_id          VARCHAR(255),
    token_encrypted     TEXT,  -- Fernet encrypted
    webhook_url         VARCHAR(2048),
    status              VARCHAR(20) NOT NULL DEFAULT 'created'
        CHECK (status IN ('created', 'active', 'failed', 'destroying', 'stopped')),
    health_check_last   TIMESTAMPTZ,
    messages_today      INTEGER NOT NULL DEFAULT 0,
    uptime_pct          DECIMAL(5,2) NOT NULL DEFAULT 100.0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bots_user   ON bots(user_id);
CREATE INDEX IF NOT EXISTS idx_bots_tenant ON bots(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bots_agent  ON bots(agent_deployment_id);
CREATE INDEX IF NOT EXISTS idx_bots_status ON bots(status);

ALTER TABLE bots ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON bots;
CREATE POLICY tenant_isolation ON bots
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_bots_updated_at
    BEFORE UPDATE ON bots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
