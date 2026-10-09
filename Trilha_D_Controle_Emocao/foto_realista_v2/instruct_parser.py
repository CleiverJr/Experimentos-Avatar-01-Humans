"""
Parser e codificador de instruções textuais para direcionamento de avatares.
Inspirado na arquitetura do InstructAvatar (AAAI 2025) e Sistema 2 do OmniHuman-1.5.
"""

import re
import numpy as np
from typing import Dict, Any, List


class InstructParser:
    """Mapeia linguagem natural para parâmetros de controle motor e vetores de condicionamento."""
    def __init__(self, embedding_dim: int = 16):
        self.embedding_dim = embedding_dim
        
        # Palavras-chave associadas a emoções primárias (substantivos, adjetivos e verbos)
        self.emotion_keywords = {
            "happy": ["feliz", "felizes", "alegre", "alegres", "alegria", "sorria", "sorrindo", "sorriso", "animado", "animada", "contente", "happy", "joy", "cheerful"],
            "sad": ["triste", "tristes", "tristeza", "melancólico", "melancólica", "chorando", "desanimado", "desanimada", "deprimido", "sad", "sorrow"],
            "angry": ["bravo", "brava", "irritado", "irritada", "raiva", "furioso", "furiosa", "fúria", "nervoso", "nervosa", "angry", "furious", "rage"],
            "surprised": ["surpreso", "surpresa", "surpreendente", "espantado", "espantada", "chocado", "chocada", "boquiaberto", "surprised", "shocked", "surprise"],
            "fear": ["medo", "assustado", "assustada", "apavorado", "apavorada", "temeroso", "pavor", "fear", "scared"],
            "disgusted": ["desgosto", "nojo", "enojado", "enojada", "repugnado", "repulsa", "disgust"],
            "skeptical": ["cético", "cética", "dúvida", "desconfiado", "desconfiada", "irônico", "irônica", "sarcástico", "sarcástica", "skeptical", "doubt"]
        }

        # Modificadores de intensidade (Português e Inglês)
        self.intensity_keywords = {
            "high": ["muito", "muita", "muitos", "muitas", "extremamente", "bastante", "intenso", "intensa", "intensamente", "forte", "demais", "super", "very", "extremely", "heavily", "intense", "high"],
            "low": ["pouco", "pouca", "poucos", "poucas", "leve", "levemente", "suave", "suavemente", "discreto", "discreta", "sutil", "contido", "contida", "lightly", "slightly", "softly", "gently", "subtle", "low"]
        }

        # Modificadores espaciais de pose de cabeça
        self.spatial_keywords = {
            "turn_left": ["esquerda", "vire a esquerda", "olhe para esquerda", "left"],
            "turn_right": ["direita", "vire a direita", "olhe para direita", "right"],
            "look_up": ["cima", "para cima", "olhe para cima", "up"],
            "look_down": ["baixo", "para baixo", "olhe para baixo", "down"],
            "nod": ["acenar", "concordando", "acene", "afirmativo", "nod"]
        }

    def parse_instruction(self, text: str) -> Dict[str, Any]:
        """
        Analisa uma instrução em texto e extrai:
        - Pesos de emoções
        - Fator de intensidade geral
        - Vieses de pose de cabeça (head_bias)
        - Vetor de condicionamento contínuo para o modelo de difusão
        """
        lower = text.lower()
        
        # 1. Detecção de emoções
        detected_emotions = {}
        for emo, words in self.emotion_keywords.items():
            matches = sum(1 for w in words if re.search(r'\b' + re.escape(w) + r'\b', lower))
            if matches > 0:
                detected_emotions[emo] = float(matches)
                
        if not detected_emotions:
            detected_emotions["neutral"] = 1.0

        # Normalização dos pesos de emoção
        total_w = sum(detected_emotions.values())
        emotion_weights = {k: v / total_w for k, v in detected_emotions.items()}

        # 2. Análise de intensidade
        intensity = 1.0
        for w in self.intensity_keywords["high"]:
            if w in lower:
                intensity = 1.5
                break
        for w in self.intensity_keywords["low"]:
            if w in lower:
                intensity = 0.6
                break

        # 3. Análise de vieses espaciais (Yaw, Pitch, Roll)
        head_bias = {"yaw_deg": 0.0, "pitch_deg": 0.0, "roll_deg": 0.0, "nodding": False}
        if any(w in lower for w in self.spatial_keywords["turn_left"]):
            head_bias["yaw_deg"] += 15.0
        if any(w in lower for w in self.spatial_keywords["turn_right"]):
            head_bias["yaw_deg"] -= 15.0
        if any(w in lower for w in self.spatial_keywords["look_up"]):
            head_bias["pitch_deg"] += 10.0
        if any(w in lower for w in self.spatial_keywords["look_down"]):
            head_bias["pitch_deg"] -= 10.0
        if any(w in lower for w in self.spatial_keywords["nod"]):
            head_bias["nodding"] = True

        # 4. Construção do vetor de condicionamento para o Denoiser [embedding_dim]
        cond_vector = self._build_conditioning_vector(emotion_weights, intensity, head_bias)

        return {
            "raw_instruction": text,
            "emotion_weights": emotion_weights,
            "intensity": intensity,
            "head_bias": head_bias,
            "conditioning_vector": cond_vector
        }

    def _build_conditioning_vector(self, emotion_weights: Dict[str, float], intensity: float, head_bias: Dict[str, Any]) -> np.ndarray:
        """Gera um vetor contínuo de 16 dimensões para guiar a difusão."""
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        
        # Dimensões 0 a 6: Emoções canônicas ponderadas pela intensidade
        canonical = ["happy", "sad", "angry", "surprised", "fear", "disgusted", "skeptical"]
        for i, emo in enumerate(canonical):
            if emo in emotion_weights:
                vec[i] = emotion_weights[emo] * intensity

        # Dimensões 7 a 9: Vieses espaciais normalizados
        vec[7] = np.clip(head_bias["yaw_deg"] / 30.0, -1.0, 1.0)
        vec[8] = np.clip(head_bias["pitch_deg"] / 30.0, -1.0, 1.0)
        vec[9] = 1.0 if head_bias.get("nodding") else 0.0

        # Dimensão 10: Intensidade geral normalizada
        vec[10] = intensity / 2.0

        # Dimensões 11 a 15: Hash determinístico de contexto de texto
        for idx in range(11, self.embedding_dim):
            vec[idx] = float(np.sin(sum(vec[:idx]) * 3.1415))

        return vec
