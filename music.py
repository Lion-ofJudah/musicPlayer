from pygame import mixer
from mutagen.easyid3 import EasyID3
import os
import mutagen


class Music:
    def __init__(self):
        mixer.init()
        self.music = mixer.music
        self.is_playing = self.music.get_busy()

        with open('./data/volume.txt') as volume:
            self.volume = volume.read()
            self.volume = int(self.volume)

        self.music_length = 0
        self.current_music_time = 0
        self.volume_range = 10
        self.artist_name = None
        self.song_name = None
        self.music.set_volume(self.volume / self.volume_range)

    def play(self, path):
        self.music.load(path)
        self.music.play()

    def pause(self):
        self.music.pause()

    def unpause(self):
        self.music.unpause()

    def adjust_volume(self, value):
        volume = value / self.volume_range
        self.music.set_volume(volume)

    def get_total_time(self, path):
        music_file = mutagen.File(path)
        self.music_length = music_file.info.length

        return self.music_length

    def get_current_time(self):
        millisecond_in_second = 1000

        # >>>>get_pos() method will give a result in millisecond and to convert it into second
        self.current_music_time = self.music.get_pos() / millisecond_in_second

        return self.current_music_time

    def get_artist_name(self, path):
        try:
            song = EasyID3(path)
            self.artist_name = song['album'][0]

        except KeyError:
            self.artist_name = 'Unknown Album'

        finally:
            return self.artist_name

    def get_song_name(self, path):
        try:
            song = EasyID3(path)
            self.song_name = song['title'][0]

        except KeyError:
            self.song_name = os.path.basename(path)

        except mutagen.MutagenError:
            self.song_name = os.path.basename(path)

        finally:
            return self.song_name

    def seek_song(self, position):
        self.music.set_pos(position)
        self.current_music_time = position
