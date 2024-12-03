from setuptools import setup

setup(
    name="music-ripper",
    version="0.1",
    description="An advanced utility for downloading music from YouTube",
    author="Brandon Hammond",
    author_email="newdaynewburner@gmail.com",
    packages=["music-ripper"],
    install_requires=[
        "pytube",
        "pytubefix",
        "eyed3",
    ],
)