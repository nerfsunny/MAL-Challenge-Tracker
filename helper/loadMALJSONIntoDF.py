import pandas as pd

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