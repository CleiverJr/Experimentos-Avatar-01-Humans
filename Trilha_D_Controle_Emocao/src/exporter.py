"""
Exportador de trajetórias de movimento para as Trilhas B (Arthur - FLAME) e C (Fernando - 3DGS).
Gera arquivos em formato JSON estruturado e matrizes binárias compactadas (.npz).
"""

import json
import numpy as np
from typing import Dict, List, Any


class MotionExporter:
    def __init__(self, fps: float = 30.0):
        self.fps = fps

    @staticmethod
    def euler_to_rotation_matrix(pitch_deg: float, yaw_deg: float, roll_deg: float) -> np.ndarray:
        """Converte ângulos de Euler (graus) para matriz de rotação 3x3 (ordem ZYX)."""
        p = np.radians(pitch_deg)
        y = np.radians(yaw_deg)
        r = np.radians(roll_deg)

        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(p), -np.sin(p)],
            [0, np.sin(p), np.cos(p)]
        ])
        Ry = np.array([
            [np.cos(y), 0, np.sin(y)],
            [0, 1, 0],
            [-np.sin(y), 0, np.cos(y)]
        ])
        Rz = np.array([
            [np.cos(r), -np.sin(r), 0],
            [np.sin(r), np.cos(r), 0],
            [0, 0, 1]
        ])
        return np.dot(Rz, np.dot(Ry, Rx))

    @staticmethod
    def rotation_matrix_to_6d(R: np.ndarray) -> np.ndarray:
        """Converte matriz 3x3 para representação contínua 6D (Zhou et al., CVPR 2019)."""
        # Primeiras duas colunas da matriz de rotação
        col1 = R[:, 0]
        col2 = R[:, 1]
        return np.concatenate([col1, col2]).astype(np.float32)

    def assemble_animation_package(self,
                                   head_trajectories: np.ndarray,
                                   au_trajectories: np.ndarray,
                                   flame_trajectories: List[Dict[str, np.ndarray]],
                                   metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        head_trajectories: [T, 6] (pitch, yaw, roll, tx, ty, tz)
        au_trajectories: [T, num_aus]
        flame_trajectories: Lista de dicionários com expression_coefficients e jaw_rotation
        """
        T = head_trajectories.shape[0]
        frames_list = []

        for t in range(T):
            pitch, yaw, roll, tx, ty, tz = head_trajectories[t]
            R = self.euler_to_rotation_matrix(pitch, yaw, roll)
            rot_6d = self.rotation_matrix_to_6d(R)

            flame_data = flame_trajectories[t]

            frame_entry = {
                "frame_idx": t,
                "timestamp": round(t / self.fps, 4),
                "head_pose": {
                    "rotation_euler_deg": [round(float(pitch), 3), round(float(yaw), 3), round(float(roll), 3)],
                    "rotation_6d": [round(float(v), 5) for v in rot_6d],
                    "translation_cam": [round(float(tx), 4), round(float(ty), 4), round(float(tz), 4)]
                },
                "facs_action_units": {
                    f"AU_{idx:02d}": round(float(val), 4) for idx, val in enumerate(au_trajectories[t])
                },
                "flame_parameters": {
                    "expression_coefficients": [round(float(v), 4) for v in flame_data["expression_coefficients"]],
                    "jaw_rotation_axis_angle": [round(float(v), 4) for v in flame_data["jaw_rotation"]],
                    "eyeballs_rotation": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }
            frames_list.append(frame_entry)

        package = {
            "version": "1.0.0",
            "metadata": metadata,
            "fps": self.fps,
            "total_frames": T,
            "duration_seconds": round(T / self.fps, 3),
            "frames": frames_list
        }
        return package

    def save_json(self, package: Dict[str, Any], output_path: str):
        """Salva pacote legível em JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2, ensure_ascii=False)

    def save_npz(self, 
                 head_trajectories: np.ndarray, 
                 au_trajectories: np.ndarray, 
                 flame_exp_trajectories: np.ndarray, 
                 flame_jaw_trajectories: np.ndarray, 
                 output_path: str):
        """Salva tensores binários compactados (.npz) para leitura veloz em PyTorch."""
        np.savez_compressed(
            output_path,
            head_trajectories=head_trajectories.astype(np.float32),
            au_trajectories=au_trajectories.astype(np.float32),
            flame_expression=flame_exp_trajectories.astype(np.float32),
            flame_jaw=flame_jaw_trajectories.astype(np.float32),
            fps=self.fps
        )
