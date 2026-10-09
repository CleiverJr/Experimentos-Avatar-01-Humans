"""
Módulo central da Trilha D: Controle, Emoção e Comportamento.
Pesquisa para síntese autônoma de avatares acionados por áudio e texto.
"""

from .audio_processor import AudioProcessor
from .action_units import ActionUnitsSystem, EMO_FACS_MAP
from .motion_diffusion import DDPMScheduler, TemporalMotionDenoiser, MotionDiffusionPipeline
from .instruct_parser import InstructParser
from .exporter import MotionExporter

__all__ = [
    "AudioProcessor",
    "ActionUnitsSystem",
    "EMO_FACS_MAP",
    "DDPMScheduler",
    "TemporalMotionDenoiser",
    "MotionDiffusionPipeline",
    "InstructParser",
    "MotionExporter",
]
