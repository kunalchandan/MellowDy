import pickle
import threading

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd

import sounddevice
import scipy.io.wavfile
import numpy as np

from dotmap import DotMap

import noise


CANVAS_HEIGHT = 500
HEIGHTS = np.zeros((noise.NUM_FREQS)) + CANVAS_HEIGHT
DB = np.zeros((noise.NUM_FREQS))


def play_sound():
    # db = 20log_10(amplitude)
    sound = noise.gen_noise(10 ** (DB / 20))
    sound = (sound * (2**15)).astype("int16")
    scipy.io.wavfile.write("noise.wav", noise.SAMPLING_RATE, sound)
    sounddevice.play(sound, noise.SAMPLING_RATE)


def save_sound(time_len: int):
    sound = noise.gen_noise(10 ** (DB / 20), time_len)
    sound = (sound * (2**15)).astype("int16")
    scipy.io.wavfile.write("noise.wav", noise.SAMPLING_RATE, sound)


class AmpPlot(tk.Canvas):
    """PLots frequency power"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.width = kwargs.get("width", noise.NUM_FREQS)
        self.height = kwargs.get("height", 500)
        self.bind("<B1-Motion>", self.add_line)
        self.draw_ui()

    def draw_ui(self):
        """Draw the UI e.g. dB lines, freq lines"""
        self.left_ax = 20
        self.create_line(self.left_ax, 0, self.left_ax, self.height, fill="red")
        self.db_ticks = 10
        ticks = self.db_ticks
        for i in range(ticks):
            y_pos = i * (self.height / ticks)
            self.create_line(self.left_ax, y_pos, self.left_ax + 30, y_pos, fill="red")
            if i > 0:
                db = (-i + 2) * 20
                self.create_text(self.left_ax + 50, y_pos, text=f"{db:02}dB")
        self.bottom_bar_height = self.height - (self.height / ticks)
        self.create_line(
            self.left_ax,
            self.bottom_bar_height,
            self.width,
            self.bottom_bar_height,
            fill="black",
        )
        for i in range(ticks):
            x_pos = i * (self.width / ticks) + self.left_ax
            self.create_line(
                x_pos, self.bottom_bar_height, x_pos, self.bottom_bar_height + 10
            )
            self.create_text(
                x_pos,
                self.bottom_bar_height + 10,
                text=f"{noise.freqs_hz[int(x_pos)]:.2G}Hz",
            )

    def play_sound(self):
        """Play sample of generated sound"""
        global DB
        DB = -(
            (HEIGHTS * (180 / self.bottom_bar_height)) - 40
        )  # Translate height to db
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.start()

    def save_sound(self):
        save_sound(int(self.time_entry.get()))

    def add_line(self, event):
        """Draw heights and change heights"""
        if not (
            event.x > self.left_ax
            and event.y < self.bottom_bar_height
            and event.y > 0
            and event.x < noise.NUM_FREQS
        ):
            event.x = max(event.x, self.left_ax)
            event.x = min(event.x, noise.NUM_FREQS - 1)
            event.y = max(event.y, 0)
            event.y = min(event.y, self.bottom_bar_height)

        delete_line = (
            event.x,
            self.bottom_bar_height,
            event.x,
            min(HEIGHTS[event.x], self.bottom_bar_height),
        )
        new_line = (event.x, self.bottom_bar_height, event.x, event.y)
        HEIGHTS[event.x] = event.y
        self.create_line(delete_line, fill="white")
        self.create_line(new_line)

    def save_response(self):
        """Save with a dialog"""
        f = fd.asksaveasfilename(
            confirmoverwrite=False,
            initialdir="./",
            defaultextension=".pkl",
            initialfile="heights",
            filetypes=(("Pickle file", ".pkl .pickle"), ("All Files", "*.*")),
        )
        with open(f, "wb") as file_handle:
            pickle.dump(HEIGHTS, file_handle)

    def load_response(self):
        """Load with a dialog"""
        global HEIGHTS
        f = fd.askopenfilename(
            initialdir="./",
            defaultextension=".pkl",
            initialfile="heights",
            filetypes=(("Pickle file", ".pkl .pickle"), ("All Files", "*.*")),
        )
        with open(f, "rb") as file_handle:
            HEIGHTS = pickle.load(file_handle)
        self.create_rectangle(
            0, 0, noise.NUM_FREQS, CANVAS_HEIGHT, fill="white", outline="white"
        )
        # Redraw heights
        [self.add_line(DotMap(x=i, y=height)) for i, height in enumerate(HEIGHTS)]
        self.draw_ui()


def validate_uint(user_input: str):
    if str.isdigit(user_input) or user_input == "":
        return True
    else:
        return False


def create_window():
    root = tk.Tk()
    root.title("MellowDy")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry(f"{noise.NUM_FREQS}x{600}")

    sketch = AmpPlot(root, width=noise.NUM_FREQS, height=CANVAS_HEIGHT, bg="white")
    sketch.grid(column=0, row=0)
    sketch.draw_ui()

    buttons_frame = tk.Frame(root)
    preview = ttk.Button(buttons_frame, text="Preview Sound", command=sketch.play_sound)
    save = ttk.Button(buttons_frame, text="Save Response", command=sketch.save_response)
    load = ttk.Button(buttons_frame, text="Load Response", command=sketch.load_response)
    redraw = ttk.Button(buttons_frame, text="Redraw UI", command=sketch.draw_ui)

    generate = ttk.Button(
        buttons_frame, text="Generate Long Audio", command=sketch.save_sound
    )
    length = ttk.Entry(buttons_frame, validate="all", validatecommand=validate_uint)
    sketch.time_entry = length

    buttons_frame.grid(column=0, row=1)
    preview.grid(column=0, row=0)
    save.grid(column=1, row=0)
    load.grid(column=2, row=0)
    redraw.grid(column=3, row=0)

    generate.grid(column=1, row=1)
    length.grid(column=2, row=1)

    root.mainloop()


create_window()
