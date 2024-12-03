#!/usr/bin/python3

"""
Music Ripper

    An advanced tool for downloading large amounts of music
from YouTube in MP3 format. Can download either individual
songs or entire music albums. It also generates a standardized
filename for the downloads, and adds ID3 metadata tags either
automatically or manually, when appropriate. 

    The program also boasts several methods of bypassing YouTube's 
bot detection algorithms and the resulting captcha/lockout when it is
triggered.
"""

import os
import sys
import time
import getopt
import configparser
import subprocess
import threading
import eyed3
from pytubefix import YouTube, Playlist
from lib import database
from lib import fetch_tag_data
from lib import download

def _show_banner():
    """ Print the banner message
    
    Arguments:
        None
        
    Returns:
        None
    """
    
    #os.system("clear") # LINUX
    os.system("cls") # WINDOWS
    print("+------------------------------------------+")
    print("| Bebop's                                  |")
    print("|     Music Ripper (version 0.1)           |")
    print("|                                          |")
    print("| A tool for pirating music from YouTube!  |")
    print("+------------------------------------------+")
    print("")
    
def _show_settings_details(config_file, database_file):
    """ Print program run details
    
    Arguments:
        config_file - filepath - Config file used
        database_file - filepath - Database file used
        
    Returns:
        None
    """
    
    print("+------------------------------------------+")
    print("| Config File & Database Loaded:           |")
    print("+------------------------------------------+")
    print("[Config File]:")
    print("\t{}".format(config_file))
    print("[Database]:")
    print("\t{}".format(database_file))
    print("+------------------------------------------+")
    print("")
    
def _show_dl_target_details(dl_mode, target_name, target_url, vid_count):
    """ Show the download mode and target details
    
    Arguments:
        dl_mode - string - The programs download mode
        target_name - string - Title of the target video or Playlist
        target_url - string - URL of the video or Playlist
        vid_count - int - Number of videos to download
        
    Returns:
        None
    """
    
    print("+------------------------------------------+")
    print("| Download Target Details:                 |")
    print("+------------------------------------------+")
    print("[Download Mode]:")
    print("\t{}".format(dl_mode))
    print("[Target URL]:")
    print("\t{}".format(target_url))
    if dl_mode == "Song":
        print("[Video Title]:")
        print("\t{}".format(target_name))
        print("+------------------------------------------+")
        print("")
    if dl_mode == "Album":
        print("[Album Title]:")
        print("\t{}".format(target_name))
        print("[Videos In Album]:")
        print("\t{}".format(vid_count))
        print("+------------------------------------------+")
        print("")
        
def _init_dl_message():
    """ Download initiation message
    
    Arguments:
        None
        
    Returns:
        None
    """
    
    print("+------------------------------------------+")
    print("| Beginning download. Initializing threads:|")
    print("+------------------------------------------+")
    
def _dl_complete_message():
    """ Download complete message
    
    Arguments:
        None
        
    Returns:
        None
    """
    
    print("+------------------------------------------+")
    print("| Download complete!                       |")
    print("+------------------------------------------+")
    print("")
        

