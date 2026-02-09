import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from py_yt import VideosSearch
import config

class SpotifyService:
    def __init__(self):
        self._pattern = r"^(https:\/\/open.spotify.com\/)(.*)$"
        
        if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET:
            self.auth = SpotifyClientCredentials(
                config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET
            )
            self.api = spotipy.Spotify(client_credentials_manager=self.auth)
        else:
            self.api = None

    async def valid(self, url: str):
        return bool(re.search(self._pattern, url))

    async def track(self, url: str):
        track_data = self.api.track(url)
        query = track_data["name"]

        for artist in track_data["artists"]:
            name = artist["name"]
            if "Various Artists" not in name:
                query += f" {name}"
                
        search = VideosSearch(query, limit=1)
        res = await search.next()
        video = res["result"][0]
        
        return {
            "title": video["title"],
            "link": video["link"],
            "vidid": video["id"],
            "duration_min": video["duration"],
            "thumb": video["thumbnails"][0]["url"].split("?")[0],
        }, video["id"]

    async def playlist(self, url):
        pl_data = self.api.playlist(url)
        track_list = []
        
        for item in pl_data["tracks"]["items"]:
            track = item["track"]
            name = track["name"]
            for artist in track["artists"]:
                art_name = artist["name"]
                if "Various Artists" not in art_name:
                    name += f" {art_name}"
            track_list.append(name)
            
        return track_list, pl_data["id"]

    async def album(self, url):
        alb_data = self.api.album(url)
        track_list = []
        
        for item in alb_data["tracks"]["items"]:
            name = item["name"]
            for artist in item["artists"]:
                art_name = artist["name"]
                if "Various Artists" not in art_name:
                    name += f" {art_name}"
            track_list.append(name)

        return track_list, alb_data["id"]

    async def artist(self, url):
        art_data = self.api.artist(url)
        top_tracks = self.api.artist_top_tracks(url)
        track_list = []
        
        for item in top_tracks["tracks"]:
            name = item["name"]
            for artist in item["artists"]:
                art_name = artist["name"]
                if "Various Artists" not in art_name:
                    name += f" {art_name}"
            track_list.append(name)

        return track_list, art_data["id"]