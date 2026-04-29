"""
Task Validator API — validates ABE Academy student submissions
Endpoints: /validate/audio, /validate/video (delegates to safety-validator)
"""
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from validators.audio import AudioValidator

app = FastAPI(title="Task Validator", version="1.0.0")


@app.post("/validate/audio")
async def validate_audio(
    file: UploadFile = File(...),
    check_bpm: bool = Form(True),
    check_mastering: bool = Form(True),
    check_hihat: bool = Form(False),
    min_bpm: float = Form(100.0),
    max_bpm: float = Form(120.0),
):
    if not file.content_type or "audio" not in file.content_type:
        raise HTTPException(400, "Solo archivos de audio")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        results = {}
        passed_all = True
        if check_bpm:
            r = AudioValidator.validate_bpm(tmp_path, min_bpm, max_bpm)
            results["bpm"] = r
            if not r.get("passed"):
                passed_all = False
        if check_mastering:
            r = AudioValidator.validate_mastering(tmp_path)
            results["mastering"] = r
            if not r.get("passed"):
                passed_all = False
        if check_hihat:
            r = AudioValidator.detect_hihat(tmp_path)
            results["hihat"] = r
            if not r.get("detected"):
                passed_all = False
        xp = 100 if passed_all else 25
        mdx = 10 if passed_all else 2
        return {"passed": passed_all, "checks": results, "rewards": {"xp": xp, "mdx_points": mdx}}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "task-validator"}
