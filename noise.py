import time
import numpy as np

NUM_FREQS = 1000

freqs_hz = np.geomspace(1, 20_000, NUM_FREQS)  # frequencies Hz
freqs_rad_s = freqs_hz * 2 * np.pi  # \omega = 2 \pi f

amplitudes = np.zeros((NUM_FREQS)) + 0.1 + np.sin(np.linspace(0, np.pi, NUM_FREQS))
phase = np.random.random((NUM_FREQS)) * np.pi * 2

SAMPLING_RATE = 44100
DT = 1.0 / SAMPLING_RATE
SAMPLES = SAMPLING_RATE * 1


def gen_noise(response: np.array, time_length: int = 1) -> np.array:
    SAMPLES = SAMPLING_RATE * time_length
    noise = np.zeros(SAMPLES, dtype=np.float32)  # white noise

    time_vals = np.array(range(SAMPLES)) / SAMPLING_RATE
    # vol_calculation = lambda time: np.sum(np.multiply(np.sin(freqs_rad_s * time + phase), response))
    # vol_vectorized = np.vectorize(vol_calculation)
    t1 = time.time_ns()
    vol = [
        np.sum(np.multiply(np.sin(freqs_rad_s * t + phase), response))
        for t in time_vals
    ]
    t2 = time.time_ns()
    print(f"{(t2-t1)//1000_000}ms")
    # t1 = time.time_ns()
    # vol = np.sum(np.multiply(np.sin(np.outer(time_vals, freqs_rad_s) + phase), response))
    # t2 = time.time_ns()
    # print(f"{(t2-t1)//1000_000}ms")

    noise = vol
    noise /= np.max(np.abs(noise), axis=0)
    return noise
