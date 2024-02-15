import tkinter.filedialog
import pygame
import math
import webbrowser
import os
import json
import time as t
from tkinter import *
from customtkinter import CTkSlider
from CTkListbox import *
from PIL import ImageTk, Image
from music import Music

background = '#f4f4f4'
foreground = '#000000'
frame_background = '#2f2f2f'
listbox_background = '#1f1f1f'
listbox_hover_color = '#d4597c'
listbox_select_color = '#d24371'
listbox_text_color = '#ffffff'
slider_color = '#d24371'
song_title_font = ('Arial', 15, 'bold')
artist_name_font = ('Arial', 11, 'normal')
general_font = ('Arial', 10, 'normal')
window_padding_x = 40
window_padding_y = 40
frame_width = 380
frame_height = 360
listbox_height = 260
listbox_width = 362


# **************************Functions**************************

# ---------------------Custom Button---------------------

def custom_button(image: PhotoImage, command=None):
    """
    This function will create a custom button where the background and the border is removed. The function will only
    accept a tkinter PhotoImage.
    :param image: tkinter PhotoImage
    :param command: function (optional)
    :return: tkinter button object
    """
    button = Button(window, image=image, command=command)
    button.config(relief=FLAT, borderwidth=0, background=background, activebackground=background)
    return button


# ---------------------Song Label Name Changer---------------------

def change_song_label_name(name: str):
    """
    This function will change the name displayed under the song name label by removing the extension and also shorten
    the name if necessary.
    :param name: string
    """
    if len(name) > 26:
        name = name[:25] + '...'

    song_title_label.config(text=name)


# ---------------------Artist Label Name Changer---------------------

def change_artist_label_name(name: str):
    """
    This function will change the name displayed under the artist name label by shortening the name if necessary.
    :param name: string
    """
    if len(name) > 32:
        name = name[:31] + '...'

    artist_name_label.config(text=name)


# ---------------------Correct Volume Icon---------------------

def correct_volume_icon():
    """
    This function will return the correct volume icon based on the current value of the music volume.
    :return: PhotoImage
    """
    if music.volume > 5:
        volume_img = max_volume_img

    elif music.volume == 0:
        volume_img = mute_volume_img

    else:
        volume_img = min_volume_img

    return volume_img


# ---------------------Total Music Length---------------------

def total_music_length(path: str):
    """
    This function will calculate the total playing time of the music from the specified path and returns the time in
    string.
    :param path: string location of the song
    :return: string time in mm:ss format
    """
    seconds_in_minute = 60
    time = music.get_total_time(path)
    time = round(time)

    minutes = time // seconds_in_minute
    seconds = time % seconds_in_minute

    # >>>>Formatting the time to have 00:00 format
    time_label = f'{minutes:02d}:{seconds:02d}'
    return time_label


# ---------------------Current Music Time---------------------

def current_music_time():
    """
    This function will calculate the current music time for the music. It will be responsible for changing the current
    time label of the song:
    """
    # >>>>The music current time will not be an integer it needs to be rounded
    running_time = round(music.get_current_time())

    # >>>>Making the song slider follow the current time of the song
    song_slider.set(running_time)

    minutes = running_time // 60
    seconds = running_time % 60

    time = f'{minutes:02d}:{seconds:02d}'

    current_time_label.config(text=time)

    # >>>>The function should update the current time every second hence it should be inside an window.after()
    window.after(1000, current_music_time)


# ---------------------Music Play---------------------

def music_play(path: str):
    """
    This function will control everything related to the play of the music
    :param path: string
    """
    global is_music_playing
    global is_song_present
    global is_heart_active
    global is_loop_active

    music.play(path)

    # >>>>Changing the from_ value of song_slider to have the length of the song
    song_slider.configure(to=music.get_total_time(path))
    song_slider.configure(number_of_steps=music.get_total_time(path))

    change_song_label_name(music.get_song_name(path))
    change_artist_label_name(music.get_artist_name(path))

    update_heart_button(path)

    play_button.config(image=pause_img)
    total_time_label.config(text=total_music_length(path))

    heart_button.config(command=lambda: heart(path))
    loop_button.config(command=loop)

    is_music_playing = TRUE
    is_song_present = TRUE
    current_music_time()


# ---------------------Check to Loop---------------------

