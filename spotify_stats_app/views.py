
from django.shortcuts import render, redirect
from decouple import config
from spotify_stats_project import settings
from urllib.parse import urlencode
from django.urls import reverse


def start_page_redirect(request):
    
    return render(request,"start.html")

def fail_view(request):
    return render(request, 'fail.html')


def spotify_callback(request):
   
    return render(request, "home.html")
    
     
def top_track(request):


    return render(request, "top_tracks.html")


def top_artist(request):


    return render(request, "top_artists.html")
        