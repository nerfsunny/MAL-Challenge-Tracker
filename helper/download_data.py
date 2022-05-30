import requests
import json
from bs4 import BeautifulSoup as bs
from helper.custom_classes import hofAnime

def myAnimeData(malClientID, myAnimeList, selectedFields, directoryPath):
    animeListStatus = ['watching', 'completed', 'dropped', 'on_hold', 'plan_to_watch']
    selectedLimit = '1000'
    print("Downloading my anime data.")
    for myStatus in animeListStatus:
        with open(directoryPath + myStatus + '.json', 'w', encoding='utf-8') as file:
            data = requests.get(myAnimeList, headers={'X-MAL-CLIENT-ID' : malClientID}, params={'status' : myStatus, 'fields' : selectedFields, 'nsfw' : 'true', 'limit' : selectedLimit})
            json.dump(data.json(), file, ensure_ascii=False, indent=4)
            print('\t' + myStatus + " complete...")

def hofAnimeThemeData(themes_tags, directoryPath):
    hof = dict()

    for theme in themes_tags:
        link = f'https://anime.jhiday.net/hof/challenge/{theme}#challengeItems'
        request = requests.get(link)

        if request.status_code != 200:
            print(f'Error connecting to {theme} on HoF')
            continue

        print(f'Connected successfully to {theme} on HoF')
        pageSoup = bs(request.content, "html.parser")

        print('\tGathering data.')
        contentTab = pageSoup.find_all('a', {'href' : '#challengeItems'})
        eligibleItems = pageSoup.find_all('li', {'category' : 'All Series'})

        numberOfExpectedItems = int(contentTab[0].text.strip().split('\n')[1])

        if numberOfExpectedItems != len(eligibleItems):
            print("Number of items obtained does not match expected size. Passing.")
            continue

        print('\tProcessing data.')
        for item in eligibleItems:
            malID = item.find('a', {'class' : 'seriesLink'})['seriesid']

            if malID not in hof.keys():
                hof[malID] = hofAnime(malID, item.text.strip())

            hof[malID].addTheme(theme)

        print('\tStoring data.')
        hofList = []

        for anime in hof.values():
            hofList.append(json.loads(json.dumps(anime.__dict__, ensure_ascii=True)))

        with open(directoryPath + 'hofTheme.json', 'w') as file:
            json.dump(hofList, file, ensure_ascii=4,  indent=4)

        print('\tDone')
    
    return hof