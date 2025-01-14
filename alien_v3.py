from pygame.mixer import *
import audioread
import tkinter as tk
from PIL import Image, ImageTk

from screeninfo import get_monitors
import concurrent.futures
import threading
from time import sleep
from random import randint, shuffle
from os import listdir
from os.path import realpath, dirname

# monitor setup
mon = get_monitors()[0]
# RES = (WIDTH, HEIGHT) = (mon.width, mon.height)
RES = (WIDTH, HEIGHT) = (mon.width, mon.height)

mon1_width = get_monitors()[0].width

# Initialize tk
root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes('-topmost', True)
root.geometry("{}x{}+0+0".format(WIDTH, HEIGHT))
display = tk.Label(root)
display.configure(background="black")
display.pack()
root.attributes('-alpha', 0.0)

# Initialzie pygame mixer
init()

# initialize files and shuffle list
path = dirname(realpath(__file__)) + "/"
files = [s for s in listdir(path + "Alien/") if s.endswith(".ogg") and not s.startswith(".")]
shuffle(files)

# generator function to iterate through shuffled list
def filepath():
    for f in files:
        yield path + "Alien/" + f

gif = path + "Alien.gif"
info = Image.open(gif)

frames = info.n_frames # number of frames in gif

# make list of gif frames
photoimage_objects = []
for i in range(frames):
    obj = tk.PhotoImage(file=gif, format=f"gif -index {i}")
    photoimage_objects.append(obj.zoom(4))

# initialize pools
pool = concurrent.futures.ThreadPoolExecutor(max_workers=6)
main_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def animation(current_frame=0):
    global loop
    image = photoimage_objects[current_frame]

    display.configure(image=image)
    current_frame += 1

    if current_frame == frames:
        current_frame = 0

    loop = root.after(20, lambda: animation(current_frame))

def stop_animation():
    root.after_cancel(loop)

def fade_in_gif(window, alpha_value=0.0):
    if window.attributes()[1] < 1.0 and alpha_value < 1.0:
        window.attributes('-alpha', alpha_value)
        alpha_value += 0.03
        window.after(50, fade_in_gif, window, alpha_value)

def fade_out_gif(window, alpha_value=1.0):
    if window.attributes()[1] > 0.0 and alpha_value > 0.0:
        window.attributes('-alpha', alpha_value)
        alpha_value -= 0.05
        window.after(50, fade_out_gif, window, alpha_value)

def fade_in_audio(volume=0.0):
    if music.get_volume() < 1.0:
        music.set_volume(volume)
        volume += 0.03
        sleep(0.2)
        fade_in_audio(volume)

def fade_out_audio(volume=1.0):
    if music.get_volume() > 0.0:
        music.set_volume(volume)
        volume -= 0.05
        sleep(0.2)
        fade_out_audio(volume)

def calculate_timing(duration):
    min_play_time = 20
    start_time = randint(0, duration - 2 * min_play_time)
    played_duration = randint(min_play_time, duration - start_time)

    return start_time, played_duration

def play_random_part_of_video():
    if not music.get_busy():
        fi = next(f)
        totalsec = 0
        with audioread.audio_open(fi) as fl: 
            totalsec = int(fl.duration)

        start_time, played_duration = calculate_timing(totalsec)

        music.load(fi)
        music.set_volume(0)

        print("Playing {} (total of {} seconds). Starting at {} and playing for {} seconds"\
        .format(fi, totalsec, start_time, played_duration))
        pool.submit(animation)
        root.after(20, fade_in_gif, root)
        sleep(0.1)
        music.play()
        music.set_pos(start_time)

        pool.submit(fade_in_audio)
        sleep(played_duration-3)
        root.after(20, fade_out_gif, root)

        fade_out_audio()
        stop_animation()
        music.stop()
        music.unload()

def main():
    while True:
        # sleep(randint(300, 3600))

        # sleep(randint(180,300))
        sleep(5)

        play_random_part_of_video()

f = filepath()

pool.submit(main)

root.mainloop()