def check_to_loop(path):
    """
    This function will check whether the song is done playing and the loop button is active to play the song again if
    both conditions are satisfied
    :param path: string
    """
    global is_loop_active
    global is_music_from_playlist

    if not is_music_from_playlist:
        # >>>>The math.floor is used to round the numbers
        current_time = math.floor(music.current_music_time)
        total_length = math.floor(music.music_length)

        if current_time == total_length and is_loop_active:
            t.sleep(1)
            music_play(path)

    window.after(300, lambda: check_to_loop(path))


# ---------------------File Access---------------------

def file_access():
    """
    This function is responsible for the actions which will be performed when the file button is clicked. It will
    provide a path that will be given to the music_play function to perform activities that are essential to the music
    being played.
    """
    try:
        path = tkinter.filedialog.askopenfilename(title='File Manager')
        music_play(path)
        check_to_loop(path)

    except pygame.error:
        pass


# ---------------------Playlist---------------------

def playlist():
    global is_playlist_on
    global is_favorites_on

    if not is_playlist_on:
        is_playlist_on = TRUE

        # >>>>Making sure the is_favorites_on flag is false when the playlist bar is opened
        if is_favorites_on:
            is_favorites_on = FALSE
            frame_listbox.delete(0, END)

        frame_img.grid_forget()
        frame_back_button.grid(row=0, column=0, pady=10, padx=0)

        frame_listbox.grid(row=1, column=0, columnspan=6)
        frame_add_button.grid(row=2, column=0, pady=10)
        frame_play_button.grid(row=2, column=2, columnspan=2, padx=0)
        frame_remove_button.grid(row=2, column=5, pady=10)

    else:
        is_playlist_on = FALSE
        frame_listbox.delete(0, END)
        frame_back_button.grid_forget()
        frame_listbox.grid_forget()
        frame_add_button.grid_forget()
        frame_remove_button.grid_forget()
        frame_play_button.grid_forget()
        frame_img.grid(row=0, column=0)


# ---------------------Back Command---------------------

def back():
    global is_playlist_on
    global is_favorites_on

    is_playlist_on = FALSE
    is_favorites_on = FALSE

    frame_listbox.delete(0, END)

    frame_back_button.grid_forget()
    frame_listbox.grid_forget()
    frame_add_button.grid_forget()
    frame_remove_button.grid_forget()
    frame_play_button.grid_forget()

    frame_img.grid(row=0, column=0)


# ---------------------Favorites Access---------------------

def favorites():
    global is_favorites_on
    global is_playlist_on
    global song_playlist

    if not is_favorites_on:
        is_favorites_on = TRUE

        # >>>>Making sure the is_playlist_on flag is false when the favorites bar is opened
        if is_playlist_on:
            is_playlist_on = FALSE
            frame_listbox.delete(0, END)

        frame_img.grid_forget()
        frame_add_button.grid_forget()
        frame_remove_button.grid_forget()

        frame_back_button.grid(row=0, column=0, pady=10, padx=5)
        frame_listbox.grid(row=1, column=0, columnspan=6)
        frame_play_button.grid(row=2, column=2, columnspan=2, pady=10, padx=(0, 28))

        with open('favorites.json', 'r') as data:
            song_playlist = json.load(data)

            for song in song_playlist:
                song_name = music.get_song_name(song)

                if len(song_name) > 40:
                    song_name = song_name[:39] + '...'

                frame_listbox.insert(END, song_name)

    else:
        is_favorites_on = FALSE
        frame_listbox.delete(0, END)
        frame_back_button.grid_forget()
        frame_listbox.grid_forget()
        frame_play_button.grid_forget()
        frame_img.grid(row=0, column=0)


# ---------------------Add to Playlist---------------------

def add_to_playlist():
    global index

    path = tkinter.filedialog.askopenfilename()
    song_playlist.append(path)
    song_name = music.get_song_name(path)
    if len(song_name) > 40:
        song_name = song_name[:39] + '...'
    frame_listbox.insert(index, song_name)
    index += 1


# ---------------------Remove from Playlist---------------------

def remove_from_playlist():
    selected_index = frame_listbox.curselection()
    song_playlist.pop(selected_index)
    frame_listbox.delete(selected_index)


# ---------------------Play Playlist---------------------

def play_playlist():
    global is_playlist_on

    is_playlist_on = TRUE


# ---------------------Play Pause Button Control---------------------

