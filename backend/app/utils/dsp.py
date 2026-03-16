"""
This file contains utility functions for applying audio
effects to a given sound file
"""

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt


def rms_normalize(target_rms: int, infile: str, outfile: sf.SoundFile):
    y, sr = librosa.load(infile, sr=None)
    rms = np.sqrt(np.mean(y**2))
    gain = target_rms / rms

    y_normalized = y * gain
    y_normalized = np.clip(y_normalized, -1.0, 1.0)

    sf.write(outfile, y_normalized, sr)


def gain(factor: int, infile: str, outfile: sf.SoundFile):
    y, sr = librosa.load(infile, sr=None)
    sf.write(outfile, y * factor, sr)


def trim_silence(infile: str, outfile: sf.SoundFile, top_db: int):
    y, sr = librosa.load(infile, sr=None)
    trimmed, index = librosa.effects.trim(y, top_db)
    sf.write(outfile, trimmed, sr)


def low_pass(infile: str, outfile: sf.SoundFile):
    audio, sr = librosa.load(infile, sr=None)

    cutoff_freq = 3000
    nyquist = 0.5 * sr
    normalized_cutoff = cutoff_freq / nyquist

    b, a = butter(N=5, Wn=normalized_cutoff, btype='low')

    filtered_audio = filtfilt(b, a, audio)
    sf.write(outfile, filtered_audio, sr)


def high_pass(infile: str, outfile: sf.SoundFile):
    audio, sr = librosa.load(infile, sr=None)

    cutoff_freq = 1000
    nyquist = 0.5 * sr
    normalized_cutoff = cutoff_freq / nyquist

    b, a = butter(N=5, Wn=normalized_cutoff, btype="high")

    filtered_audio = filtfilt(b, a, audio)
    sf.write(outfile, filtered_audio, sr)


def band_pass(infile: str, outfile: sf.SoundFile):
    audio, sr = librosa.load(infile, sr=None)

    low_cutoff = 300
    high_cutoff = 3000

    nyquist = 0.5 * sr
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist

    b, a = butter(N=5, Wn=[low, high], btype="band")

    filtered_audio = filtfilt(b, a, audio)
    sf.write(outfile, filtered_audio, sr)


# TODO - implement this function later
def compression():
    pass


# TODO - implement this function later
def gate():
    pass


def pitch_shift(infile: str, outfile: sf.SoundFile, n_steps: int):
    audio, sr = librosa.load(infile, sr=None)
    shifted = librosa.effects.pitch_shift(audio, sr, n_steps)

    sf.write(outfile, shifted, sr)


def time_stretch(infile: str, outfile: sf.SoundFile, rate: float):
    audio, sr = librosa.load(infile, sr=None)
    stretched = librosa.effects.time_stretch(audio, rate)

    sf.write(outfile, stretched, sr)
