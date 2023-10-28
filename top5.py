import math
import os
import spotipy
import typer
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing_extensions import Annotated

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-modify-public playlist-read-private playlist-modify-private"
))

MARKET = "DE"


def main(
        filename: Annotated[str, typer.Option(
            help="A text file containing all the artists to be added to the playlist. (Each artist must be in a separate line).")],
        playlist: Annotated[str, typer.Option(
            help="The name of the new playlist")]
):
    artists = []
    tracks = []
    current_user = spotify_client.current_user()

    with open(file=filename) as f:
        search_artists = f.readlines()

    for search_artist in search_artists:
        artists.append(get_artist_id(
            artist_name=search_artist.replace("\n", "")))

    for artist_id in artists:
        tracks = tracks + get_top_tracks(artist_id=artist_id)
    playlist_items = {
        "uris": tracks
    }

    total_playlists = spotify_client.current_user_playlists()["total"]

    all_user_playlists = get_all_user_playlists(current_user["id"])

    playlist_exists = [
        item for item in all_user_playlists if item["name"] == playlist]

    if not playlist_exists:
        print("Playlist not existing. Will create it now...")
        new_playlist = spotify_client.user_playlist_create(
            user=current_user["id"],
            name=playlist,
            public=True
        )

        spotify_client.playlist_add_items(
            playlist_id=new_playlist["id"], items=tracks)
    else:
        confirm = typer.confirm(
            "The playlist already exists. Proceeding will delete all its contents and replace them. Proceed?",
            abort=True
        )
        existing_playlist = spotify_client.playlist(
            playlist_id=playlist_exists[0]["id"])

        print(existing_playlist)


def get_artist_id(artist_name: str) -> str:
    # fmt: off
    search_artist = f"artist:{artist_name}"
    # fmt: on
    result = spotify_client.search(
        q=search_artist, limit=1, type="artist", market=MARKET)
    return result["artists"]["items"][0]["id"]


def get_top_tracks(artist_id: str) -> list:
    tracks = []
    result = spotify_client.artist_top_tracks(
        artist_id=artist_id, country=MARKET)
    for track in result["tracks"][:5]:
        tracks.append(track["uri"])

    return tracks


def get_all_user_playlists(user_id: str) -> list:
    offset = 0
    limit = 50
    batch_size = 50
    all_playlists = []

    total_playlists = spotify_client.current_user_playlists()["total"]

    num_batches = -(-total_playlists // batch_size)

    for i in range(num_batches):
        offset = i * batch_size
        user_playlists = spotify_client.current_user_playlists(
            limit=batch_size, offset=offset)

        all_playlists.extend(user_playlists["items"])

    return all_playlists


if __name__ == "__main__":
    typer.run(main)
