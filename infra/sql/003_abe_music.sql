-- Migration 003: ABE Music Inc schema
-- Artistas, catálogo musical, regalías, ABE Academy

BEGIN;

-- Artistas
CREATE TABLE IF NOT EXISTS artistas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    bio TEXT,
    genero VARCHAR(100) DEFAULT 'norteño',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'prospecto')),
    management_pct DECIMAL(5,2) DEFAULT 20.00,
    wallet_address VARCHAR(42),
    spotify_artist_id VARCHAR(50),
    tiktok_handle VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Canciones / catálogo
CREATE TABLE IF NOT EXISTS catalogo_musical (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artista_id UUID NOT NULL REFERENCES artistas(id) ON DELETE CASCADE,
    titulo VARCHAR(300) NOT NULL,
    isrc VARCHAR(15),
    album VARCHAR(300),
    duracion_seg INTEGER,
    bpm DECIMAL(6,2),
    lufs DECIMAL(6,2),
    fecha_lanzamiento DATE,
    plataformas JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Regalías
CREATE TABLE IF NOT EXISTS royalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artista_id UUID NOT NULL REFERENCES artistas(id) ON DELETE CASCADE,
    cancion_id UUID REFERENCES catalogo_musical(id),
    periodo VARCHAR(7) NOT NULL, -- YYYY-MM
    gross_revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    management_cut DECIMAL(12,2) NOT NULL DEFAULT 0,
    artista_net DECIMAL(12,2) NOT NULL DEFAULT 0,
    productor_cut DECIMAL(12,2) NOT NULL DEFAULT 0,
    academy_pool DECIMAL(12,2) NOT NULL DEFAULT 0,
    currency CHAR(3) DEFAULT 'MXN',
    fuente VARCHAR(50),
    pagado BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ABE Academy — Cursos
CREATE TABLE IF NOT EXISTS academy_cursos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    titulo VARCHAR(300) NOT NULL,
    descripcion TEXT,
    nivel VARCHAR(20) DEFAULT 'basico' CHECK (nivel IN ('basico', 'intermedio', 'avanzado')),
    duracion_horas INTEGER DEFAULT 10,
    precio_mxn DECIMAL(10,2) DEFAULT 0,
    certificado_soulbound BOOLEAN DEFAULT true,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ABE Academy — Inscripciones
CREATE TABLE IF NOT EXISTS academy_inscripciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curso_id UUID NOT NULL REFERENCES academy_cursos(id),
    student_email VARCHAR(255) NOT NULL,
    student_name VARCHAR(200),
    wallet_address VARCHAR(42),
    score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'in_progress', 'completed', 'failed')),
    nft_token_id BIGINT,
    nft_tx_hash VARCHAR(66),
    xp_earned INTEGER DEFAULT 0,
    mdx_earned INTEGER DEFAULT 0,
    inscrito_at TIMESTAMPTZ DEFAULT now(),
    completado_at TIMESTAMPTZ
);

-- MDX Points ledger (off-chain mirror)
CREATE TABLE IF NOT EXISTS mdx_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_address VARCHAR(42) NOT NULL,
    student_email VARCHAR(255),
    amount INTEGER NOT NULL,
    reason VARCHAR(200),
    tx_hash VARCHAR(66),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Contenido programado (social media)
CREATE TABLE IF NOT EXISTS contenido_programado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artista_id UUID REFERENCES artistas(id),
    tenant_id UUID REFERENCES tenants(id),
    plataforma VARCHAR(30) NOT NULL,
    tipo VARCHAR(30) DEFAULT 'post',
    titulo VARCHAR(300),
    body TEXT,
    media_url TEXT,
    hashtags TEXT[],
    scheduled_at TIMESTAMPTZ NOT NULL,
    published_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'published', 'failed')),
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_artistas_tenant ON artistas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_catalogo_artista ON catalogo_musical(artista_id);
CREATE INDEX IF NOT EXISTS idx_royalties_artista_periodo ON royalties(artista_id, periodo);
CREATE INDEX IF NOT EXISTS idx_academy_inscripciones_email ON academy_inscripciones(student_email);
CREATE INDEX IF NOT EXISTS idx_contenido_scheduled ON contenido_programado(scheduled_at, status);
CREATE INDEX IF NOT EXISTS idx_mdx_wallet ON mdx_ledger(wallet_address);

-- Datos iniciales — cursos ABE Academy
INSERT INTO academy_cursos (slug, titulo, nivel, duracion_horas, precio_mxn) VALUES
    ('produccion-norteña-basica', 'Producción Norteña Básica', 'basico', 12, 2500),
    ('mezcla-mastering-regional', 'Mezcla y Mastering Regional MX', 'intermedio', 20, 4500),
    ('acordeon-norteño', 'Acordeón Norteño desde Cero', 'basico', 15, 2000),
    ('marketing-artista-digital', 'Marketing Digital para Artistas', 'basico', 8, 1800),
    ('contratos-musica-mx', 'Contratos Musicales en México (Legal)', 'avanzado', 6, 3500),
    ('distribucion-streaming', 'Distribución en Streaming 2026', 'intermedio', 10, 2800)
ON CONFLICT (slug) DO NOTHING;

COMMIT;
