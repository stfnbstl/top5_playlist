import base64
import os

import spotipy
import typer
from rich.progress import track
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from typing_extensions import Annotated

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-modify-public playlist-read-private playlist-modify-private ugc-image-upload"
))

MARKET = "DE"


def main(
        filename: Annotated[str, typer.Option(
            help="A text file containing all the artists to be added to the playlist. (Each artist must be in a separate line).")],
        playlist: Annotated[str, typer.Option(
            help="The name of the playlist")],
        description: Annotated[str, typer.Option(
            help="The description of your playlist")] = "",
        cover: Annotated[str, typer.Option(
            help="Path to your playlist cover (JPG File)")] = None
):
    artists = []
    tracks = []
    current_user = spotify_client.current_user()

    with open(file=filename) as f:
        search_artists = f.readlines()

    for search_artist in track(search_artists, description="Getting Artist IDs"):
        artists.append(get_artist_id(
            artist_name=search_artist.replace("\n", "")))

    for artist_id in track(artists, description="Getting top tracks"):
        tracks = tracks + get_top_tracks(artist_id=artist_id)

    all_user_playlists = get_all_user_playlists()

    playlist_exists = [
        item for item in all_user_playlists if item["name"] == playlist]

    if not playlist_exists:
        print("Playlist not existing. Will create it now...")
        work_playlist = spotify_client.user_playlist_create(
            user=current_user["id"],
            name=playlist,
            public=True,
            description=description
        )
    else:
        confirm = typer.confirm(
            "The playlist already exists. Proceeding will delete all its contents and replace them. Proceed?",
            abort=True
        )
        work_playlist = spotify_client.playlist(
            playlist_id=playlist_exists[0]["id"])

        existing_tracks = get_all_tracks_playlist(
            playlist_id=work_playlist["id"])
        spotify_client.playlist_change_details(
            playlist_id=work_playlist["id"], description=description)
        # only 100 tracks can be deleted in one request
        # splitting
        chunk_size = 100
        chunks = [existing_tracks[i:i + chunk_size]
                  for i in range(0, len(existing_tracks), chunk_size)]

        for chunk in chunks:
            spotify_client.playlist_remove_all_occurrences_of_items(
                playlist_id=work_playlist["id"], items=chunk)

    # splitting tracks in chunks of 100 items
    # because there's a limit of 100 tracks for one request
    chunk_size = 100
    chunks = [tracks[i:i + chunk_size]
              for i in range(0, len(tracks), chunk_size)]

    for chunk in track(chunks, description="Adding Songs"):
        spotify_client.playlist_add_items(
            playlist_id=work_playlist["id"], items=chunk)

    if cover is not None:
        with open(cover, "rb") as image:
            binary_cover = image.read()

        base64_cover = base64.b64encode(binary_cover).decode("utf-8")
        spotify_client.playlist_upload_cover_image(
            playlist_id=work_playlist["id"], image_b64=base64_cover)

    print("Done!")


def get_artist_id(artist_name: str) -> str:
    # fmt: off
    search_artist = f"artist:{artist_name}"
    # fmt: on
    result = spotify_client.search(
        q=search_artist, limit=10, type="artist", market=MARKET)
    artist_id = result["artists"]["items"][0]["id"]

    return artist_id


def get_top_tracks(artist_id: str) -> list:
    tracks = []
    result = spotify_client.artist_top_tracks(
        artist_id=artist_id, country=MARKET)
    for track in result["tracks"][:5]:
        tracks.append(track["uri"])

    return tracks


def get_all_user_playlists() -> list:
    offset = 0
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


def get_all_tracks_playlist(playlist_id: str) -> list:
    all_tracks = []
    offset = 0
    batch_size = 50

    total_tracks = spotify_client.playlist_items(
        playlist_id=playlist_id)["total"]

    num_batches = -(-total_tracks // batch_size)

    for i in range(num_batches):
        offset = i * batch_size
        track_batch = spotify_client.user_playlist_tracks(
            playlist_id=playlist_id, limit=batch_size, offset=offset)
        track_batch_uris = [track["track"]["id"]
                            for track in track_batch["items"]]

        all_tracks.extend(track_batch_uris)

    return all_tracks


if __name__ == "__main__":
    typer.run(main)
