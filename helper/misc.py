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

def extractDataColumn(listOfDicts, colName):
    extract = []

    for genre in listOfDicts:
        extract.append(genre['name'])

    return extract

def loadMALJSONIntoDF(json, nodeColumns, listStatusColumns, df):
    specialInstructionsCols = ['genres', 'studios']
    
    if list(df.columns) != (nodeColumns + listStatusColumns):
        raise ValueError('Columns in given DataFrame do not match columns the result of combining nodeColumns and listStatusColumns.')

    row = {}
    for animeNode in json['data']:
        animeInfo = animeNode['node']

        for selectedColumn in nodeColumns:
            if selectedColumn in specialInstructionsCols:
                row[selectedColumn] = extractDataColumn(animeInfo[selectedColumn], "name")
            else:
                row[selectedColumn] = animeInfo[selectedColumn]

        myListInfo = animeNode['list_status']

        for selectedColumn in listStatusColumns:
            if selectedColumn not in myListInfo.keys():
                row[selectedColumn] = "N/A"
            else:
                row[selectedColumn] = myListInfo[selectedColumn]

        df = pd.concat([df, pd.DataFrame.from_dict(row, orient='index').transpose()], ignore_index=True)
        row.clear()

    return df

def createHOFDF(hofThemeJSONFile, myMALDF):
    hofThemeDF = pd.DataFrame.from_records(hofThemeJSONFile)
    hofThemeDF = hofThemeDF.astype({'mal_id' : 'int64', 'name' : 'string'})
    myHOFDF = pd.merge(hofThemeDF[['mal_id', 'themes']], myMALDF[['mal_id', 'title', 'status', 'finish_date', 'color', 'label']], how='inner', left_on='mal_id', right_on='mal_id')
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

def summaryOfChallenge(challenge_name, difficulty, numberOfExpectedItems, animeDF):
    numberOfCompleted = len(animeDF.index[animeDF['status'] == 'completed'])
    new_row = pd.DataFrame({'challenge_name' : challenge_name, 
                            'progress' : f'{min(numberOfCompleted, numberOfExpectedItems)}/{numberOfExpectedItems}', 
                            'difficulty' : difficulty, 
                            'items_added' : 'N/A',
                            'items_removed' : 'N/A',
                            'update' : 'N/A',
                            'complete' : str(numberOfCompleted == numberOfExpectedItems)}, 
                            index=[0])

    return new_row

def storeAnimeUsed(parent_path, challenge_name, animeDF):
    with open(f'{parent_path}/{challenge_name}/{challenge_name}_used.txt', 'w') as file:
        for id in animeDF['mal_id']:
            file.write(f'{id}\n')