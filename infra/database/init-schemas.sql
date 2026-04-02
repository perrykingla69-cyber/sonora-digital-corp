-- ========== MULTI-TENANT SCHEMA ==========

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    rfc VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    tier VARCHAR(20) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Fourgea
INSERT INTO tenants (name, rfc, email, tier) VALUES 
('Fourgea México SA de CV', 'FOU201202ABC', 'admin@fourgea.com', 'premium')
ON CONFLICT (rfc) DO NOTHING;

-- Triple R
INSERT INTO tenants (name, rfc, email, tier) VALUES 
('Triple R Empresa', 'TRI201202ABC', 'admin@tripler.com', 'premium')
ON CONFLICT (rfc) DO NOTHING;

-- ========== USUARIOS POR TENANT ==========

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- ========== AUDIT LOG ==========

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100),
    resource VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant ON audit_log(tenant_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);

GRANT USAGE ON SCHEMA public TO mystic;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mystic;
