"""
DSP utility module for backend audio processing.
"""

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt
from typing import Optional, List, Dict


class AudioProcessor:
    def __init__(self, infile: str):
        self.infile = infile
        self.audio, self.sr = librosa.load(infile, sr=None)
    

    def save(self, outfile: str):
        sf.write(outfile, self.audio, self.sr)


    def rms_normalize(self, target_rms: float = 0.1):
        rms = np.sqrt(np.mean(self.audio**2))
        if rms == 0:
            raise ValueError("Audio RMS is zero, cannot normalize")
        gain = target_rms / rms
        self.audio = np.clip(self.audio * gain, -1.0, 1.0)
        return self


    def gain(self, factor: float = 1.0):
        self.audio = np.clip(self.audio * factor, -1.0, 1.0)
        return self


    def trim_silence(self, top_db: int = 20):
        trimmed, _ = librosa.effects.trim(self.audio, top_db=top_db)
        self.audio = trimmed
        return self


    def low_pass(self, cutoff_freq: float = 3000):
        nyquist = 0.5 * self.sr
        b, a = butter(N=5, Wn=cutoff_freq / nyquist, btype="low")
        self.audio = filtfilt(b, a, self.audio)
        return self


    def high_pass(self, cutoff_freq: float = 1000):
        nyquist = 0.5 * self.sr
        b, a = butter(N=5, Wn=cutoff_freq / nyquist, btype="high")
        self.audio = filtfilt(b, a, self.audio)
        return self


    def band_pass(self, low_cutoff: float = 300, high_cutoff: float = 3000):
        nyquist = 0.5 * self.sr
        b, a = butter(N=5, Wn=[low_cutoff / nyquist, high_cutoff / nyquist], btype="band")
        self.audio = filtfilt(b, a, self.audio)
        return self


    def pitch_shift(self, n_steps: int = 0):
        self.audio = librosa.effects.pitch_shift(self.audio, self.sr, n_steps)
        return self


    def time_stretch(self, rate: float = 1.0):
        if rate <= 0:
            raise ValueError("Time stretch rate must be > 0")
        self.audio = librosa.effects.time_stretch(self.audio, rate)
        return self


    def compression(self, threshold: float = -20.0, ratio: float = 2.0):
        # TODO: implement compression
        return self


    def gate(self, threshold: float = -40.0):
        # TODO: implement noise gate
        return self


    @classmethod
    def apply_pipeline(cls, infile: str, outfile: str, pipeline: List[Dict]):
        """
        example pipeline:
        [
            {"effect": "rms_normalize", "target_rms": 0.1},
            {"effect": "low_pass", "cutoff_freq": 4000},
            {"effect": "gain", "factor": 1.2}
        ]
        """
        processor = cls(infile)
        for step in pipeline:
            effect_name = step.pop("effect")
            effect_method = getattr(processor, effect_name, None)
            if effect_method is None:
                raise ValueError(f"Effect {effect_name} not found")
            effect_method(**step)
        processor.save(outfile)
        return outfile