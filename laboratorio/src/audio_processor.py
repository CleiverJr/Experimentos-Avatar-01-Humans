"""
Processador acústico para extração de representações de áudio (prosódia, mel-espectrogramas e energia).
Compatível com as entradas dos modelos VASA-1, Audio2Photoreal e AUHead.
"""

import math
import numpy as np
import scipy.signal
import soundfile as sf
from typing import Dict, Tuple, Optional


class AudioProcessor:
    def __init__(self, sample_rate: int = 16000, n_mels: int = 80, fps: float = 30.0):
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.fps = fps
        self.hop_length = int(sample_rate / fps)
        self.n_fft = 1024

    def load_audio(self, file_path: str) -> np.ndarray:
        """Carrega arquivo WAV e converte para mono e taxa alvo (16kHz)."""
        data, sr = sf.read(file_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1)  # Estéreo para Mono
        if sr != self.sample_rate:
            num_samples = int(len(data) * self.sample_rate / sr)
            data = scipy.signal.resample(data, num_samples)
        # Normalização de amplitude
        max_val = np.max(np.abs(data)) + 1e-8
        return (data / max_val).astype(np.float32)

    def generate_synthetic_speech(self, duration_sec: float = 3.0, base_f0: float = 130.0) -> np.ndarray:
        """Gera sinal harmônico com modulação de formantes e pausas simulando fala humana."""
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        # Pitch variável (entonação prosódica)
        f0_curve = base_f0 + 25.0 * np.sin(2 * np.pi * 1.5 * t) + 10.0 * np.sin(2 * np.pi * 3.7 * t)
        phase = 2 * np.pi * np.cumsum(f0_curve) / self.sample_rate
        
        # Som harmônico (cordas vocais)
        signal = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase) + 0.15 * np.sin(4 * phase)
        
        # Envelope de palavras e pausas (cadência de fala natural)
        envelope = np.clip(0.6 * np.sin(2 * np.pi * 2.2 * t) + 0.4 * np.sin(2 * np.pi * 0.8 * t), 0, 1)
        # Adicionar ruído de fricativas e consoantes
        noise = np.random.normal(0, 0.05, len(t))
        speech = (signal * envelope + noise * (envelope > 0.1)).astype(np.float32)
        max_val = np.max(np.abs(speech)) + 1e-8
        return speech / max_val

    def extract_features(self, audio_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extrai características sincronizadas por frame visual (30 FPS):
        - Log-Mel Spectrogram (80 bins)
        - Energy RMS (Envelope de volume)
        - Pitch aproximado (F0)
        """
        num_frames = max(1, int(len(audio_data) / self.hop_length))
        mel_features = []
        energy_features = []
        pitch_features = []

        # Banco de filtros Mel triangular aproximado
        mel_filters = self._create_mel_filterbank(self.n_mels, self.n_fft, self.sample_rate)

        window = np.hanning(self.n_fft)

        for i in range(num_frames):
            start = i * self.hop_length
            end = start + self.n_fft
            
            if end <= len(audio_data):
                frame = audio_data[start:end] * window
            else:
                frame = np.pad(audio_data[start:], (0, max(0, end - len(audio_data)))) * window

            # Espectrograma de potência
            fft_mag = np.abs(np.fft.rfft(frame)) ** 2
            mel_spectrum = np.dot(mel_filters, fft_mag)
            log_mel = np.log(np.maximum(mel_spectrum, 1e-6))
            mel_features.append(log_mel)

            # Energia RMS do frame
            rms = np.sqrt(np.mean(frame**2) + 1e-8)
            energy_features.append(rms)

            # Estimativa de Pitch F0 via autocorrelação
            f0 = self._estimate_f0(frame)
            pitch_features.append(f0)

        mel_array = np.array(mel_features, dtype=np.float32)  # [T, n_mels]
        energy_array = np.array(energy_features, dtype=np.float32)  # [T]
        pitch_array = np.array(pitch_features, dtype=np.float32)    # [T]

        return {
            "mel_spectrogram": mel_array,
            "energy_rms": energy_array,
            "pitch_f0": pitch_array,
            "num_frames": num_frames,
            "duration_sec": len(audio_data) / self.sample_rate
        }

    def _create_mel_filterbank(self, n_mels: int, n_fft: int, sample_rate: int) -> np.ndarray:
        """Constrói matriz de filtros Mel triangulares."""
        def hz_to_mel(hz):
            return 2595.0 * np.log10(1.0 + hz / 700.0)

        def mel_to_hz(mel):
            return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

        low_mel = hz_to_mel(80.0)
        high_mel = hz_to_mel(sample_rate / 2.0)
        mel_points = np.linspace(low_mel, high_mel, n_mels + 2)
        hz_points = mel_to_hz(mel_points)
        bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

        num_fft_bins = n_fft // 2 + 1
        filterbank = np.zeros((n_mels, num_fft_bins), dtype=np.float32)

        for m in range(1, n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            for k in range(f_m_minus, f_m):
                if k < num_fft_bins and (f_m - f_m_minus) > 0:
                    filterbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                if k < num_fft_bins and (f_m_plus - f_m) > 0:
                    filterbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

        return filterbank

    def _estimate_f0(self, frame: np.ndarray) -> float:
        """Calcula F0 aproximado usando autocorrelação normalizada."""
        corr = np.correlate(frame, frame, mode='full')
        corr = corr[len(corr)//2:]
        dcorr = np.diff(corr)
        start_indices = np.where(dcorr > 0)[0]
        if len(start_indices) == 0:
            return 0.0
        start = start_indices[0]
        peak = np.argmax(corr[start:]) + start
        if peak == 0:
            return 0.0
        f0 = self.sample_rate / peak
        if 60.0 <= f0 <= 500.0:
            return float(f0)
        return 0.0