def play_pause_control():
    """
    This function will control the action of the play button. It will check whether there is a song present or not and
    if so it will check whether a music is playing or not.
    """
    global is_music_playing
    global is_song_present

    if is_song_present:
        if is_music_playing:
            music.pause()
            play_button.config(image=play_img)
            is_music_playing = FALSE

        else:
            is_music_playing = TRUE
            play_button.config(image=pause_img)
            music.unpause()


# ---------------------Volume Button Control---------------------

def volume_button_control():
    """
    This function will control the mute or unmute functionality of the volume button. It will check whether the song is
    muted or not and performs actions accordingly.
    """
    global is_mute
    volume = music.volume

    if volume == 0:
        is_mute = TRUE
        volume = 1

    if is_mute:
        is_mute = FALSE
        volume_slider_control(volume)
        volume_slider.set(volume)
        volume_button.config(image=correct_volume_icon())

    else:
        is_mute = TRUE
        volume_slider.set(0)
        music.adjust_volume(0)
        volume_label.config(text='0')
        volume_button.config(image=mute_volume_img)


# ---------------------Volume Slider Control---------------------

def volume_slider_control(value):
    """
    This function will control the volume with the help of the volume slider. It will adjust the volume according to the
    value provided by the volume slider.
    :param value: integer
    """
    music.adjust_volume(value)

    music.volume = math.ceil(value)

    with open('./data/volume.txt', 'w') as vol:
        vol.write(str(music.volume))

    volume_label.config(text=f'{music.volume}')

    volume_button.config(image=correct_volume_icon())


# ---------------------Information---------------------

def about():
    """
    This function will open a webpage that has information about the music application. It is associated with the
    info_button.
    """
    relative_path = 'about_link/index.html'

    # >>>>To insure having the correct absolute path irrespective of the device
    absolute_path = os.path.abspath(relative_path)
    webbrowser.open('file://' + absolute_path)


# ---------------------Heart Button Control---------------------

def heart_button_control(path):
    """
    This function will be responsible on changing the heart icon and the variable responsible to activating the
    condition of the song be liked or not. It will also add the path to the favorites.json file in order to activate the
    condition.
    """
    global is_heart_active
    data = load_favorite()

    if is_heart_active:
        is_heart_active = FALSE
        heart_button.config(image=heart_img)
        data.remove(path)

    else:
        is_heart_active = TRUE
        heart_button.config(image=active_heart_img)
        data.append(path)

    add_favorite(data)


# ---------------------Heart Button Control---------------------

def heart(path):
    """
    This function will call the heart_button_control function once every one millisecond to refresh the function.
    """
    window.after(1, lambda: heart_button_control(path))


# ---------------------Favorite Path Adder---------------------

def add_favorite(path):
    """
    This function will update the json file called favorites.json by writing through it. It will add the path to the
    json file.
    :param path: string
    """
    with open('favorites.json', 'w') as file:
        json.dump(path, file, indent=4)


# ---------------------Favorite Loader---------------------

def load_favorite():
    """
    This function will return a json object by reading it from a json file called favorites.json.
    :return: json data
    """
    try:
        with open('favorites.json', 'r') as file:
            return json.load(file)

    except json.decoder.JSONDecodeError:
        return []


# ---------------------Favorite Button Updater---------------------

def update_heart_button(path):
    """
    This function will update the state of the heart button depending on the song being a favorite or not.
    :param path: string
    """
    global is_heart_active

    data = load_favorite()
    if path in data:
        heart_button.config(image=active_heart_img)
        is_heart_active = TRUE

    else:
        heart_button.config(image=heart_img)
        is_heart_active = FALSE


# ---------------------Loop Button Control---------------------

def loop_button_control():
    """
    This function is responsible to controlling the looping of the song or not. It will change the loop icon and also
    the variable responsible to controlling the looping of the song.
    """
    global is_loop_active

    if is_loop_active:
        is_loop_active = FALSE
        loop_button.config(image=loop_img)

    else:
        is_loop_active = TRUE
        loop_button.config(image=active_loop_img)


# ---------------------Loop Control---------------------

def loop():
    """
    This function will call the loop_button_control function once every one millisecond to activate the said function.
    """
    window.after(1, loop_button_control)


# ---------------------Seek Control---------------------

def seek(val):
    music.seek_song(val)
    music.current_music_time = val


# **************************Creating a Tkinter window**************************

window = Tk()

# **************************Variables**************************

