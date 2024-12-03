"""
lib/download.py

Contains classes and functions related to downloading the audio
from YouTube
"""

import os
import subprocess
import eyed3
from urllib.urlparse import urlparse
from pytubefix import YouTube
from pytubefix.exceptions import AgeRestrictedError, VideoRegionBlocked, VideoUnavailable, PytubeError
from pytubefix.innertube import _default_clients

def _convert(raw_audio_file, dl_filename):
    """ Convert raw audio to MP3
    
    Arguments:
        raw_audio_file - filename - Downloaded raw audio
        dl_filename - filename - Desired MP3 filename
        
    Returns:
        mp3_filename - filename - Name of converted file
    """
    
    convert_command = """ffmpeg -hide_banner -loglevel error -i "{0}" "{1}" """.format(raw_audio_file, dl_filename)
    subprocess.check_output(convert_command, shell=True)
    os.remove(raw_audio_file)
    
    mp3_filename = dl_filename
    return mp3_filename
    
def _tag(dl_filename, song_tag_data):
    """ Add tags to downloaded MP3
    
    Arguments:
        dl_filename - filename - MP3 file to tag
        song_tag_data - dict - Song tag data
        
    Returns:
        is_successful - bool - True if successul
    """
    
    mp3_file = eyed3.load(dl_filename)
    mp3_file.initTag()
    mp3_file.tag.title = song_tag_data["title"]
    mp3_file.tag.artist = song_tag_data["artist"]
    mp3_file.tag.genre = song_tag_data["genre"]
    mp3_file.tag.album = song_tag_data["album"]
    mp3_file.tag.track_num = song_tag_data["track_num"]
    mp3_file.tag.year = song_tag_data["release_year"]
    mp3_file.tag.save()
    
    is_successful = True
    return is_successful

def download_thread(config, yt_video_url, dl_filename, song_tag_data):
    """ Download raw audio then convert and add tags
    
    Arguments:
        config - ConfigParser object - Configuration data
        yt_video_url - string - Songs YouTube video URL
        dl_filename - filename - MP3 filename for download
        song_tag_data - dict - Song tag data
        
    Returns:
        None
    """
    
    # Define possible default clients
    default_client_list = ["ANDROID_CREATOR", "ANDROID", "WEB"]
    backup_client_num = 0
    
    # Attempt to download until success or retry limit reached
    for attempt in range(config["Download"]["max_retries"]):
        # Check OAuth settings
        if config["Download"]["use_oauth"] == "yes":
            use_oauth = True
        else:
            use_oauth = False
        if config["Download"]["allow_oauth_cache"] == "yes":
            allow_oauth_cache = True
        else:
            allow_oauth_cache = False
        
        # Check proxy settings
        if config["Download"]["use_proxies"] == "yes":
            http_proxy = config["Download"]["http_proxy"]
            https_proxy = config["Download"]["https_proxy"]
            
            proxies = {
                "http": urlparse(http_proxy).netloc,
                "https": urlparse(https_proxy).netloc
            }

            yt = YouTube(yt_video_url, proxies=proxies, use_oauth=use_oauth, allow_oauth_cache=allow_oauth_cache)
        else:
            yt = YouTube(yt_video_url, use_oauth=use_oauth, allow_oauth_cache=allow_oauth_cache)
        
        # Attempt the download and handle errors
        try:
            raw_audio = yt.streams.filter(only_audio=True).first()
            raw_audio_file = raw_audio.download()
            break
            
        except AgeRestrictedError as err_msg:
            # Handle video being age restricted
            print("[ERROR] Video is age restricted. Attempting to bypass.")
            if use_oauth == False:
                print("[ERROR] If issue persists, enable OAuth support")
                
            _default_clients["ANDROID_MUSIC"] = _default_clients[default_client_list[backup_client_num]]
            
            if backup_client_num < len(default_client_list) - 1:
                backup_client_num = backup_client_num + 1
            elif backup_client_num == len(default_client_list) - 1:
                backup_client_num = 0
                
            continue
            
        except VideoRegionBlocked as err_msg:
            # Handle video being region blocked
            print("[ERROR] Video is region blocked. Try a proxy or VPN in another country")
            continue
            
        except VideoUnavailable as err_msg:
            # Handle generic video unavailable error
            print("[ERROR] Video unavailable: {}".format(err_msg))
            continue
            
        except PytubeError as err_msg:
            # Handle technical PyTube errors
            print("[ERROR] PyTube error: {}".format(err_msg))
            continue
    
    _convert(raw_audio_file, dl_filename)
    _tag(dl_filename, song_tag_data)