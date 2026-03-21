from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "skills"))

from skills_v2 import SkillCatalog


def test_skill_catalog_loads_backend_skills_config():
    catalog = SkillCatalog.from_yaml(Path("backend/app/ai/configs/skills.yaml"))
    entries = {entry.name: entry for entry in catalog.list()}

    assert "shell" in entries
    assert entries["shell"].module == "skills.shell"
    assert "shell:execute" in entries["shell"].scopes
