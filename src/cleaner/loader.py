from typing import List
import json
import pandas as pd


def loadFiles(files: List[str]) -> pd.DataFrame:
    data = pd.DataFrame({'endTime': [],
                         'artistName': [],
                         'trackName': [],
                         'msPlayed': []})

    #for filePath in files:
    loadStreamingFile(files[0], data)

    return data


def loadStreamingFile(path: str, dataFrame: pd.DataFrame):
    """
    Load the contents of a json streaming history file and append it to an
    existing pandas dataframe.
    :param path: the file to load
    :param dataFrame: the dataframe to modify
    """

    file = open(path, encoding='utf-8')
    j = json.load(file)
    file.close()

    for listen in j:
        dataFrame.loc[len(dataFrame)] = [
            listen['endTime'],
            listen['artistName'],
            listen['trackName'],
            listen['msPlayed']
        ]
