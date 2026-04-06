-- ================================================================
-- Migración 003: videos, assets, tokens internos
-- Para HeyGen webhook, fal.ai webhook y sistema de tokens
-- ================================================================

-- ── Columnas nuevas en users ──────────────────────────────────
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS telegram_chat_id  VARCHAR(50),
    ADD COLUMN IF NOT EXISTS tokens_balance    INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS plan              VARCHAR(20) NOT NULL DEFAULT 'starter'
        CHECK (plan IN ('starter', 'pro', 'enterprise')),
    ADD COLUMN IF NOT EXISTS slug              VARCHAR(100) UNIQUE,
    ADD COLUMN IF NOT EXISTS avatar_url        TEXT;

-- ── Tabla videos (HeyGen) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS videos (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    external_id     VARCHAR(200) UNIQUE,          -- video_id de HeyGen
    title           VARCHAR(300),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'ready', 'failed')),
    url             TEXT,                          -- URL del video terminado
    thumbnail_url   TEXT,
    error_message   TEXT,
    tokens_cost     INTEGER NOT NULL DEFAULT 50,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_tenant   ON videos(tenant_id);
CREATE INDEX IF NOT EXISTS idx_videos_user     ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_external ON videos(external_id);

-- RLS
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON videos;
CREATE POLICY tenant_isolation ON videos
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Tabla assets (fal.ai) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS assets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id      VARCHAR(200) UNIQUE,           -- request_id de fal.ai
    type            VARCHAR(20) NOT NULL DEFAULT 'image'
        CHECK (type IN ('image', 'video', 'unknown')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'ready', 'failed')),
    url             TEXT,
    prompt          TEXT,
    model_used      VARCHAR(100),
    error_message   TEXT,
    tokens_cost     INTEGER NOT NULL DEFAULT 10,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_tenant  ON assets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assets_user    ON assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_request ON assets(request_id);

ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON assets;
CREATE POLICY tenant_isolation ON assets
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Tabla token_packages (paquetes de tokens) ─────────────────
CREATE TABLE IF NOT EXISTS token_packages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    tokens      INTEGER NOT NULL,
    price_mxn   NUMERIC(10,2) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_promo    BOOLEAN NOT NULL DEFAULT FALSE,
    badge       VARCHAR(50),                       -- "POPULAR", "OFERTA", etc.
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Paquetes iniciales
INSERT INTO token_packages (name, tokens, price_mxn, is_promo, badge) VALUES
    ('Starter Pack',    500,   49.00, FALSE, NULL),
    ('Pro Pack',       2000,  149.00, FALSE, 'POPULAR'),
    ('Creator Pack',   5000,  299.00, FALSE, NULL),
    ('Mega Pack',     15000,  699.00, TRUE,  'MEJOR PRECIO')
ON CONFLICT DO NOTHING;

-- ── Tabla payments (historial de pagos) ──────────────────────
CREATE TABLE IF NOT EXISTS payments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    external_id     VARCHAR(200) UNIQUE,   -- payment_id de MercadoPago
    tokens_credited INTEGER NOT NULL DEFAULT 0,
    amount_mxn      NUMERIC(10,2),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'failed', 'refunded')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_user     ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_external ON payments(external_id);
