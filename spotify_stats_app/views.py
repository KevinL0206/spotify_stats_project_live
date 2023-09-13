from django.conf import settings
from django.shortcuts import render, redirect
from spotipy.oauth2 import SpotifyOAuth
from django.http import HttpResponse
from spotify_stats_project import settings
from decouple import config
from spotify_stats_project import settings
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
import random
import string
import requests
import base64
import datetime



class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    scope = None
    redirect_uri=None
    token_url = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret,redirect_uri,scope, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def is_token_expired(self):
        # Check if the access token has expired
        access_token = self.get_access_token()
        if not access_token:
            return True
        
    def login(self):
        
        authorization_url = 'https://accounts.spotify.com/authorize?' + urlencode({
            "response_type" : "code",
            "client_id" : self.client_id,
            "scope" : self.scope,
            'redirect_uri': self.redirect_uri
        })
        return authorization_url

    def refresh_spotify_token(self,refresh_token):
        # Define the Spotify API endpoint for token refresh
        

        # Set up the request headers and data for token refresh
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8')).decode('utf-8')
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }

        # Send a POST request to refresh the token
        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            # Parse the response content as JSON
            now = datetime.datetime.now()
            response_data = response.json()
            access_token = response_data["access_token"]
            token_type = response_data["token_type"]
            scope = response_data["scope"]
            expires_in = response_data["expires_in"]
            refresh_token = response_data.get("refresh_token", refresh_token)  # Refresh token may or may not be included

            expires = now + datetime.timedelta(seconds=expires_in)

            # Update instance variables with new token data
            self.access_token = access_token
            self.access_token_expires = expires
            self.access_token_did_expire = False

            # Return the new access token and other relevant data
            return access_token, refresh_token, expires

        else:
            # Handle the error condition here
            # You can return an error response or handle it as needed
            return None

    def auth(self,code):
        auth_options = {
            'url': 'https://accounts.spotify.com/api/token',
            'data': {
                'code': code,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code'
            },
            'headers': {
                'Authorization': 'Basic ' + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8')).decode('utf-8')
            }
        }

        response = requests.post(**auth_options)
        
        if response.status_code == 200:
            # Parse the response content as JSON
            now = datetime.datetime.now()
            response_data = response.json()
            access_token = response_data["access_token"]
            token_type = response_data["token_type"]
            scope = response_data["scope"]
            expires_in = response_data["expires_in"]
            refresh_token = response_data["refresh_token"]

            expires = now + datetime.timedelta(seconds=expires_in)
            if expires <= now:
                access_token, refresh_token, expires = self.refresh_spotify_token(refresh_token)

            

            self.access_token = access_token
            self.access_token_expires = expires

        else:
            return redirect("fail")
            
   

# Create a Spotify API Class to store data
client_id=settings.SPOTIPY_CLIENT_ID
client_secret=settings.SPOTIPY_CLIENT_SECRET
redirect_uri=settings.SPOTIPY_REDIRECT_URI
scope="user-top-read"
spotify_api=SpotifyAPI(client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri,scope=scope)

def start_page_redirect(request):
    
    return redirect("spotify-auth")

def fail_view(request):
    return render(request, 'fail.html')


def spotify_auth(request):
    
    auth = spotify_api.login()
    return redirect(auth)


def spotify_callback(request):
    
    #get code and state form URL
    code = request.GET.get('code', None)
    state = request.GET.get('state', None)

    if code :
        spotify_api.auth(code=code)
        return redirect("top-tracks")
    

     
def top_track(request):

    
    time_range = request.GET.get('time_frame', 'short_term')
    limit = int(request.GET.get('limit_frame', 20))

    endpoint_url = f'https://api.spotify.com/v1/me/top/tracks'
    # Set up the request headers with the access token
    headers = {
        'Authorization': f'Bearer {spotify_api.access_token}',
    }

    # Specify query parameters, such as time_range and limit
    params = {
        'time_range': time_range,
        'limit': limit,
    }

    # Make a GET request to the Spotify API
    response = requests.get(endpoint_url, headers=headers, params=params)
    
    if response.status_code == 200:
        # Parse the response content as JSON
        top_tracks_data = response.json()
        # Extract track information
        tracks = top_tracks_data.get('items', [])  # Get a list of track items


        track_info = []
        for track in tracks:
            

            # Album cover URLauthenticating

            album_cover_url = track.get('album', {}).get('images', [{}])[0].get('url', 'Album Cover URL Not Found')

            # Artist name (assuming there can be multiple artists for a track)
            artists = track.get('artists', [])
            artist_names = [artist.get('name', 'Artist Name Not Found') for artist in artists]

            track_info.append({
                'track': track,
                'album_cover': album_cover_url,
                'artist_name' : artist_names,
            })

        time_frame = params["time_range"]
        timeframe = " "

        if time_frame == "short_term":
            timeframe = "1 Month"
        elif time_frame == "medium_term":
            timeframe = "6 Months"
        else:
            timeframe = "All Time"


    return render(request, "top_tracks.html", {"top_tracks": track_info, "timeframe": timeframe})


def top_artist(request):

    
    time_range = request.GET.get('time_frame', 'short_term')
    limit = int(request.GET.get('limit_frame', 20))


    endpoint_url = f'https://api.spotify.com/v1/me/top/artists'
    # Set up the request headers with the access token
    headers = {
        'Authorization': f'Bearer {spotify_api.access_token}',
    }

    # Specify query parameters, such as time_range and limit
    params = {
        'time_range': time_range,
        'limit': limit,
    }

    # Make a GET request to the Spotify API
    response = requests.get(endpoint_url, headers=headers, params=params)
    
    if response.status_code == 200:
        # Parse the response content as JSON
        top_artists_data = response.json()
        # Extract track information
        artists = top_artists_data.get('items', [])  # Get a list of track items


        artist_info = []
        for artist in artists:
            
            artist_genre = artist['genres']
            artist_picture = artist['images'][0]['url']
            artist_popularity = artist['popularity']
            artist_name = artist['name']

            

            artist_info.append({
                'artist_genre': artist_genre,
                'artist_picture': artist_picture,
                'artist_popularity' : artist_popularity,
                'artist_name': artist_name
            })

        time_frame = params["time_range"]
        timeframe = " "

        if time_frame == "short_term":
            timeframe = "1 Month"
        elif time_frame == "medium_term":
            timeframe = "6 Months"
        else:
            timeframe = "All Time"


    return render(request, "top_artists.html", {"top_artists": artist_info, "timeframe": timeframe})
        