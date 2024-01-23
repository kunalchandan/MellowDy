import numpy as np
from scipy.io.wavfile import write

NUM_FREQS = 1000

freqs_hz = np.geomspace(1, 10_000, NUM_FREQS)  # frequencies Hz
freqs_rad_s = freqs_hz * 2 * np.pi  # \omega = 2 \pi f

amplitudes = np.zeros((NUM_FREQS)) + 0.1 + np.sin(np.linspace(0, np.pi, NUM_FREQS))
phase = np.random.random((NUM_FREQS)) * np.pi * 2

SAMPLING_RATE = 44100
DT = 1.0 / SAMPLING_RATE
SAMPLES = SAMPLING_RATE * 3


def gen_noise() -> np.array:
    noise = np.zeros(SAMPLES, dtype=np.float32)  # white noise

    t = 0.0
    for i in range(SAMPLES):
        t += DT
        vol = np.sum(np.multiply(np.sin(freqs_rad_s * t + phase), amplitudes))
        noise[i] = vol

    # noise /= np.max(np.abs(noise), axis=0)
    noise /= 1000

    # write("noise.wav", SAMPLING_RATE, noise)
    return noise
