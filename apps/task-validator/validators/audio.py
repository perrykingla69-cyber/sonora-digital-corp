"""
Audio Validator — BPM, mastering (LUFS), hi-hat detection for ABE Academy tasks
"""
import os
from typing import Dict


class AudioValidator:

    @staticmethod
    def validate_bpm(file_path: str, min_bpm: float = 100.0, max_bpm: float = 120.0) -> Dict:
        try:
            import librosa
            y, sr = librosa.load(file_path, duration=60)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if hasattr(tempo, '__iter__') else float(tempo)
            passed = min_bpm <= bpm <= max_bpm
            return {"passed": passed, "bpm": round(bpm, 1), "range": [min_bpm, max_bpm], "message": f"BPM: {bpm:.1f}" + (" ✅" if passed else f" ❌ (fuera de {min_bpm}-{max_bpm})")}
        except ImportError:
            return {"passed": False, "bpm": None, "error": "librosa no instalado"}
        except Exception as e:
            return {"passed": False, "bpm": None, "error": str(e)}

    @staticmethod
    def validate_mastering(file_path: str, target_lufs: float = -14.0, lufs_tolerance: float = 2.0, true_peak_max: float = -1.0) -> Dict:
        try:
            import pyloudnorm as pyln
            import soundfile as sf
            data, rate = sf.read(file_path)
            meter = pyln.Meter(rate)
            loudness = meter.integrated_loudness(data)
            lufs_ok = abs(loudness - target_lufs) <= lufs_tolerance
            peak = float(data.max())
            import math
            true_peak_db = 20 * math.log10(max(abs(peak), 1e-9))
            peak_ok = true_peak_db <= true_peak_max
            passed = lufs_ok and peak_ok
            return {
                "passed": passed,
                "lufs": round(loudness, 2),
                "true_peak_db": round(true_peak_db, 2),
                "lufs_ok": lufs_ok,
                "peak_ok": peak_ok,
                "message": "✅ Mastering correcto" if passed else f"❌ LUFS: {loudness:.1f} (target {target_lufs}±{lufs_tolerance}), Peak: {true_peak_db:.1f}dBTP",
            }
        except ImportError:
            return {"passed": False, "lufs": None, "error": "pyloudnorm/soundfile no instalado"}
        except Exception as e:
            return {"passed": False, "lufs": None, "error": str(e)}

    @staticmethod
    def detect_hihat(file_path: str, threshold_percent: float = 5.0) -> Dict:
        try:
            import librosa
            import numpy as np
            y, sr = librosa.load(file_path, duration=30)
            stft = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            hihat_mask = freqs > 8000
            hihat_energy = stft[hihat_mask].mean()
            total_energy = stft.mean()
            pct = (hihat_energy / max(total_energy, 1e-9)) * 100
            detected = pct >= threshold_percent
            return {"detected": detected, "hihat_percent": round(pct, 2), "threshold": threshold_percent, "message": f"Hi-hat: {pct:.1f}% {'✅' if detected else '❌ (insuficiente)'}"}
        except ImportError:
            return {"detected": False, "hihat_percent": None, "error": "librosa no instalado"}
        except Exception as e:
            return {"detected": False, "hihat_percent": None, "error": str(e)}
