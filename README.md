# Top 5 Spotify Playlist

This quick & dirty CLI tool will create a [Spotify](https://spotify.com) playlist with the top 5 songs from all artists stored in a text file. See [sample_bands.txt](sample_bands.txt)

## Usage

<img src="assets/help_msg.svg">

### Create a Spotify app

In order to use the Spotify API, you'll need an application. To create one, log into your Spotify account and open up the [developer dashboard](https://developer.spotify.com/dashboard).

- Click on `create app`
- Give the app a name and a description of your choosing
- for local usage enter `http://localhost:8080` as the `Redirect URI`
- Check the box for `Web API` under `Which API/SDKs are you planning to use?`
- click on `Save`
- After you created your app, switch to the settings and copy the `Client ID` and `Client secret`.

### Create an .env file

Paste the `Client ID`, `Client secret` and your `Redirect URI` to your .env file like this:

```ini
SPOTIPY_CLIENT_ID=Client_ID
SPOTIPY_CLIENT_SECRET=Client_Secret
SPOTIPY_REDIRECT_URI=http://localhost:8080
```

> The .env file is located in the same directory as the [top5.py](top5.py)

### Create an artists file

Create a file which holds a list of artists. Every artist must be in a new line. See [sample_bands.txt](sample_bands.txt)[^1]

### Run the script

Depending on whether the specified playlist already exists, a prompt may appear that must be confirmed before the script continues to run. 

> <span style="color: red">**Be careful with existing playlists! The script will remove all songs in the playlist and repopulate it with your artist list.**</span>

Example:

```shell
python top5.py --filename sample_bands.txt --playlist "Summer Breeze 2024" --description "Top 5 songs of every band playing at Summer Breeze 2024" --cover ~/Downloads/cover.jpg
```

<img src="assets/usage_msg.svg">

[^1]: This list contains all bands that will play at [Summer Breeze 2024](https://www.summer-breeze.de/de/)