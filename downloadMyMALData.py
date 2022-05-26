import os
import requests
from dotenv import load_dotenv
import json

def downloadMyAnimeData():
    animeListStatus = ['watching', 'completed', 'dropped', 'on_hold', 'plan_to_watch']
    selectedLimit = '1000'
    for myStatus in animeListStatus:
        with open('./MAL Anime Data/' + myStatus + '.json', 'w', encoding='utf-8') as file:
            data = requests.get(myAnimeList, headers={'X-MAL-CLIENT-ID' : malClientID}, params={'status' : myStatus, 'fields' : selectedFields, 'nsfw' : 'true', 'limit' : selectedLimit})
            json.dump(data.json(), file, ensure_ascii=False, indent=4)

load_dotenv()

malClientID = os.getenv('X-MAL-CLIENT-ID')
myAnimeList = os.getenv('myAnimeList')
selectedFields = 'rating, media_type, genres, studios, list_status'

downloadMyAnimeData()