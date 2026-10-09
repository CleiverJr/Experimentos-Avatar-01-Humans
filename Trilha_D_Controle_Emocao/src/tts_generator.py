"""
Módulo de Síntese de Fala (TTS) para geração de áudio a partir de texto.
Utiliza o sintetizador nativo do macOS ('say') com fallback para o sintetizador acústico harmônico.
"""

import os
import subprocess
import soundfile as sf
import numpy as np
from typing import Optional, Tuple


class SpeechSynthesizer:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.available_macos_say = self._check_macos_say()
        self.default_pt_voice = self._find_portuguese_voice() if self.available_macos_say else None

    def _check_macos_say(self) -> bool:
        try:
            res = subprocess.run(["which", "say"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def _find_portuguese_voice(self) -> Optional[str]:
        try:
            res = subprocess.run(["say", "-v", "?"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in res.stdout.splitlines():
                if "pt_BR" in line:
                    voice_name = line.split()[0]
                    # Se tiver parênteses, pega o nome completo antes do código
                    return voice_name
            return None
        except Exception:
            return None

    def synthesize(self, text: str, output_wav_path: str, voice: Optional[str] = None) -> Tuple[np.ndarray, float]:
        """
        Sintetiza texto em áudio WAV mono a 16kHz.
        Retorna: (audio_samples, duration_seconds)
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)

        if self.available_macos_say:
            voice_arg = voice or self.default_pt_voice
            cmd = ["say"]
            if voice_arg:
                cmd.extend(["-v", voice_arg])
            cmd.extend(["-o", output_wav_path, "--data-format=LEI16@16000", text])

            try:
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0 and os.path.exists(output_wav_path):
                    data, sr = sf.read(output_wav_path)
                    if data.ndim > 1:
                        data = np.mean(data, axis=1)
                    duration = len(data) / self.sample_rate
                    return data.astype(np.float32), float(duration)
            except Exception as e:
                print(f"Aviso: Falha ao invocar 'say' ({e}). Usando sintetizador acústico fallback.")

        # Fallback: Síntese acústica sintética proporcional ao tamanho do texto
        word_count = max(1, len(text.split()))
        duration = max(2.0, word_count * 0.35)
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        f0 = 135.0 + 20.0 * np.sin(2 * np.pi * 1.8 * t)
        phase = 2 * np.pi * np.cumsum(f0) / self.sample_rate
        signal = np.sin(phase) + 0.4 * np.sin(2 * phase)
        env = np.clip(0.6 * np.sin(2 * np.pi * (word_count / duration) * t), 0, 1)
        data = (signal * env).astype(np.float32)
        sf.write(output_wav_path, data, self.sample_rate)
        return data, float(duration)
