from flask import Flask, render_template, Response
from util import *
import csv
import random
import os
import re
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
 
def generate_frames(camera):
    while True:
        global emotion
        frame, emotion = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get-songs')
def getSongs():
    CLIENT_ID = os.getenv("CLIENT_ID", "011e37396bd5450ab6273510416b5e1f")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "62aafcf856bb4914907d3d6f1db46ae9")
    PLAYLIST_LINK = "https://open.spotify.com/playlist/0z5GPu1ZL2ryEmPbTyH0tB?si=d42be5c6ec194bb9&nd=1"

    emotions = {
        'sad': '0z5GPu1ZL2ryEmPbTyH0tB',
        'angry': '0a4Hr64HWlxekayZ8wnWqx',
        'happy': '1ZKdvf5yXvwVyzgznVz2Nl',
        'surprise': '3FDsPHUToNnMClpbcQ1fyj'
    }

    f_emotion = emotion

    # map facial expression emotion with song genre
    if f_emotion in emotions:
        code = emotions[f_emotion]

        PLAYLIST_LINK = f"https://open.spotify.com/playlist/{code}?si=d42be5c6ec194bb9&nd=1"
    else:
        print(f"Error: '{f_emotion}' is not a valid emotion.")

    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    # create spotify session object
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get uri from https link
    if match := re.match(r"https://open.spotify.com/playlist/(.*)\?", PLAYLIST_LINK):   
        playlist_uri = match.groups()[0]

    else:
        raise ValueError("Expected format: https://open.spotify.com/playlist/...")

    # get list of tracks in a given playlist (note: max playlist length 100)
    tracks = session.playlist_tracks(playlist_uri)["items"]

    # extract name and artist
    playlist = []
    for track in tracks:
        name = track["track"]["name"]
        uri = track["track"]["preview_url"]
        #uri  = re.sub(r'spotify:track:', 'https://open.spotify.com/track/', song_uri)

        artists = ", ".join([artist["name"] for artist in track["track"]["artists"]])
        if uri and artists:
            playlist.append((uri, name, artists))

    random_playlists = random.sample(playlist, 8)
    return render_template('index.html', playlist=random_playlists)
   # return render_template("index.html", emotion=emotion)
    #console.log("hihihi--->", df1)


if __name__ == "__main__":
    app.run(debug=True)
