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