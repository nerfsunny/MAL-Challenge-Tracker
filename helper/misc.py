import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from dotenv import set_key
import os

def canUpdateData(envFile, envVariable, date_format, incNumberOfWeeks):
    importDate = dt.datetime.strptime(os.getenv(envVariable), date_format).date()
    currentDate = dt.date.today()

    if currentDate > importDate:
        print(f'Can update data. Incrementing import date by {incNumberOfWeeks} weeks.')
        set_key(envFile, envVariable, (dt.date.today() + relativedelta(weeks=+incNumberOfWeeks)).strftime(date_format))
        return True

    print(f'Cannot update data. Next scheduled update is {importDate}')
    return False

def loadMALJSON_DF(jsonFile, itemInfo, userListInfo):
    specialColumns = ['genres', 'studios']

    if 'start_date' in itemInfo:
        itemInfo[itemInfo.index('start_date')] = 'publish_start_date'

    if 'end_date' in itemInfo:
        itemInfo[itemInfo.index('end_date')] = 'publish_end_date'

    df = pd.DataFrame(columns=itemInfo + userListInfo)

    df_row = {}
    for jsonData in jsonFile['data']:
        itemNode = jsonData['node']
        myListItemNode = jsonData['list_status']

        for info in itemInfo:
            if info in specialColumns:
                expandEntry = []

                for info2 in itemNode[info]:
                    expandEntry.append(info2['name'])

                df_row[info] = expandEntry
            elif info == 'publish_start_date' or info == 'publish_end_date':
                if info[8:] not in itemNode:
                    df_row[info] = 'N/A'
                else:
                    df_row[info] = itemNode[info[8:]]
            elif info not in itemNode:
                df_row[info] = 'N/A'
            else:
                df_row[info] = itemNode[info]

        for info in userListInfo:
            if info not in myListItemNode:
                df_row[info] = 'N/A'
            else:
                df_row[info] = myListItemNode[info]
            
        df = pd.concat([df, pd.DataFrame.from_dict(df_row, orient='index').transpose()], ignore_index=True)
    return df

def createHOFDF(hofThemeJSONFile, myMALDF):
    hofThemeDF = pd.DataFrame.from_records(hofThemeJSONFile)
    hofThemeDF = hofThemeDF.astype({'mal_id' : 'int64', 'name' : 'string'})
    myHOFDF = pd.merge(hofThemeDF[['mal_id', 'themes']], myMALDF[['id', 'title', 'status', 'finish_date', 'color', 'label']], how='inner', left_on='mal_id', right_on='id').drop(columns='id')
    return myHOFDF

def eligibleItems_Theme(myHOFThemeDF, theme, challengeStartDate):
    eligibleItems = myHOFThemeDF
    eligibleItems.drop(index=eligibleItems.index[eligibleItems['finish_date'] == 'N/A'].intersection(eligibleItems.index[eligibleItems['status'] == 'completed']), inplace=True)
    eligibleItems.drop(index=eligibleItems.index[eligibleItems['finish_date'] < challengeStartDate].intersection(eligibleItems.index[eligibleItems['status'] == 'completed']), inplace=True)
    eligibleItems = eligibleItems.explode('themes', ignore_index=True)
    eligibleItems.drop(index=eligibleItems.index[eligibleItems['themes'] != theme], inplace=True)

    eligibleItems.sort_values('finish_date', inplace=True, ignore_index=True)

    eligibleItems.loc[eligibleItems['status'] == 'completed', ['color', 'label']] = 'green', 'o'
    eligibleItems.loc[eligibleItems['status'] == 'watching', ['color', 'label']] = 'orange', 'x'
    eligibleItems.drop(columns=['themes'], inplace=True)

    return eligibleItems

def specificStudios(myAnimeDF, studio, set=-1):
    studioDF = myAnimeDF.explode('studios', ignore_index=True)
    studioDF.drop(index=studioDF.index[studioDF['studios'] != studio], columns=['genres', 'rating', 'start_date'], inplace=True)

    naItems = studioDF.loc[studioDF['finish_date'] == 'N/A']
    studioDF.drop(index=naItems.index, inplace=True)

    studioDF.sort_values('finish_date', inplace=True, ascending=True, ignore_index=True)
    studioDF = pd.concat([naItems, studioDF], ignore_index=True)

    studioDF.loc[studioDF['status'] == 'completed', ['color', 'label']] = 'green', 'o'
    studioDF.loc[studioDF['status'] == 'watching', ['color', 'label']] = 'orange', 'x'

    if set == 1:
        studioDF['difficulty'] = 'N/A'

        for row in range(0, min(201, studioDF.shape[0])):
            if row <= 19:
                studioDF.loc[row, 'difficulty'] = 'easy'
            elif row <= 59:
                studioDF.loc[row, 'difficulty'] = 'medium'
            elif row <= 119:
                studioDF.loc[row, 'difficulty'] = 'hard'
            elif row <= 200:
                studioDF.loc[row, 'difficulty'] = 'conquered'
            else:
                studioDF.loc[row, 'difficulty'] = 'N/A'

    return studioDF

def summaryOfChallenge(challenge_name, difficulty, numberOfExpectedItems, animeDF):
    numberOfCompleted = len(animeDF.index[animeDF['status'] == 'completed'])
    new_row = pd.DataFrame({'challenge_name' : challenge_name, 
                            'progress' : f'{min(numberOfCompleted, numberOfExpectedItems)}/{numberOfExpectedItems}', 
                            'difficulty' : difficulty, 
                            'update' : 'N/A',
                            'complete' : str(numberOfCompleted == numberOfExpectedItems)}, 
                            index=[0])

    return new_row

def storeAnimeUsed(parent_path, challenge_name, animeDF):
    with open(f'{parent_path}/{challenge_name}/{challenge_name}_used.txt', 'w') as file:
        for id in animeDF['mal_id']:
            file.write(f'{id}\n')

def combineMALDFs(malDF1, malDF2):
    return pd.concat([malDF1, malDF2], ignore_index=True)