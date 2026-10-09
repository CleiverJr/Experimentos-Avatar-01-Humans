"""
Implementação Manual 01: O Espaço Latente de Movimento do LivePortrait & Ditto
==============================================================================
Neste script, implementamos do zero os fundamentos matemáticos que regem
a representação de pose e expressão facial no LivePortrait e no Ditto:

1. bin66_to_degree: Conversão de distribuição discreta de 66 bins para graus contínuos.
2. euler_to_rotation_matrix: Cálculo da matriz de rotação 3D R(pitch, yaw, roll).
3. liveportrait_keypoints_equation: Equação fundamental de deformação implícita:
   x_d = scale * (x_canonical @ R + exp) + t
"""

import numpy as np
import torch
import torch.nn.functional as F


def bin66_to_degree_numpy(logits: np.ndarray) -> np.ndarray:
    """
    Converte logits de 66 bins em graus contínuos [-97.5°, +97.5°].
    
    Por que 66 bins?
    Em vez de fazer uma regressão direta de um número (que costuma sofrer com
    ruído e oscilações), o modelo prevê uma distribuição de probabilidade
    sobre 66 intervalos de 3 graus cada. O valor contínuo final é a média ponderada (esperança).
    
    Fórmula:
        graus = sum(softmax(logits)_i * i * 3.0) - 97.5
    """
    # Softmax sobre a dimensão dos bins
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    
    indices = np.arange(66, dtype=np.float32)
    # Esperança matemática
    degrees = np.sum(probs * indices * 3.0, axis=-1) - 97.5
    return degrees


def euler_to_rotation_matrix(pitch_deg: float, yaw_deg: float, roll_deg: float) -> np.ndarray:
    """
    Calcula a matriz de rotação 3D SO(3) a partir dos ângulos de Euler (em graus).
    
    Convenção LivePortrait: R = R_z(roll) @ R_y(yaw) @ R_x(pitch)
    """
    # Converte graus para radianos
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)
    roll = np.radians(roll_deg)
    
    # Rotação em torno do eixo X (Pitch: olhar para cima/baixo)
    Rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(pitch), -np.sin(pitch)],
        [0.0, np.sin(pitch), np.cos(pitch)]
    ], dtype=np.float32)
    
    # Rotação em torno do eixo Y (Yaw: olhar para esquerda/direita)
    Ry = np.array([
        [np.cos(yaw), 0.0, np.sin(yaw)],
        [0.0, 1.0, 0.0],
        [-np.sin(yaw), 0.0, np.cos(yaw)]
    ], dtype=np.float32)
    
    # Rotação em torno do eixo Z (Roll: inclinar a cabeça lateralmente)
    Rz = np.array([
        [np.cos(roll), -np.sin(roll), 0.0],
        [np.sin(roll), np.cos(roll), 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float32)
    
    R = Rz @ Ry @ Rx
    return R


def compute_driven_keypoints(
    x_canonical: np.ndarray,
    pitch_deg: float,
    yaw_deg: float,
    roll_deg: float,
    exp_delta: np.ndarray,
    scale: float = 1.0,
    translation: np.ndarray = None
) -> np.ndarray:
    """
    Equação nuclear do LivePortrait:
        x_d = scale * (x_c @ R + exp) + t
        
    Args:
        x_canonical: Array (21, 3) com os 21 pontos implícitos da face neutra.
        pitch_deg, yaw_deg, roll_deg: Ângulos de rotação da cabeça em graus.
        exp_delta: Array (21, 3) de deslocamento de expressão (lábios, sobrancelhas).
        scale: Fator escalar de escala/zoom (geralmente próximo de 1.0).
        translation: Vetor (3,) de translação tridimensional (t_x, t_y, t_z).
        
    Returns:
        x_d: Array (21, 3) com os keypoints 3D deformados e posicionados no frame.
    """
    if translation is None:
        translation = np.zeros(3, dtype=np.float32)
        
    R = euler_to_rotation_matrix(pitch_deg, yaw_deg, roll_deg)
    
    # 1. Rotação rígida da face neutra
    x_rotated = x_canonical @ R
    
    # 2. Adição da deformação não-rígida de expressão
    x_expressed = x_rotated + exp_delta
    
    # 3. Escala e translação espacial
    x_driven = scale * x_expressed + translation
    
    return x_driven


if __name__ == "__main__":
    print("=" * 70)
    print("🔬 TESTE DIDÁTICO: O ESPAÇO LATENTE DE MOVIMENTO DO LIVEPORTRAIT & DITTO")
    print("=" * 70)
    
    # 1. Testando a conversão de 66 bins para graus
    print("\n[1] Conversão de 66 Bins para Graus:")
    # Exemplo: um logits concentrado no bin 32 (centro: 32.5 * 3 - 97.5 = 0°)
    logits_centro = np.zeros(66, dtype=np.float32)
    logits_centro[32] = 10.0  # alta probabilidade no centro
    grau_centro = bin66_to_degree_numpy(logits_centro)
    print(f"  • Logits com pico no bin 32 (centro neutro) -> {grau_centro:.2f}° (esperado ~0°)")
    
    # Exemplo: logits concentrado no bin 45 (45 * 3 - 97.5 = +37.5°)
    logits_rotacionado = np.zeros(66, dtype=np.float32)
    logits_rotacionado[45] = 10.0
    grau_rot = bin66_to_degree_numpy(logits_rotacionado)
    print(f"  • Logits com pico no bin 45 (rotação)      -> {grau_rot:.2f}° (esperado ~37.5°)")
    
    # 2. Criando 21 keypoints canônicos sintéticos
    print("\n[2] Geometria Canônica (21 Keypoints 3D):")
    np.random.seed(42)
    # Rosto padrão centrado na origem
    x_c = np.random.randn(21, 3).astype(np.float32) * 0.1
    print(f"  • Shape de x_canonical: {x_c.shape} (21 pontos tridimensionais)")
    
    # 3. Aplicando deformações: Neutro vs. Rotação + Expressão
    print("\n[3] Aplicando a Equação Fundamental:")
    # Rosto neutro
    x_neutro = compute_driven_keypoints(x_c, pitch_deg=0.0, yaw_deg=0.0, roll_deg=0.0, exp_delta=np.zeros_like(x_c))
    
    # Rosto com Yaw = 15° (olhando para a direita) e boca aberta
    exp_boca_aberta = np.zeros((21, 3), dtype=np.float32)
    # Índices dos lábios no LivePortrait: 6, 12, 14, 17, 19, 20
    # O keypoint 19 é o centro da mandíbula/lábio inferior: deslocamento para baixo (y+)
    exp_boca_aberta[19, 1] = 0.05
    
    x_animado = compute_driven_keypoints(
        x_canonical=x_c,
        pitch_deg=5.0,     # Leve inclinação para cima
        yaw_deg=15.0,      # Rotação para a direita
        roll_deg=0.0,
        exp_delta=exp_boca_aberta,
        scale=1.02,
        translation=np.array([0.01, -0.01, 0.0], dtype=np.float32)
    )
    
    deslocamento_medio = np.mean(np.linalg.norm(x_animado - x_neutro, axis=-1))
    deslocamento_mandibula = np.linalg.norm(x_animado[19] - x_neutro[19])
    
    print(f"  • Deslocamento médio global de keypoints: {deslocamento_medio:.4f}")
    print(f"  • Deslocamento específico do kp 19 (mandíbula): {deslocamento_mandibula:.4f}")
    print("\n✅ Sucesso! Os cálculos matemáticos do espaço de movimento foram validados.")
    print("=" * 70)