music = Music()
index = 0
song_playlist = []
is_mute = BooleanVar()
is_mute.set(False)
is_music_playing = FALSE
is_song_present = FALSE
is_mute = FALSE
is_heart_active = FALSE
is_loop_active = FALSE
is_music_from_playlist = FALSE
is_playlist_on = FALSE
is_favorites_on = FALSE

# **************************Creating every image instance to be used**************************

# ---------------------Logo images---------------------
logo_img = PhotoImage(file='./images/logo/logo.png')
webapp_img = PhotoImage(file='./images/logo/webapp.png')

# ---------------------Images for the menu bar (file, playlist, favorite, information)---------------------
file_img = PhotoImage(file='./images/icons/folder.png')
playlist_img = PhotoImage(file='./images/icons/playlist.png')
favorite_img = PhotoImage(file='./images/icons/favorite.png')
info_img = PhotoImage(file='./images/icons/info.png')

# ---------------------Play and pause images---------------------
play_img = PhotoImage(file='./images/icons/play/play.png')
pause_img = PhotoImage(file='./images/icons/play/pause.png')

# ---------------------Previous and next images---------------------
previous_img = PhotoImage(file='./images/icons/previous.png')
next_img = PhotoImage(file='./images/icons/next.png')

# ---------------------Loop active and inactive images---------------------
loop_img = PhotoImage(file='./images/icons/loop/loop.png')
active_loop_img = PhotoImage(file='./images/icons/loop/loop_active.png')

# ---------------------Heart active and inactive images---------------------
heart_img = PhotoImage(file='images/icons/heart/heart.png')
active_heart_img = PhotoImage(file='./images/icons/heart/heart_active.png')

# ---------------------Maximum, minimum and mute volume images---------------------
max_volume_img = PhotoImage(file='./images/icons/volume/max_volume.png')
min_volume_img = PhotoImage(file='./images/icons/volume/min_volume.png')
mute_volume_img = PhotoImage(file='./images/icons/volume/mute_volume.png')

# ---------------------Tkinter frame image instances---------------------
headphone = Image.open('images/frame/headphone.jpg')
headphone = headphone.resize((frame_width, frame_height))

headphone_img = ImageTk.PhotoImage(headphone)

back_img = PhotoImage(file='images/frame/back.png')
add_img = PhotoImage(file='./images/frame/add.png')
remove_img = PhotoImage(file='./images/frame/remove.png')
play_collection_img = PhotoImage(file='./images/frame/play.png')

# **************************Buttons**************************

# ---------------------File Button---------------------
file_button = custom_button(image=file_img, command=file_access)
file_button.grid(row=0, column=0, pady=(0, 20))

# ---------------------Playlist Button---------------------
playlist_button = custom_button(image=playlist_img, command=playlist)
playlist_button.grid(row=1, column=0, pady=(20, 20))

# ---------------------Favorites Button---------------------
favorite_button = custom_button(image=favorite_img, command=favorites)
favorite_button.grid(row=2, column=0, pady=(20, 20))

# ---------------------Information Button---------------------
info_button = custom_button(image=info_img, command=about)
info_button.grid(row=7, column=0)

# ---------------------WebApp Button---------------------
webapp_button = custom_button(image=webapp_img)
webapp_button.grid(row=3, column=0, pady=(20, 20))

# ---------------------Loop Button---------------------
loop_button = custom_button(image=loop_img)
loop_button.grid(row=7, column=1, pady=(10, 10), padx=(25, 0))

# ---------------------Heart Button---------------------
heart_button = custom_button(image=heart_img)
heart_button.grid(row=7, column=6, pady=(10, 10))

# ---------------------Previous Button---------------------
previous_button = custom_button(image=previous_img)
previous_button.grid(row=10, column=1, pady=(20, 0), padx=(40, 10))

# ---------------------Play Button---------------------
play_button = custom_button(image=pause_img, command=play_pause_control)
play_button.grid(row=10, column=2, pady=(20, 0), padx=(10, 10))

# ---------------------Next Button---------------------
next_button = custom_button(image=next_img)
next_button.grid(row=10, column=3, pady=(20, 0), padx=(10, 10))

# ---------------------Volume Button---------------------
volume_button = custom_button(image=correct_volume_icon(), command=volume_button_control)
volume_button.grid(row=10, column=4, pady=(20, 0), padx=(20, 0))

