-- ╔══════════════════════════════════════════════════════════╗
-- ║     HERMES OS — Multi-tenant Schema con RLS              ║
-- ║     Row Level Security: nunca cruza info entre tenants   ║
-- ╚══════════════════════════════════════════════════════════╝

-- Extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Schema N8N separado
CREATE SCHEMA IF NOT EXISTS n8n;

-- ── TENANTS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tenants (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug        VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(200) NOT NULL,
    plan        VARCHAR(20) NOT NULL DEFAULT 'starter' CHECK (plan IN ('starter','pro','enterprise')),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    settings    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── USUARIOS ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200),
    role            VARCHAR(20) NOT NULL DEFAULT 'member' CHECK (role IN ('owner','admin','member','viewer')),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- ── CANALES (WhatsApp instances, Telegram bots) ───────────────
CREATE TABLE IF NOT EXISTS channels (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type        VARCHAR(20) NOT NULL CHECK (type IN ('whatsapp','telegram','email','web')),
    name        VARCHAR(100) NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',  -- tokens, instance names (ENCRIPTADO)
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── CONVERSACIONES ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    channel_id      UUID REFERENCES channels(id),
    external_id     VARCHAR(255),        -- chat_id de Telegram / phone de WA
    contact_name    VARCHAR(200),
    contact_data    JSONB DEFAULT '{}',
    agent_assigned  VARCHAR(20) CHECK (agent_assigned IN ('hermes','mystic','human')),
    status          VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open','resolved','archived')),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── MENSAJES ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant','system','tool')),
    content         TEXT NOT NULL,
    agent           VARCHAR(20),         -- 'hermes' | 'mystic' | null
    tokens_used     INTEGER DEFAULT 0,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── DOCUMENTOS (contabilidad, facturas, etc.) ─────────────────
CREATE TABLE IF NOT EXISTS documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type            VARCHAR(50) NOT NULL,   -- 'factura','cfdi','reporte','contrato'
    folio           VARCHAR(100),
    period_year     INTEGER,
    period_month    INTEGER,
    amount          NUMERIC(15,2),
    currency        VARCHAR(3) DEFAULT 'MXN',
    data            JSONB NOT NULL DEFAULT '{}',
    file_path       VARCHAR(500),
    status          VARCHAR(30) DEFAULT 'pending',
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── AUDIT LOG (inmutable) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   UUID NOT NULL,
    user_id     UUID,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100),
    resource_id UUID,
    ip_address  INET,
    user_agent  TEXT,
    payload     JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY — El núcleo del multi-tenant
-- ════════════════════════════════════════════════════════════

-- Habilitar RLS en todas las tablas con tenant_id
ALTER TABLE users         ENABLE ROW LEVEL SECURITY;
ALTER TABLE channels      ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages      ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents     ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log     ENABLE ROW LEVEL SECURITY;

-- Rol de aplicación (nunca superuser en la app)
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hermes_app') THEN
        CREATE ROLE hermes_app;
    END IF;
END $$;

GRANT CONNECT ON DATABASE hermes_db TO hermes_app;
GRANT USAGE ON SCHEMA public TO hermes_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO hermes_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO hermes_app;

-- Función para obtener tenant del JWT/session
CREATE OR REPLACE FUNCTION current_tenant_id() RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_tenant_id', true), '')::UUID;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- POLÍTICAS RLS — cada tabla solo ve sus propios datos
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_tenant_id());

CREATE POLICY tenant_isolation ON channels
    USING (tenant_id = current_tenant_id());

CREATE POLICY tenant_isolation ON conversations
    USING (tenant_id = current_tenant_id());

CREATE POLICY tenant_isolation ON messages
    USING (tenant_id = current_tenant_id());

CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_tenant_id());

CREATE POLICY tenant_isolation ON audit_log
    USING (tenant_id = current_tenant_id());

-- ── ÍNDICES ───────────────────────────────────────────────────
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(tenant_id, email);
CREATE INDEX idx_conversations_tenant ON conversations(tenant_id, status);
CREATE INDEX idx_messages_conv ON messages(conversation_id, created_at);
CREATE INDEX idx_documents_tenant ON documents(tenant_id, type, period_year, period_month);
CREATE INDEX idx_audit_tenant ON audit_log(tenant_id, created_at);

-- ── TRIGGER: updated_at automático ───────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
