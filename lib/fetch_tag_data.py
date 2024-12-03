"""
lib/fetch_tag_data.py

Contains functions related to fetching song tag data and
adding it to the DB
"""

import os
from pytubefix import YouTube, Playlist

class TagDataFetcher(object):
    """ Contains methods that help retrieve tag data
    
    Methods:
        __init__() - Initialize the object
        get_song_tags() - Fetch song tag data for a song
        get_album_tags() - Fetch album tag data
    """
    
    def __init__(self, config, db_manager):
        """ Initialize the objects instance
        
        Arguments:
            self - object - This object
            config - ConfigParser object - Configuration data
            db_manager - DatabaseManager object - DB manager object instance
            
        Returns:
            None
        """
        
        self.config = config
        self.db_manager = db_manager
        
    def get_song_tags(self, yt_video_url, album_tag_data=None):
        """ Fetch song tag data for a song
        
        Arguments:
            self - object - This object
            yt_video_url - string - YouTube video URL for the song
            
        Returns:
            song_tag_data - dict - All song tag data retrieved
        """
        
        song_tag_data = {
            "title": None,
            "artist": None,
            "genre": None,
            "album": None,
            "track_num": None,
            "release_year": None
        }
        
        yt = YouTube(yt_video_url)
        
        # Automatic tagging mode
        if self.config["Tagging"]["tag_mode"] == "automatic":
            if self.config["Tagging"]["automatic_tag_mode_manually_confirm"] == "yes":
                print("+------------------------------------------+")
                print("| Manual confirmation of automatically     |")
                print("| fetched tag data is enabled. Press ENTER |")
                print("| to confirm tag data or enter other value.|")
                print("+------------------------------------------+")
                print("[Current Song URL]:")
                print("\t{}".format(yt_video_url))
                print("+------------------------------------------+")
                print("[Title]: {}".format(yt.title))
                song_title = input(">")
                if song_title == "":
                    song_title = yt.title
                song_tag_data["title"] = song_title
                if album_tag_data != None:
                    song_tag_data["artist"] = album_tag_data["artist"]
                    song_tag_data["genre"] = album_tag_data["genre"]
                    song_tag_data["album"] = album_tag_data["title"]
                    track_nums = album_tag_data["track_nums"]
                    song_tag_data["track_num"] = track_nums[yt_video_url]
                    song_tag_data["release_year"] = album_tag_data["release_year"]
                else:
                    print("[Artist]: {}".format(yt.author))
                    song_artist = input(">")
                    if song_artist == "":
                        song_artist = yt.author
                    song_tag_data["artist"] = song_artist
                    print("[Release Year]: {}".format(yt.publish_date))
                    song_release_year = input(">")
                    if song_release_year == "":
                        song_release_year = yt.publish_date
                    song_tag_data["release_year"] = song_release_year
            
            else:
                song_tag_data["title"] = yt.title
                if album_tag_data != None:
                    song_tag_data["artist"] = album_tag_data["artist"]
                    song_tag_data["genre"] = album_tag_data["genre"]
                    song_tag_data["album"] = album_tag_data["title"]
                    song_tag_data["track_num"] = album_tag_data["track_nums"][yt_video_url]
                    song_tag_data["release_year"] = album_tag_data["release_year"]
                else:
                    song_tag_data["artist"] = yt.author
                    song_tag_data["release_year"] = yt.publish_date
                    
        # Manual tagging mode
        elif config["Tagging"]["tag_mode"] == "manual":
            print("+------------------------------------------+")
            print("| Manual tagging mode is enabled. Please   |")
            print("| Provide the appropriate tag data below.  |")
            print("+------------------------------------------+")
            print("[Current Song URL]:")
            print("\t{}".format(yt_video_url))
            print("[Video Title]:")
            print("\t{}".format(yt.title))
            print("+------------------------------------------+")
            song_tag_data["title"] = input("[Title]> ")
            song_tag_data["artist"] = input("[Artist]> ")
            song_tag_data["genre"] = input("[Genre]> ")
            song_tag_data["album"] = input("[Album]> ")
            song_tag_data["track_num"] = input("[Track Num]> ")
            song_tag_data["release_year"] = input("[Release Year]> ")
            
        # Handle invalid tag mode
        else:
            print("[ERROR] Invalid tag mode specified in config!")
            exit(0)
            
        return song_tag_data
                
    def get_album_tags(self, yt_playlist_url):
        """ Fetch album related tag data
        
        Arguments:
            self - object - This object
            yt_playlist_url - string - YouTube Playlist URL
            
        Returns:
            album_tag_data - dict - Album level tag data
        """
        
        album_tag_data = {
            "title": None,
            "artist": None,
            "genre": None,
            "track_nums": {},
            "release_year": None
        }
        
        pl = Playlist(yt_playlist_url)
        
        # Automatic tagging mode
        if self.config["Tagging"]["tag_mode"] == "automatic":
            if self.config["Tagging"]["automatic_tag_mode_manually_confirm"] == "yes":
                print("[Album Title]: {}".format(pl.title))
                album_title = input(">")
                if album_title == "":
                    album_title = pl.title
                album_tag_data["title"] = album_title
                print("[Artist]: {}".format(pl.owner))
                album_artist = input(">")
                if album_artist == "":
                    album_artist = pl.owner
                album_tag_data["artist"] = album_artist
                print("[Genre]: ")
                album_genre = input(">")
                album_tag_data["genre"] = album_genre
                track_num = 1
                for video_url in pl.video_urls:
                    album_tag_data["track_nums"][video_url] = track_num
                    track_num = track_num + 1
                print("[Release Year]: {}".format(pl.last_updated))
                album_release_year = input(">")
                if album_release_year == "":
                    album_release_year = pl.last_updated
                album_tag_data["release_year"] = album_release_year
                
            else:
                album_tag_data["title"] = pl.title
                album_tag_data["artist"] = pl.owner
                album_tag_data["release_year"] = pl.last_updated
        
        # Manual tagging mode
        elif config["Tagging"]["tag_mode"] == "manual":
            print("+------------------------------------------+")
            print("| Manual tagging mode is enabled. Please   |")
            print("| Provide the appropriate tag data below.  |")
            print("+------------------------------------------+")
            print("[Playlist URL]:")
            print("\t{}".format(yt_playlist_url))
            print("[Playlist Title]:")
            print("\t{}".format(pl.title))
            print("+------------------------------------------+")
            album_tag_data["title"] = input("[Title]> ")
            album_tag_data["artist"] = input("[Artist]> ")
            
        # Handle invalid tag mode
        else:
            print("[ERROR] Invalid tag mode specified in config!")
            exit(0)
            
        return album_tag_data
            
        