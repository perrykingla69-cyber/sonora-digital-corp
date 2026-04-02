"""
NICHE REGISTRY — El mapa de conocimiento por giro
MYSTIC usa esto para auto-seed cuando llega un cliente nuevo.
Nunca manual. Siempre automático.
"""

NICHE_REGISTRY = {

    # ── ALIMENTOS Y BEBIDAS ──────────────────────────────────
    "pastelero": {
        "keywords": ["repostería", "pastelería", "panadería", "postres", "dulces"],
        "collections": ["global_alimentos", "global_fiscal_mx"],
        "sources": [
            {"type": "nom", "id": "NOM-251-SSA1-2009", "topic": "Buenas Prácticas de Manufactura"},
            {"type": "nom", "id": "NOM-086-SSA1-1994", "topic": "Etiquetado productos azúcares"},
            {"type": "url", "url": "https://www.cofepris.gob.mx/regulacion/paginas/alimentos.aspx"},
            {"type": "rss", "url": "https://www.dof.gob.mx/rss.php", "filter": "alimentos"},
        ],
        "update_cron": "0 6 * * 1",  # Lunes 6am
    },

    "restaurante": {
        "keywords": ["restaurante", "cocina", "comida", "taquería", "fonda", "cafetería"],
        "collections": ["global_alimentos", "global_fiscal_mx", "global_legal_mx"],
        "sources": [
            {"type": "nom", "id": "NOM-251-SSA1-2009", "topic": "BPM restaurantes"},
            {"type": "url", "url": "https://www.cofepris.gob.mx"},
            {"type": "pdf", "url": "https://www.impi.gob.mx/marcas", "topic": "registro marca"},
            {"type": "url", "url": "https://www.sat.gob.mx/consultas/operaciones/facturacion"},
        ],
        "update_cron": "0 6 * * 1",
    },

    "proveedor_alimentos": {
        "keywords": ["proveedor", "distribuidor", "mayorista", "importador alimentos"],
        "collections": ["global_alimentos", "global_fiscal_mx", "global_aduanas"],
        "sources": [
            {"type": "url", "url": "https://www.sat.gob.mx/tramites/padron-importadores"},
            {"type": "nom", "id": "NOM-194-SSA1-2004", "topic": "especificaciones sanitarias"},
        ],
        "update_cron": "0 6 * * 1",
    },

    # ── SERVICIOS PROFESIONALES ──────────────────────────────
    "contador": {
        "keywords": ["contador", "contabilidad", "fiscal", "despacho contable", "CPA"],
        "collections": ["global_fiscal_mx", "global_legal_mx"],
        "sources": [
            {"type": "url", "url": "https://www.sat.gob.mx/informacion_fiscal/legislacion_tributaria"},
            {"type": "url", "url": "https://www.dof.gob.mx", "filter": "fiscal SAT CFF ISR IVA"},
            {"type": "pdf", "url": "https://www.sat.gob.mx/cs/Satellite?blobcol=urldata&blobkey=id&blobtable=MungoBlobs&blobwhere=1461173671738", "topic": "CFF 2025"},
            {"type": "rss", "url": "https://www.sat.gob.mx/rss/noticias.xml"},
        ],
        "update_cron": "0 5 * * *",  # Diario 5am (alta frecuencia por cambios SAT)
    },

    "abogado": {
        "keywords": ["abogado", "despacho jurídico", "legal", "asesoría legal", "notaría"],
        "collections": ["global_legal_mx", "global_fiscal_mx"],
        "sources": [
            {"type": "rss", "url": "https://www.dof.gob.mx/rss.php"},
            {"type": "url", "url": "https://www.scjn.gob.mx/jurisprudencias"},
            {"type": "url", "url": "https://www.diputados.gob.mx/LeyesBiblio/"},
        ],
        "update_cron": "0 6 * * *",
    },

    # ── SEGURIDAD Y EMERGENCIAS ──────────────────────────────
    "bombero": {
        "keywords": ["bombero", "protección civil", "emergencias", "rescate", "CENAPRED"],
        "collections": ["global_seguridad", "global_legal_mx"],
        "sources": [
            {"type": "nom", "id": "NOM-002-STPS-2010", "topic": "Condiciones seguridad prevención incendios"},
            {"type": "nom", "id": "NOM-003-SEGOB-2011", "topic": "Señales y avisos protección civil"},
            {"type": "url", "url": "https://www.cenapred.unam.mx"},
            {"type": "url", "url": "https://www.proteccioncivil.cdmx.gob.mx"},
            {"type": "rss", "url": "https://www.dof.gob.mx/rss.php", "filter": "protección civil STPS"},
        ],
        "update_cron": "0 6 * * 1",
    },

    # ── SALUD ────────────────────────────────────────────────
    "medico": {
        "keywords": ["médico", "clínica", "consultorio", "salud", "hospital", "IMSS"],
        "collections": ["global_salud", "global_fiscal_mx", "global_legal_mx"],
        "sources": [
            {"type": "url", "url": "https://www.cofepris.gob.mx/as/paginas/establecimientos-de-salud.aspx"},
            {"type": "url", "url": "https://www.gob.mx/salud/normasoficiales"},
            {"type": "rss", "url": "https://www.dof.gob.mx/rss.php", "filter": "NOM salud COFEPRIS"},
        ],
        "update_cron": "0 6 * * 1",
    },

    # ── CONSTRUCCIÓN ─────────────────────────────────────────
    "constructor": {
        "keywords": ["constructor", "obra", "arquitecto", "inmobiliaria", "desarrollador"],
        "collections": ["global_construccion", "global_fiscal_mx"],
        "sources": [
            {"type": "url", "url": "https://www.gob.mx/conavi"},
            {"type": "nom", "id": "NMX-C-", "topic": "normas construcción materiales"},
            {"type": "url", "url": "https://www.sat.gob.mx/operacion/49066/sector-inmobiliario"},
        ],
        "update_cron": "0 6 * * 1",
    },

    # ── FALLBACK: nicho desconocido ───────────────────────────
    "general": {
        "keywords": [],
        "collections": ["global_fiscal_mx", "global_legal_mx"],
        "sources": [
            {"type": "url", "url": "https://www.sat.gob.mx"},
            {"type": "rss", "url": "https://www.dof.gob.mx/rss.php"},
        ],
        "update_cron": "0 6 * * 1",
        "note": "MYSTIC propone nuevo nicho específico basado en conversaciones",
    },
}


def classify_niche(business_description: str) -> str:
    """
    Clasifica el giro del negocio.
    MYSTIC llama esto en el onboarding.
    Si no encuentra match → 'general' + MYSTIC hace deep discovery.
    """
    desc_lower = business_description.lower()
    for niche, config in NICHE_REGISTRY.items():
        if niche == "general":
            continue
        for keyword in config["keywords"]:
            if keyword in desc_lower:
                return niche
    return "general"


def get_niche_sources(niche: str) -> dict:
    return NICHE_REGISTRY.get(niche, NICHE_REGISTRY["general"])
