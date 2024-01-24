import pickle
import threading

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd

import simpleaudio as sa
import numpy as np
import noise

CANVAS_HEIGHT = 500
HEIGHTS = np.zeros((noise.NUM_FREQS)) + CANVAS_HEIGHT
DB = np.zeros((noise.NUM_FREQS))

def play_sound():
    sound = noise.gen_noise(HEIGHTS)
    sound = (sound * (2**15)).astype("int16")
    wa = sa.WaveObject(sound, 1, 2, noise.SAMPLING_RATE)
    play_obj = wa.play()
    play_obj.wait_done()
    # play_obj = sa.play_buffer(sound, 1, 2, noise.SAMPLING_RATE)
    # play_obj.wait_done()


class AmpPlot(tk.Canvas):
    """PLots frequency power"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.width = kwargs.get("width", 100)
        self.height = kwargs.get("height", 100)
        # self.bind("<Button-1>", self.save_posn)
        self.bind("<B1-Motion>", self.add_line)
        self.bind("P", play_sound)
        self.draw_UI()

    def draw_UI(self):
        """Draw the UI e.g. dB lines, freq lines"""
        self.left_ax = 20
        self.create_line(self.left_ax, 0, self.left_ax, self.height, fill="red")
        n_ticks = 10
        for i in range(n_ticks):
            y_pos = i * (self.height / n_ticks)
            self.create_line(self.left_ax, y_pos, self.left_ax + 30, y_pos, fill="red")
            if i > 0:
                db = (-i + 2) * 20
                self.create_text(self.left_ax + 50, y_pos, text=f"{db:02}dB")
        self.bottom_bar_height = self.height - (self.height / n_ticks)
        self.create_line(
            self.left_ax,
            self.bottom_bar_height,
            self.width,
            self.bottom_bar_height,
            fill="black",
        )
        for i in range(n_ticks):
            x_pos = i * (self.width / n_ticks) + self.left_ax
            self.create_line(
                x_pos, self.bottom_bar_height, x_pos, self.bottom_bar_height + 10
            )
            self.create_text(
                x_pos,
                self.bottom_bar_height + 10,
                text=f"{noise.freqs_hz[int(x_pos)]:.1e}Hz",
            )

    def play_sound(self, event=None):
        """Play sample of generated sound"""
        print(f"You pressed the {event} key!")
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.start()

    def add_line(self, event):
        """Draw heights and change heights"""
        if (
            event.x > self.left_ax
            and event.y < self.bottom_bar_height
            and event.x < noise.NUM_FREQS
        ):
            delete_line = (
                event.x,
                self.bottom_bar_height,
                event.x,
                min(HEIGHTS[event.x], self.bottom_bar_height),
            )
            new_line = (event.x, self.bottom_bar_height, event.x, event.y)
            HEIGHTS[event.x] = event.y
            DB[event.x] = HEIGHTS # Translate height to db
            self.create_line(delete_line, fill="white")
            self.create_line(new_line)
            # self.save_posn(event)


def save_data():
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


def load_data():
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
    # Redraw UI


def create_window():
    root = tk.Tk()
    root.title("MellowDy")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry(f"{noise.NUM_FREQS}x{600}")

    sketch = AmpPlot(root, width=noise.NUM_FREQS, height=CANVAS_HEIGHT, bg="white")
    sketch.grid(column=0, row=0)
    sketch.draw_UI()

    buttons_frame = tk.Frame(root)
    play = ttk.Button(buttons_frame, text="Play Sound", command=sketch.play_sound)
    save = ttk.Button(buttons_frame, text="Save", command=save_data)
    load = ttk.Button(buttons_frame, text="Load", command=load_data)
    redraw = ttk.Button(buttons_frame, text="Redraw UI", command=sketch.draw_UI)
    buttons_frame.grid(column=0, row=1)
    play.grid(column=0, row=0)
    save.grid(column=1, row=0)
    load.grid(column=2, row=0)
    redraw.grid(column=3, row=0)

    root.mainloop()


# window_thread = threading.Thread(target=create_window)

# Start the threads
# window_thread.start()

create_window()
