import threading
import time
import simpleaudio as sa
import tkinter as tk
import numpy as np
import noise

HEIGHTS = np.zeros((noise.NUM_FREQS))


def play_sound():
    sound = noise.gen_noise()
    sound = (sound * (2**15)).astype("int16")
    wa = sa.WaveObject(sound, 1, 2, noise.SAMPLING_RATE)
    while True:
        play_obj = wa.play()
        play_obj.wait_done()
        time.sleep(3)
        # play_obj = sa.play_buffer(sound, 1, 2, noise.SAMPLING_RATE)
        # play_obj.wait_done()


class AmpPlot(tk.Canvas):
    """PLots frequency power"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # self.bind("<Button-1>", self.save_posn)
        self.bind("<B1-Motion>", self.add_line)
        self.bind("P", play_sound)

    def draw_UI(self):
        self.create_line(20, 0, 20, self.winfo_height(), fill="red")
        n_ticks = 20
        for i in range(n_ticks):
            y_pos = i * (self.winfo_height() / n_ticks)
            self.create_line(20, y_pos, 20 + 30, y_pos, fill="red")
            if i > 0:
                self.create_text(20 + 50, y_pos, text=f"{(i-2)*20:02}dB")
        bottom_bar_height = self.winfo_height() - (self.winfo_height() / 20)
        self.create_line(
            20, bottom_bar_height, self.winfo_width(), bottom_bar_height, fill="black"
        )

    def play_sound(self, event):
        print(f"You pressed the {event} key!")
        # sound_thread = threading.Thread(target=play_sound)
        # sound_thread.start()
        # sound_thread.join()

    # def save_posn(self, event):
    #     self.lastx, self.lasty = event.x, event.y

    def add_line(self, event):
        delete_line = (event.x, self.winfo_height(), event.x, 0)
        new_line = (event.x, self.winfo_height(), event.x, event.y)
        HEIGHTS[event.x] = event.y
        self.create_line(delete_line, fill="white")
        self.create_line(new_line)
        self.draw_UI()
        # self.save_posn(event)


def create_window():
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    sketch = AmpPlot(root, width=noise.NUM_FREQS, height=500, bg="white")
    sketch.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    root.mainloop()


# window_thread = threading.Thread(target=create_window)

# Start the threads
# window_thread.start()

create_window()
