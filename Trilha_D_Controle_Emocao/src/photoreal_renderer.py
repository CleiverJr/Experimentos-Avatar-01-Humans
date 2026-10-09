"""
Renderizador Foto-Realista de Avatares a partir de Foto Estática e Parâmetros de Movimento.
Aplica deformação facial densa (Delaunay Mesh Warping + Cavidade Bucal + Piscadas) sobre foto real.
Gera vídeo MP4 final sincronizado com áudio via FFmpeg.
"""

import os
import cv2
import numpy as np
import subprocess
from typing import List, Dict, Any, Tuple


class PhotorealAvatarRenderer:
    def __init__(self, portrait_image_path: str, target_size: int = 512):
        self.target_size = target_size
        self.orig_img = cv2.imread(portrait_image_path)
        if self.orig_img is None:
            raise FileNotFoundError(f"Imagem não encontrada: {portrait_image_path}")
        
        # Redimensiona para resolução quadrada alvo (512x512)
        self.base_img = cv2.resize(self.orig_img, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # Pontos de controle canônicos calibrados para o retrato em 512x512
        self.base_points = self._get_canonical_points()
        # Calcula triangulação de Delaunay nos pontos base
        self.triangles = self._compute_delaunay(self.base_points)

    def _get_canonical_points(self) -> np.ndarray:
        """Gera grade de pontos de controle para ancoragem e deformação facial."""
        # Dimensões na escala 512x512
        pts = [
            # Bordas da imagem (ancoragem estática do fundo)
            [0, 0], [256, 0], [511, 0],
            [0, 256], [511, 256],
            [0, 511], [256, 511], [511, 511],

            # Ombros e peito (movimento suave de respiração/tronco)
            [120, 420], [392, 420], [170, 350], [342, 350],

            # Contorno da cabeça / Mandíbula
            [175, 150], [337, 150],  # Têmporas
            [190, 210], [322, 210],  # Bochechas externas
            [210, 270], [302, 270],  # Ângulos da mandíbula
            [256, 305],              # Ponta do queixo

            # Sobrancelha Esquerda
            [215, 115], [235, 110], [250, 115],
            # Sobrancelha Direita
            [262, 115], [277, 110], [297, 115],

            # Olho Esquerdo
            [220, 128], [233, 122], [246, 128], [233, 134],
            # Olho Direito
            [266, 128], [279, 122], [292, 128], [279, 134],

            # Nariz
            [256, 125], [256, 155], [244, 168], [268, 168], [256, 172],

            # Lábios Externos
            [238, 192],  # Canto esquerdo
            [256, 185],  # Topo centro
            [274, 192],  # Canto direito
            [256, 206],  # Fundo centro (lábio inferior)
            [246, 199], [266, 199], # Bordas inferiores

            # Lábios Internos (para abertura)
            [243, 192], [256, 190], [269, 192], [256, 198]
        ]
        return np.array(pts, dtype=np.float32)

    def _compute_delaunay(self, points: np.ndarray) -> np.ndarray:
        rect = (0, 0, self.target_size, self.target_size)
        subdiv = cv2.Subdiv2D(rect)
        for p in points:
            subdiv.insert((float(p[0]), float(p[1])))
        
        triangle_list = subdiv.getTriangleList()
        triangles = []

        for t in triangle_list:
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])

            idx1 = self._find_point_index(pt1, points)
            idx2 = self._find_point_index(pt2, points)
            idx3 = self._find_point_index(pt3, points)

            if idx1 is not None and idx2 is not None and idx3 is not None:
                triangles.append([idx1, idx2, idx3])

        return np.array(triangles, dtype=np.int32)

    @staticmethod
    def _find_point_index(pt: Tuple[float, float], points: np.ndarray, tol: float = 1.5) -> int:
        dists = np.linalg.norm(points - np.array(pt), axis=1)
        min_idx = np.argmin(dists)
        if dists[min_idx] < tol:
            return int(min_idx)
        return None

    def deform_frame(self, 
                     pitch: float, 
                     yaw: float, 
                     roll: float, 
                     jaw_open: float, 
                     smile: float, 
                     brow: float, 
                     blink: float) -> np.ndarray:
        """
        Deforma a foto estática real para o estado motor especificado.
        pitch, yaw, roll: graus
        jaw_open: [0.0 - 1.0] (abertura na fala)
        smile: [0.0 - 1.0]
        brow: [-1.0 - 1.0]
        blink: [0.0 - 1.0]
        """
        pts = self.base_points.copy()
        cx, cy = 256.0, 180.0 # Centro da cabeça

        # 1. Rotação 3D com perspectiva e paralaxe
        rad_y = np.radians(yaw)
        rad_p = np.radians(pitch)
        rad_r = np.radians(roll)

        # Fatores de paralaxe: pontos do centro (nariz) movem mais que bordas
        for i in range(8, len(pts)):
            dx = pts[i, 0] - cx
            dy = pts[i, 1] - cy

            # Rotação Yaw (horizontal) com profundidade z aproximada
            z_factor = 1.0 + 0.3 * (1.0 - abs(dx) / 100.0)
            shift_x = rad_y * 1.5 * z_factor * 20.0
            shift_y = rad_p * 1.5 * 18.0

            # Rotação Roll (2D)
            new_dx = dx * np.cos(rad_r) - dy * np.sin(rad_r)
            new_dy = dx * np.sin(rad_r) + dy * np.cos(rad_r)

            pts[i, 0] = cx + new_dx + shift_x
            pts[i, 1] = cy + new_dy + shift_y

        # 2. Deformação de Boca e Fala (Lábio inferior e queixo descem)
        jaw_disp = jaw_open * 14.0 # deslocamento em pixels
        # Queixo (índice 17)
        pts[17, 1] += jaw_disp * 0.9
        # Lábio inferior (índices 34, 35, 36, 40)
        pts[34, 1] += jaw_disp * 1.0
        pts[35, 1] += jaw_disp * 0.7
        pts[36, 1] += jaw_disp * 0.7
        pts[40, 1] += jaw_disp * 0.9

        # Lábio superior sobe ligeiramente
        pts[32, 1] -= jaw_open * 2.0
        pts[38, 1] -= jaw_open * 2.0

        # 3. Sorriso (AU12: Cantos da boca sobem e alargam)
        smile_disp = smile * 9.0
        pts[31, 0] -= smile_disp * 0.4 # Canto esquerdo
        pts[31, 1] -= smile_disp * 0.8
        pts[33, 0] += smile_disp * 0.4 # Canto direito
        pts[33, 1] -= smile_disp * 0.8

        # 4. Sobrancelhas (AU01/AU04)
        brow_disp = brow * 8.0
        for b_idx in [18, 19, 20, 21, 22, 23]:
            pts[b_idx, 1] -= brow_disp

        # 5. Aplica Warping Triângulo por Triângulo usando interpolação bilinear afim
        warped_img = np.zeros_like(self.base_img)
        
        for tri in self.triangles:
            src_tri = self.base_points[tri]
            dst_tri = pts[tri]
            self._warp_triangle(self.base_img, warped_img, src_tri, dst_tri)

        # 6. Síntese Realista da Cavidade Bucal e Dentes na abertura da fala
        if jaw_disp > 2.5:
            warped_img = self._render_inner_mouth(warped_img, pts, jaw_disp)

        # 7. Síntese da Piscada Realista (Pálpebra descendo)
        if blink > 0.2:
            warped_img = self._render_eyelid_blink(warped_img, pts, blink)

        return warped_img

    def _warp_triangle(self, src: np.ndarray, dst: np.ndarray, src_tri: np.ndarray, dst_tri: np.ndarray):
        # Bounding boxes
        r1 = cv2.boundingRect(src_tri)
        r2 = cv2.boundingRect(dst_tri)

        # Offset points
        src_tri_cropped = []
        dst_tri_cropped = []
        for i in range(3):
            src_tri_cropped.append((src_tri[i][0] - r1[0], src_tri[i][1] - r1[1]))
            dst_tri_cropped.append((dst_tri[i][0] - r2[0], dst_tri[i][1] - r2[1]))

        # Máscara do triângulo
        mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
        cv2.fillConvexPoly(mask, np.int32(dst_tri_cropped), (1.0, 1.0, 1.0), 16, 0)

        # Recorta imagem fonte
        img1_cropped = src[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]

        # Matriz afim
        warp_mat = cv2.getAffineTransform(np.float32(src_tri_cropped), np.float32(dst_tri_cropped))
        img2_cropped = cv2.warpAffine(img1_cropped, warp_mat, (r2[2], r2[3]), None, 
                                      flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

        # Mesclagem
        dst_rect = dst[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]
        dst[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = dst_rect * (1.0 - mask) + img2_cropped * mask

    def _render_inner_mouth(self, img: np.ndarray, pts: np.ndarray, jaw_disp: float) -> np.ndarray:
        """Renderiza cavidade bucal com sombra interna e dentes superiores naturais."""
        c_left = pts[31]
        c_right = pts[33]
        top_lip = pts[38]
        bot_lip = pts[40]

        center_x = int((c_left[0] + c_right[0]) / 2)
        center_y = int((top_lip[1] + bot_lip[1]) / 2)
        rx = int(abs(c_right[0] - c_left[0]) * 0.42)
        ry = int(abs(bot_lip[1] - top_lip[1]) * 0.48)

        if rx > 3 and ry > 2:
            # Cavidade oral escura com gradiente
            mouth_mask = np.zeros((self.target_size, self.target_size), dtype=np.uint8)
            cv2.ellipse(mouth_mask, (center_x, center_y), (rx, ry), 0, 0, 360, 255, -1)
            
            # Cor interna da boca (vermelho escuro oclusal)
            dark_mouth = np.array([25, 20, 60], dtype=np.uint8)
            img[mouth_mask > 0] = (img[mouth_mask > 0] * 0.2 + dark_mouth * 0.8).astype(np.uint8)

            # Dentes superiores discretos (arco dental sutil)
            teeth_mask = np.zeros((self.target_size, self.target_size), dtype=np.uint8)
            teeth_y = center_y - int(ry * 0.2)
            teeth_rx = int(rx * 0.75)
            teeth_ry = max(1, int(ry * 0.35))
            cv2.ellipse(teeth_mask, (center_x, teeth_y), (teeth_rx, teeth_ry), 0, 0, 180, 255, -1)
            
            teeth_color = np.array([210, 215, 220], dtype=np.uint8)
            teeth_idx = (teeth_mask > 0) & (mouth_mask > 0)
            img[teeth_idx] = (img[teeth_idx] * 0.25 + teeth_color * 0.75).astype(np.uint8)

        return img

    def _render_eyelid_blink(self, img: np.ndarray, pts: np.ndarray, blink: float) -> np.ndarray:
        """Simula fechamento da pálpebra com textura e cor de pele original."""
        for eye_indices in [[24, 25, 26, 27], [28, 29, 30, 31]]:
            p_left = pts[eye_indices[0]]
            p_top = pts[eye_indices[1]]
            p_right = pts[eye_indices[2]]
            p_bot = pts[eye_indices[3]]

            cx = int((p_left[0] + p_right[0]) / 2)
            cy = int((p_top[1] + p_bot[1]) / 2)
            rx = int(abs(p_right[0] - p_left[0]) * 0.55)
            ry = int(abs(p_bot[1] - p_top[1]) * 0.6)

            if rx > 2 and ry > 2:
                # Cor média da pele acima do olho (pálpebra superior)
                skin_sample = img[int(p_top[1]) - 6:int(p_top[1]) - 1, cx - 4:cx + 4]
                skin_color = np.mean(skin_sample, axis=(0, 1)) if skin_sample.size > 0 else [140, 160, 190]

                close_amount = min(1.0, blink * 1.3)
                lid_ry = int(ry * close_amount)
                
                lid_mask = np.zeros((self.target_size, self.target_size), dtype=np.uint8)
                cv2.ellipse(lid_mask, (cx, cy - int(ry * (1.0 - close_amount))), (rx, lid_ry), 0, 0, 360, 255, -1)
                
                # Linha dos cílios
                cv2.ellipse(img, (cx, cy), (rx, max(1, int(ry * 0.2))), 0, 0, 180, (40, 45, 55), 1)
                
                img[lid_mask > 0] = (img[lid_mask > 0] * 0.15 + np.array(skin_color) * 0.85).astype(np.uint8)

        return img

    def render_video_with_audio(self, 
                                frames_data: List[Dict[str, Any]], 
                                audio_wav_path: str, 
                                output_mp4_path: str, 
                                fps: float = 30.0):
        """Renderiza todos os frames e compila vídeo H.264 com áudio AAC via FFmpeg."""
        os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
        temp_raw_video = output_mp4_path.replace(".mp4", "_raw.mp4")

        # 1. Configura VideoWriter OpenCV
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_writer = cv2.VideoWriter(temp_raw_video, fourcc, fps, (self.target_size, self.target_size))

        total = len(frames_data)
        print(f"🎬 Renderizando {total} frames foto-realistas a {fps} FPS...")

        for idx, f in enumerate(frames_data):
            p = f.get("p", f.get("head_pitch", 0.0))
            y = f.get("y", f.get("head_yaw", 0.0))
            r = f.get("r", 0.0)
            jaw = f.get("jaw", 0.0)
            smile = f.get("smile", 0.0)
            brow = f.get("brow", 0.0)
            blink = f.get("blink", 0.0)

            frame_img = self.deform_frame(pitch=p, yaw=y, roll=r, jaw_open=jaw, smile=smile, brow=brow, blink=blink)
            out_writer.write(frame_img)

        out_writer.release()
        print(f"✓ Vídeo bruto gerado em: {temp_raw_video}")

        # 2. Une vídeo e áudio via FFmpeg (H.264 + AAC)
        cmd = [
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", temp_raw_video,
            "-i", audio_wav_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            output_mp4_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(output_mp4_path):
            if os.path.exists(temp_raw_video):
                os.remove(temp_raw_video)
            print(f"✨ VÍDEO FOTO-REALISTA FINAL GERADO: {output_mp4_path}")
            return output_mp4_path
        else:
            print(f"Erro no FFmpeg: {res.stderr}")
            return temp_raw_video