def main(argv):
    """ Process command line arguments and control high level
    program logic
    
    Arguments:
        argv - list - User passed CLI options and arguments
        
    Returns:
        None
    """
    
    # Process command line options and arguments
    try:
        opts, args = getopt.getopt(argv, "hvdc:S:A:t:", ("help", "version", "debug", "config=", "song=", "album=", "thumbnail="))
    except getopt.GetoptError as err_msg:
        print("[ERROR] {}!".format(err_msg))
        exit(1)
        
    # Default values set here
    debug_mode = False
    config_file = "cfg/config.ini"
    target_video_url = None
    target_playlist_url = None
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Display help message and exit
            print("USAGE:")
            print("\t{} [-h] [-v] [-d] [-c CONFIG] [-S YT_VIDEO_URL] [-A YT_PLAYLIST_URL] [-t THUMBNAIL_IMG]".format(sys.argv[0]))
            print("")
            print("An advanced utility for downloading large amounts of MP3 formatted")
            print("music from YouTube without triggering their automatic bot detection and")
            print("the resulting Captcha challenge/lockout.")
            print("")
            print("OPTIONAL ARGUMENTS:")
            print("\t-h, --help\tDisplay the help message and exit")
            print("\t-v, --version\tDisplay the version message and exit")
            print("\t-d, --debug\tEnable debugging mode")
            print("\t-c, --config CONFIG\tSpecify an alternate configuration file")
            print("\t-t, --thumbnail THUMBNAIL_IMG\tManually specify a thumbnail image to add")
            print("")
            print("REQUIRED ARGUMENTS:")
            print("\t-S, --song YT_VIDEO_URL\tDownload a song from a given YouTube video URL")
            print("\t-A, --album YT_PLAYLIST_URL\tDownload a music album from a given YouTube Playlist")
            exit(0)
            
        elif opt in ("-v", "--version"):
            # Display version message and exit
            print("Music Ripper")
            print("Version 0.1")
            print("By Brandon Hammond <newdaynewburner@gmail.com>")
            exit(0)
            
        elif opt in ("-d", "--debug"):
            # Enable debugging mode
            debug_mode = True
            
        elif opt in ("-c", "--config"):
            # Specify an alternate configuration file
            if os.path.isfile(os.path.abspath(arg)) == True:
                config_file = os.path.abspath(arg)
            else:
                # Specified file not found error
                print("[ERROR] Cannot find specified config file: {}!".format(arg))
                exit(1)
                
        elif opt in ("-S", "--song"):
            # Specify to download a song from a given video URL
            target_video_url = arg
        
        elif opt in ("-A", "--album"):
            # Specify to download an album from a given Playlist URL
            target_playlist_url = arg
            
    # Display the banner message
    _show_banner()
            
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Check if DB already exists, create it if not
    db_check = database.db_init_check(config["Database"]["database_file"])
    
    # DEBUG MESSAGE
    if debug_mode == True:
        if db_check == False:
            print("[DEBUG] Database did not already exist, was initialized")
            
    # Create a database manager
    db_manager = database.DatabaseManager(debug_mode, config["Database"]["database_file"])
            
    # Show program settings
    _show_settings_details(config_file, config["Database"]["database_file"])
    
    # Change to configured base working directory
    os.chdir(config["DEFAULT"]["base_working_directory"])
    
    # Handle song downloads
    if target_video_url != None:
        # Change to song dl location
        os.chdir(config["DEFAULT"]["individual_song_dl_location"])
        dl_mode = "Song"
        yt = YouTube(target_video_url)
        vid_count = 1
        
        # Show download target details
        _show_dl_target_details(dl_mode, yt.title, target_video_url, vid_count)
        
        # Fetch song tag data
        tag_data_fetcher = fetch_tag_data.TagDataFetcher(config, db_manager)
        song_tag_data = tag_data_fetcher.get_song_tags(target_video_url)
        # DEBUG MESSAGE
        if debug_mode == True:
            print("[DEBUG]: Value of song_tag_data:")
            print(song_tag_data)
            
        # Display download init message
        _init_dl_message()
        
        # Download the song
        dl_filename = "{0} - {1}.mp3".format(target_video_url, song_tag_data["title"])
        dl_thread = threading.Thread(target=download_thread, args=(config, target_video_url, dl_filename, song_tag_data))
        print("[Download thread initialized for song]: {}".format(target_video_url))
        dl_thread.start()
        dl_thread.join()
        
    # Handle album downloads
    if target_playlist_url != None:
        # Change to album dl location
        os.chdir(config["DEFAULT"]["album_dl_location"])
        dl_mode = "Album"
        pl = Playlist(target_playlist_url)
        vid_count = len(pl.video_urls)
        
        # Show download target details
        _show_dl_target_details(dl_mode, pl.title, target_playlist_url, vid_count)
        
        # Fetch album and song tag data
        tag_data_fetcher = fetch_tag_data.TagDataFetcher(config, db_manager)
        album_tag_data = tag_data_fetcher.get_album_tags(target_playlist_url)
        # DEBUG MESSAGE
        if debug_mode == True:
            print("[DEBUG] Value of album_tag_data:")
            print(album_tag_data)
        
        dl_queue = []
        for video_url in pl.video_urls:
            queued_song = (video_url, tag_data_fetcher.get_song_tags(video_url, album_tag_data=album_tag_data))
            dl_queue.append(queued_song)
        # DEBUG MESSAGE
        if debug_mode == True:
            print("[DEBUG] Value of dl_queue:")
            print(dl_queue)
        
            
        # Add songs to DB
        for song in dl_queue:
            was_added = db_manager.add_song_to_db(song[0], song[1])
            # DEBUG MESSAGE
            if debug_mode == True:
                if was_added == False:
                    print("[DEBUG] Error adding {} to DB".format(song[0]))
        
        # Create directory for album and change into it
        os.mkdir("{0} - {1}".format(album_tag_data["artist"], album_tag_data["title"]))
        os.chdir("{0} - {1}".format(album_tag_data["artist"], album_tag_data["title"]))
        
        # Display download init message
        _init_dl_message()
        
        # Initialize download threads
        dl_threads = []
        for song in dl_queue:
            url = song[0]
            data = song[1]
            dl_filename = "{0}. {1}.mp3".format(data["track_num"], data["title"])
            dl_thread = threading.Thread(target=download.download_thread, args=(config, url, dl_filename, data))
            print("[Download thread initialized for song]: {}".format(url))
            dl_threads.append(dl_thread)
        print("")
            
        # Start threads then wait until they finish
        if config["Download"]["download_concurrently"] == "yes":
            # Concurrent download
            for dl_thread in dl_threads:
                dl_thread.start()
                if config["Download"]["add_delay_between_downloads"] == "yes":
                    time.wait(int(config["Download"]["delay_length_ms"]))
            for dl_thread in dl_threads:
                dl_thread.join()
                
        else:
            # Single download
            for dl_thread in dl_threads:
                dl_thread.start()
                if config["Download"]["add_delay_between_downloads"] == "yes":
                    time.wait(int(config["Download"]["delay_length_ms"]))
                dl_thread.join()
            
    # Display completion message
    _dl_complete_message()

    return 0

# Begin execution
if __name__ == "__main__":
    main(sys.argv[1:])