import Globals
from Function import DataBaseConnection



def get_theChooseCurveData(cursor, choosedCurveName):
    cursor.execute(f'SELECT {choosedCurveName} FROM {Globals.theOpenedWellName}')
    theChooseAction_CurveData = cursor.fetchall()

    return theChooseAction_CurveData

def getDepth(cursor):
    cursor.execute(f'SELECT depth FROM {Globals.theOpenedWellName}')
    depth = cursor.fetchall()

    return depth
