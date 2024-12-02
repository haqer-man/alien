from codecs import lookup
import tkinter as tk
from PIL import Image, ImageTk

# audio module imports
import vlc

from screeninfo import get_monitors
import concurrent.futures
from time import sleep
from random import randint
import numpy as np
from os import listdir

# monitor setup
mon = get_monitors()[0]
RES = (WIDTH, HEIGHT) = (mon.width, mon.height)

# mon1_width = get_monitors()[0].width

# Initialize tk
root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes('-topmost', True)
# root.geometry("{}x{}+{}+0".format(WIDTH,HEIGHT,mon1_width))
root.geometry("{}x{}+0+0".format(WIDTH, HEIGHT))
display = tk.Label(root)
display.configure(background="black")
display.pack()
root.attributes('-alpha', 0.0)

'''blank = tk.Tk()
blank.overrideredirect(True)
# blank.geometry("{}x{}".format(WIDTH, HEIGHT))
blk = tk.Canvas(blank, width=WIDTH, height=HEIGHT, bg="black")
blk.pack()'''

# initialize files and shuffle list
path = dirname(realpath(__file__)) + '/Alien/'
f = [s for s in listdir(path) if s.endswith(".mp3") and not s.startswith(".")]
files = np.array(f)
np.random.shuffle(files)

# generator function to iterate through shuffled list
def filepath():
    for f in files:
        yield path + f

gif = path + "Alien.gif"
info = Image.open(gif)

frames = info.n_frames # number of frames in gif

# make list of gif frames
photoimage_objects = []
for i in range(frames):
    obj = tk.PhotoImage(file=gif, format=f"gif -index {i}")
    photoimage_objects.append(obj.zoom(4))

# initialize pool
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
    fade_out_gif(root)

def fade_in_gif(window, alpha_value=0.0):
    if alpha_value < 1.0:
        window.attributes('-alpha', alpha_value)
        alpha_value += 0.05
        window.after(50, fade_in_gif, window, alpha_value)

def fade_out_gif(window, alpha_value=1.0):
    if alpha_value > 0.0:
        window.attributes('-alpha', alpha_value)
        alpha_value -= 0.05
        window.after(50, fade_out_gif, window, alpha_value)

def fade_in_audio(volume=0):
    global player
    if player.audio_get_volume() < 100:
        player.audio_set_volume(volume)
        volume += 5
        sleep(0.2)
        #pool.submit((fade_in_audio, volume))
        fade_in_audio(volume)

def play_video():
    # root.focus_force()
    global player
    if not player.is_playing():
        fi = next(f)
        player = vlc.MediaPlayer("file://{}".format(fi))
        player.audio_set_volume(0)
        print("Playing " + fi)
        root.after(20, fade_in_gif, root)
        sleep(0.1)
        player.play()
        pool.submit(fade_in_audio)
    
def main():
    # pool.submit(blank.mainloop)
    global player
    # sleep(randint(5, 10))

    # root.after(20, fade_in, root)
    # play_video()
    while True:
        # sleep(randint(300, 3600))
        sleep(randint(180, 300))
        # sleep(15)
        

        play_video()

        sleep(1)
        
        print(player.get_length())
        sleep(player.get_length() / 1000 - 2)

        fade_out_gif(root)
                
f = filepath()

player = vlc.MediaPlayer()

main_pool.submit(main)
pool.submit(animation)
root.mainloop()
