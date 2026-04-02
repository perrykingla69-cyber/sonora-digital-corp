-- ========== ROW LEVEL SECURITY ==========

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Política para usuarios
CREATE POLICY user_tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Política para audit log
CREATE POLICY audit_tenant_isolation ON audit_log
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- ========== FUNCIÓN PARA MULTI-TENANCY ==========

CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- ========== VISTAS POR TENANT ==========

CREATE OR REPLACE VIEW tenant_users AS
    SELECT * FROM users 
    WHERE tenant_id = current_setting('app.current_tenant_id')::uuid;

CREATE OR REPLACE VIEW tenant_audit AS
    SELECT * FROM audit_log
    WHERE tenant_id = current_setting('app.current_tenant_id')::uuid;