# **************************Frame**************************

frame = Frame(window, height=frame_height, width=frame_width, background=frame_background)
frame.grid(row=0, column=1, columnspan=6, rowspan=5, padx=(30, 0), pady=(0, 20))

# ---------------------Frame Image---------------------
frame_img = Label(
    frame,
    image=headphone_img
)
frame_img.grid(row=0, column=0)

# ---------------------Frame Back Button---------------------
frame_back_button = Button(
    frame,
    image=back_img,
    relief=FLAT,
    borderwidth=0,
    background=frame_background,
    activebackground=frame_background,
    command=back
)

# ---------------------Frame ListBox---------------------
frame_listbox = CTkListbox(
    frame,
    height=listbox_height,
    width=listbox_width,
    border_width=0,
    hover_color=listbox_hover_color,
    fg_color=listbox_background,
    highlight_color=listbox_select_color,
    text_color=listbox_text_color
)

# ---------------------Add Button---------------------
frame_add_button = Button(
    frame,
    image=add_img,
    relief=FLAT,
    borderwidth=0,
    background=frame_background,
    activebackground=frame_background,
    command=add_to_playlist
)

# ---------------------Remove Button---------------------
frame_remove_button = Button(
    frame,
    image=remove_img,
    relief=FLAT,
    borderwidth=0,
    background=frame_background,
    activebackground=frame_background,
    command=remove_from_playlist
)

# ---------------------Play Collection Button---------------------
frame_play_button = Button(
    frame,
    image=play_collection_img,
    relief=FLAT,
    borderwidth=0,
    background=frame_background,
    activebackground=frame_background
)

# **************************Song Labels**************************

# ---------------------Song Title Label---------------------
song_title_label = Label(
    text='Unknown Song',
    font=song_title_font,
    background=background,
    foreground=foreground
)
song_title_label.grid(row=5, column=1, columnspan=6, pady=(20, 10))

# ---------------------Artist Name Label---------------------
artist_name_label = Label(
    text='Unknown Artist',
    font=artist_name_font,
    background=background,
    foreground=foreground
)
artist_name_label.grid(row=6, column=1, columnspan=6, pady=(0, 10))

# ---------------------Current Time Label---------------------
current_time_label = Label(
    text='00:00',
    font=general_font,
    background=background,
    foreground=foreground
)
current_time_label.grid(row=9, column=1, pady=(10, 0), padx=(30, 0))

# ---------------------Total Time Label---------------------
total_time_label = Label(text='00:00', font=general_font, background=background, foreground=foreground)
total_time_label.grid(row=9, column=6, pady=(10, 0))

# ---------------------Volume Label---------------------
volume_label = Label(
    text=f'{music.volume}',
    font=general_font,
    background=background,
    foreground=foreground
)
volume_label.grid(row=10, column=6, pady=(20, 0))

# **************************Sliders**************************

# ---------------------Song Slider---------------------
song_slider = CTkSlider(
    window,
    from_=0,
    to=100,
    orientation=HORIZONTAL,
    width=frame_width,
    progress_color=slider_color,
    button_hover_color=slider_color,
    button_color=slider_color,
    command=seek
)
song_slider.set(0)
song_slider.grid(row=8, column=1, columnspan=6, padx=(30, 0))

# ---------------------Volume Slider---------------------
volume_slider = CTkSlider(
    window,
    from_=0,
    to=music.volume_range,
    orientation=HORIZONTAL,
    width=100,
    progress_color=slider_color,
    button_hover_color=slider_color,
    button_color=slider_color,
    command=volume_slider_control,
    number_of_steps=music.volume_range
)
volume_slider.set(music.volume)
volume_slider.grid(row=10, column=5, pady=(20, 0))

# **************************Customizing the Tkinter window**************************

window.title('Play Music')
window.iconphoto(True, logo_img)

# >>>>Disabling the resizing property of the window
window.resizable(width=False, height=False)

window.config(padx=window_padding_x, pady=window_padding_y, background=background)

# >>>>Updating the window to get the appropriate dimension of the window
window.update()

# >>>>Getting the correct current width and height of the window
window_width = window.winfo_width()
window_height = window.winfo_height()

# >>>>Changing the starting position of the window
x_start = 30
y_start = 40
window.geometry(f'{window_width}x{window_height}+{x_start}+{y_start}')

# **************************Looping through the window**************************

window.mainloop()
