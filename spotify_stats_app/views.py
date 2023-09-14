from django.shortcuts import render, redirect
from decouple import config
from spotify_stats_project import settings
from urllib.parse import urlencode
from django.urls import reverse
import os




def start_page_redirect(request):

    client_info={
        "client_id" : os.environ.get('client_id'),
        "client_secret" : os.environ.get('client_secret'),
        "redirect_uri" : os.environ.get('redirect_uri'),
    }

    return render(request,"start.html",client_info)

def fail_view(request):

    return render(request, 'fail.html')


def spotify_callback(request):
   
    return render(request, "home.html")
    
     
def top_track(request):


    return render(request, "top_tracks.html")


def top_artist(request):


    return render(request, "top_artists.html")
        

