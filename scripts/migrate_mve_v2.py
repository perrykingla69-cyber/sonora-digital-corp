"""
Migración MVE v2 — Agrega columnas nuevas a tabla mves
Ejecutar en VPS: python scripts/migrate_mve_v2.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import engine
from sqlalchemy import text

COLUMNAS = [
    # Proveedor
    ("proveedor_nombre",         "VARCHAR",   "''"),
    ("proveedor_pais",           "VARCHAR",   "NULL"),
    ("proveedor_tax_id",         "VARCHAR",   "NULL"),
    ("proveedor_direccion",      "TEXT",      "NULL"),
    # Factura
    ("numero_factura",           "VARCHAR",   "NULL"),
    ("fecha_factura",            "TIMESTAMPTZ","NULL"),
    ("descripcion_mercancias",   "TEXT",      "NULL"),
    ("fraccion_arancelaria",     "VARCHAR",   "NULL"),
    ("cantidad",                 "FLOAT",     "1.0"),
    ("unidad_medida",            "VARCHAR",   "NULL"),
    # Valores
    ("incoterm",                 "VARCHAR",   "NULL"),
    ("valor_factura",            "FLOAT",     "0.0"),
    ("valor_factura_mxn",        "FLOAT",     "0.0"),
    ("flete",                    "FLOAT",     "0.0"),
    ("seguro",                   "FLOAT",     "0.0"),
    ("otros_cargos",             "FLOAT",     "0.0"),
    ("descuentos",               "FLOAT",     "0.0"),
    ("regalias",                 "FLOAT",     "0.0"),
    ("asistencias",              "FLOAT",     "0.0"),
    ("valor_en_aduana",          "FLOAT",     "0.0"),
    # Contribuciones
    ("tasa_igi",                 "FLOAT",     "0.0"),
    ("igi",                      "FLOAT",     "0.0"),
    # Método valoración
    ("metodo_valoracion",        "INTEGER",   "1"),
    ("justificacion_metodo",     "TEXT",      "NULL"),
    ("hay_vinculacion",          "BOOLEAN",   "FALSE"),
    ("justificacion_vinculacion","TEXT",      "NULL"),
    # Semáforo
    ("semaforo",                 "VARCHAR",   "NULL"),
    ("semaforo_errores",         "JSONB",     "NULL"),
    ("semaforo_validado_at",     "TIMESTAMPTZ","NULL"),
    # Estado
    ("pedimento_numero",         "VARCHAR",   "NULL"),
    ("notas",                    "TEXT",      "NULL"),
    ("updated_at",               "TIMESTAMPTZ","NOW()"),
]

def migrar():
    with engine.connect() as conn:
        # Obtener columnas existentes
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='mves'"
        ))
        existentes = {row[0] for row in result}
        print(f"Columnas actuales: {len(existentes)}")

        agregadas = 0
        for col, tipo, default in COLUMNAS:
            if col not in existentes:
                default_clause = f"DEFAULT {default}" if default != "NULL" else ""
                sql = f"ALTER TABLE mves ADD COLUMN IF NOT EXISTS {col} {tipo} {default_clause}"
                conn.execute(text(sql))
                print(f"  ✓ Agregada: {col} {tipo}")
                agregadas += 1
            else:
                print(f"  · Ya existe: {col}")

        conn.commit()
        print(f"\nMigración completa. {agregadas} columna(s) agregada(s).")

if __name__ == "__main__":
    migrar()
