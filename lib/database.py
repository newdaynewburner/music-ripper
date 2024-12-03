"""
lib/database.py

Contains classes and functions related to accessing and managing the SQLite
database that contains song tag data, proxies, and user agents
"""

import os
import sqlite3

class DatabaseManager(object):
    """ Contains methods that handle interaction with the DB
    
    Methods:
        __init__() - Initialize the object
        add_song_to_db() - Add a song to the database
    """
    
    def __init__(self, debug_mode, database_file):
        """ Connect to the database
        
        Arguments:
            self - object - This object
            debug_mode - bool - Enable debugging
            database_file - filepath - Path to the SQLite database
            
        Returns:
            None
        """
        
        self.debug_mode = debug_mode
        self.database_file = database_file
        self.db_con = sqlite3.connect(self.database_file)
        self.db_cur = self.db_con.cursor()
        
    def add_song_to_db(self, yt_video_url, song_tag_data):
        """ Add a song to the database
        
        Arguments:
            self - object - This object
            yt_video_url - string - Songs YouTube video URL
            song_tag_data - dict - Song tag data
            
        Returns:
            is_success - bool - True if successful
        """
        
        sql_statement = """INSERT INTO song_tag_data VALUES (
            '{0}',
            '{1}',
            '{2}',
            '{3}',
            '{4}',
            '{5}',
            '{6}'
        )""".format(yt_video_url, song_tag_data["title"], song_tag_data["artist"], song_tag_data["genre"], song_tag_data["album"], song_tag_data["track_num"], song_tag_data["release_year"])
        self.db_cur.execute(sql_statement)
        self.db_con.commit()
        
        is_success = True
        return is_success
       

def db_init_check(database_file):
    """ Check if the database exists already and, if not,
    create a new one and initialize the tables
    
    Arguments:
        database_file - filepath - Path to the SQLite3 database
        
    Returns:
        db_already_exists - bool - Will return True unless the DB had to be created
    """
    
    # Check if the database exists yet
    if os.path.isfile(database_file) == True:
        db_already_exists = True
        return db_already_exists
        
    else:
        # Create the DB
        db_con = sqlite3.connect(database_file)
        db_cur = db_con.cursor()
        
        # Initialize the tables
        sql_statement = "CREATE TABLE song_tag_data(yt_video_url, title, artist, genre, album, track_num, release_year)"
        db_cur.execute(sql_statement)
        db_con.commit()
        
        db_already_exists = False
        return db_already_exists
        
        
        