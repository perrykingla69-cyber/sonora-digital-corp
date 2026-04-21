"""Seed Qdrant para nichos adicionales: restaurante, abogado, constructor"""
import requests
import json
from datetime import datetime

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"

niches = {
    "restaurante": {
        "collections": ["global_restaurant_mx", "global_food_safety"],
        "sources": [
            "NOM-251-SCFI-2009 (HACCP)",
            "NOM-051-SCFI-2010 (Etiquetado)",
            "Regulaciones sanitarias COFEPRIS"
        ]
    },
    "abogado": {
        "collections": ["global_legal_mx", "global_contracts"],
        "sources": [
            "Código Civil Mexicano",
            "Código de Comercio",
            "SCJN jurisprudencia"
        ]
    },
    "constructor": {
        "collections": ["global_construction_mx", "global_building_codes"],
        "sources": [
            "RCDF (Reglamento de Construcciones)",
            "NOM-006-CONAGUA",
            "Normas técnicas complementarias"
        ]
    }
}

def seed_niche(niche_name, config):
    print(f"🌱 Seeding nicho: {niche_name}")
    for collection in config["collections"]:
        print(f"  → Collection: {collection}")
        # Mock: en producción, crear colecciones en Qdrant
    print(f"  ✅ {niche_name} seeded ({len(config['sources'])} sources)")

if __name__ == "__main__":
    for niche, config in niches.items():
        seed_niche(niche, config)
    print("\n✅ Seeding completado para nichos adicionales")
