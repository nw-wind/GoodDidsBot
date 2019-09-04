import traceback

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from oauth2client import tools

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SECRET_FILE = 'client_secret.json'
#APPLICATION_NAME = 'changes tracking'
APPLICATION_NAME = 'gooddidsbot'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    print("Cred dir = '{}'".format(credential_dir))
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
        print("made")
    credential_path = os.path.join(credential_dir,
                                   SECRET_FILE)

    print("Path='{}'".format(credential_path))
    store = Storage(credential_path)
    print("store={}".format(repr(store)))
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def build_request():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    return discovery.build('sheets', 'v4', http=http,
                           discoveryServiceUrl=discoveryUrl)


# взять sheetid по имени таблицы
def get_sheetid_by_tablename(spreadsheetid, table):
    service = build_request()
    meta = service.spreadsheets().get(spreadsheetId=spreadsheetid).execute()
    sheets = meta.get('sheets', [])
    for sheet in sheets:
        title = sheet.get("properties", {}).get("title", "")
        sheet_id = sheet.get("properties", {}).get("sheetId", 0)
        if table == title:
            return sheet_id


# создать таблицу
def create_sheet(spreadsheetid, name):
    service = build_request()
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": name
                    }
                }
            }
        ]
    }
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetid, body=body)
    try:
        execute = request.execute()
        return execute
    except Exception as e:
        pass
        # traceback.print_exc(e)
        # print(e)


def add_line(spreadsheetid, sheetname, line):
    # line-- массив значений пример [1,2,3,4,5]
    service = build_request()
    body = {
        # "valueInputOption": "USER_ENTERED",
        "range": sheetname,
        # "majorDimension": enum(Dimension),
        "values": [line]
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheetid, range=sheetname,
                                                     body=body, valueInputOption="USER_ENTERED",
                                                     includeValuesInResponse=True)
    return request.execute()


# взять список листов
def get_sheets(spreadsheetid):
    service = build_request()
    meta = service.spreadsheets().get(spreadsheetId=spreadsheetid).execute()
    sheets = meta.get('sheets', [])
    return sheets


# взять все значения таблицы
def get_all_values(spreadsheet, sheetname):
    service = build_request()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet, range=sheetname).execute()
    values = result.get('values', [])
    res = []
    i = 1
    for row in values:
        res.append({"row": row, "num": i})
        i += 1
    return res


def getrowsandcolsofspread(spreadsheet, sheetname):
    service = build_request()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet, range=sheetname).execute()
    values = result.get('values', [])
    columns = 0
    rows = len(values)
    if rows > 0:
        columns = len(values[0])
    return {"sheetname": sheetname, "rows": rows, "columns": columns, "spreadsheet": spreadsheet}


def batchupdate_with_body(spreadsheetid, body):
    service = build_request()
    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetid,
                                                          body=body)
    try:
        request.execute()
    except:
        traceback.print_exc()


def deleterowsbyrange(spreadsheetid, range):
    service = build_request()
    clear_values_request_body = {
        # TODO: Add desired entries to the request body.
    }

    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheetid, range=range,
                                                    body=clear_values_request_body)
    return request.execute()

