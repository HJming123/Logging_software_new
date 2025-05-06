import Globals
from Function import DataBaseConnection

def get_theChooseAction_CurveData(chooseActionTitle):
    connection = DataBaseConnection.connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f'SELECT {chooseActionTitle} FROM {Globals.theOpenedWellName}')
    theChooseAction_CurveData = cursor.fetchall()

    cursor.close()
    connection.close()

    return theChooseAction_CurveData

def getDepth():
    connection = DataBaseConnection.connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f'SELECT depth FROM {Globals.theOpenedWellName}')
    depth = cursor.fetchall()
    cursor.close()
    connection.close()

    return depth

def getTableHeaders():
    connection = DataBaseConnection.connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    cursor.close()
    connection.close()

    return column_names