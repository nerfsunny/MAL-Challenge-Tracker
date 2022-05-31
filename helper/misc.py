import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from dotenv import set_key
import os

def storeAnimeUsed(challengeName, runNumber, series):
    with open(f'./export_challenges/{challengeName}/{challengeName}_{runNumber}_animeUsed.txt', 'w') as file:
        for id in series:
            file.write(f'{id}\n')

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