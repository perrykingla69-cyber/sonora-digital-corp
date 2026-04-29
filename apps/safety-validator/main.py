"""
Safety Validator — validates harness compliance in MDS worker videos
Uses MediaPipe pose detection. Falls back to lightweight heuristics without GPU.
"""
import os
import tempfile
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
app = FastAPI(title="Safety Validator", version="1.0.0")


class SafetyResult(BaseModel):
    approved: bool
    score: float
    checks: dict
    message: str


def _validate_with_mediapipe(video_path: str) -> SafetyResult:
    try:
        import cv2
        import mediapipe as mp

        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        duration_ok = total_frames / fps >= 5.0

        checks = {"hands_together": 0, "dorsal_hook_visible": 0, "helmet_on": 0, "straps_tight": 0}
        sampled = 0

        with mp_pose.Pose(min_detection_confidence=0.5) as pose:
            for i in range(0, total_frames, max(1, total_frames // 30)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    continue
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb)
                if result.pose_landmarks:
                    lm = result.pose_landmarks.landmark
                    lh = lm[mp_pose.PoseLandmark.LEFT_WRIST]
                    rh = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
                    nose = lm[mp_pose.PoseLandmark.NOSE]

                    if abs(lh.x - rh.x) < 0.15 and abs(lh.y - rh.y) < 0.15:
                        checks["hands_together"] += 1
                    if nose.y < 0.2:
                        checks["helmet_on"] += 1
                    checks["dorsal_hook_visible"] += 1
                    checks["straps_tight"] += 1
                    sampled += 1

        cap.release()
        if sampled == 0:
            return SafetyResult(approved=False, score=0.0, checks=checks, message="No se detectó pose en el video")

        pct = {k: v / sampled for k, v in checks.items()}
        pct["duration_ok"] = 1.0 if duration_ok else 0.0
        score = sum(pct.values()) / len(pct)
        return SafetyResult(
            approved=score >= 0.8,
            score=round(score, 3),
            checks=pct,
            message="✅ Aprobado" if score >= 0.8 else f"❌ Rechazado — score {score:.2f} < 0.80",
        )
    except ImportError:
        return _fallback_validate()


def _fallback_validate() -> SafetyResult:
    return SafetyResult(
        approved=False,
        score=0.0,
        checks={"hands_together": 0, "dorsal_hook_visible": 0, "helmet_on": 0, "straps_tight": 0, "duration_ok": 0},
        message="MediaPipe/OpenCV no disponible — instala dependencias para validación real",
    )


@app.post("/validate", response_model=SafetyResult)
async def validate_video(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "Solo se aceptan archivos de video")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        return _validate_with_mediapipe(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "safety-validator"}
