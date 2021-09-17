from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
from datetime import date, datetime
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth


#Global Variables
THEME_COLOR = "#375362"
BILLBOARD_URL = "https://www.billboard.com/charts/"


GENRE_LIST = ["Pop", "Country", "Hard Rock", "Alternative Rock", "R&B", "Rap",
              "Latin", "Dance/Electronic", "Gospel", "Jazz", "Any"]


GENRE_DICT = {
    "Pop" : "pop-songs",
    "Country": "country-songs",
    "Hard Rock": "hot-hard-rock-songs",
    "Alternative Rock": "rock-songs",
    "R&B": "r-and-b-songs",
    "Rap": "rap-song",
    "Latin": "latin-songs",
    "Dance/Electronic": "dance-electronic-songs",
    "Gospel": "gospel-songs",
    "Jazz": "jazz-songs",
    "Any": "hot-100",
}


#User Interface Class
class SpotifyListGenerator:

    def __init__(self):
        self.window = Tk()
        self.window.title('Spotify List Generator')
        self.window.config(padx=20, pady=20, bg=THEME_COLOR)
        self.url = None
        self.genre = None
        self.date = None
        self.playlist = None
        self.songs_list = []
        self.create_UI()
        self.window.mainloop()


    def create_UI(self):
        #Title label
        self.title_label = Label(text="Spotify List Generator", bg=THEME_COLOR, fg="white", font=('Futura', 35, 'bold'))
        self.title_label.grid(row=0,column=0, columnspan=2, pady=50)

        #Genre Selection
        self.genre_label = Label(text="Select Genre", bg = THEME_COLOR, fg="white", font=('Futura', 20, 'italic'))
        self.genre_label.grid(row=1, column=0)
        self.genre_list = ttk.Combobox(values=GENRE_LIST)
        self.genre_list.grid(row=1, column=1)

        #Calendar
        today = date.today()
        self.calendar = Calendar(selectmode='day', year=today.year, month=today.month, day=today.day)
        self.calendar.grid(row=2, column=1, pady=50)
        self.date_label = Label(text="Select date", bg=THEME_COLOR, fg="white", font=('Futura', 20, 'italic'))
        self.date_label.grid(row=2,column=0)

        #Create list button
        self.create_button = Button(text="Create Song List", highlightthickness=0, font=('Futura', 15, 'normal'),
                                    command=self.get_url)
        self.create_button.grid(row=3, column=0, columnspan=2)


    def get_url(self):
        '''Obtain Billboard URL from selected options. Will show top 100 songs at selected dated from selected genre.'''
        try:
            self.genre = self.genre_list.get()
            selected_genre = GENRE_DICT[self.genre]
        except KeyError:
            self.genre = "Any"
            selected_genre = GENRE_DICT[self.genre]


        date_str = self.calendar.get_date()
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        self.date = date_obj.strftime('%Y-%m-%d')
        self.url = BILLBOARD_URL + selected_genre + "/" + self.date
        self.get_songs()


    def get_songs(self):
        "Get top 100 songs from selected chart via webscrapping"

        response = requests.get(self.url)
        billboard_web_page = response.text
        soup = BeautifulSoup(billboard_web_page, "html.parser")
        if self.genre == "Any":
            song_info = soup.find_all(name="span", class_="chart-element__information__song")
            artist_info = soup.find_all(name="span", class_="chart-element__information__artist")
        else:
            song_info = soup.find_all(name="span", class_="chart-list-item__title-text")
            artist_info = soup.find_all(name="div", class_="chart-list-item__artist")

        for (song,artist) in zip(song_info,artist_info):
            self.songs_list.append((song.getText(),artist.getText()))
        self.spotify()

    def spotify(self):
        """Connect to Spotify API, search if songs from billboard chart are available, add songs to a new list"""

        #Connection Authentication
        scope = "playlist-modify-public"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        user_id = sp.current_user()["id"]
        print(user_id)

        #Get songs URIs
        song_uris = []
        for (song,artist) in self.songs_list:
            result = sp.search(q=f"track:{song} artist:{artist}", type="track")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                try:
                    #Try again with just the song name
                    result = sp.search(q=f"track:{song}", type="track")
                    uri = result["tracks"]["items"][0]["uri"]
                    song_uris.append(uri)
                except IndexError:
                    print(f"{song} by {artist} doesn't exist in Spotify. Skipped")

        #Create a spotify playlist
        if self.genre != "Any":
            playlist_name = f"Billboard Top {self.genre} Songs. {self.date}"
        else:
            playlist_name = f"Billboard Top 100 Songs. {self.date}"

        description = "Automatic Generated Playlist from Top 100 Billboard charts vía Spotify API."
        self.playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            collaborative=False,
            description=description
        )

        #Add songs to the playlist
        sp.playlist_add_items(
            playlist_id=self.playlist["id"],
            items=song_uris
        )

        print(f"Playlist succesfully created!! \n Playlist name: {self.playlist['name']} \n Playlist URL: {self.playlist['external_urls']['spotify']}")








app = SpotifyListGenerator()


