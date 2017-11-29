from __future__ import print_function
import httplib2
import os
import string

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from copy import copy
from time import sleep

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
sheet_names = ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Round 6", "Round 7", "Round 8", "Round 9", "Round 10", "Round 11" , "Round 12", "Round 13", "Round 14" , "Round 15", "Round 16"]#, "Finals/Emergency", "Finals 2/Emergency"]
left_col = ["=CONCAT(\"A BP: \",IMPORTRANGE(\"{}\",\"{}!I32\"))", "=CONCAT(\"B BP: \",IMPORTRANGE(\"{}\",\"{}!S32\"))", "TUH", "15", "10", "-5", "Total", "=IMPORTRANGE(\"{}\",\"{}!W1\")"]
team_a_range = "{}!C1:H3"
team_b_range = "{}!M1:R3"
indiv_a_range = "{}!C32:H36"
indiv_b_range = "{}!M32:R36"
importrange_fstring = "={{IMPORTRANGE(\"{}\",\"{}\"),IMPORTRANGE(\"{}\",\"{}\")}}"


def get_gridRange(A1, i):
    col = A1[0]
    row = int(A1[1:])
    d = {i:string.ascii_uppercase.index(i) for i in string.ascii_uppercase}
    return {"sheetId" : i, "startRowIndex" : row -1, "endRowIndex" : row, "startColumnIndex" : d[col], "endColumnIndex": d[col] + 1}

def get_rooms():
    d = {}
    while True:
        inp = input("room number: ")
        if(len(inp) == 0):
            break
        else:
            d[inp] = ""
    return d

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

master_scoresheet_id = input("Master scoresheet id: ")
master_agg_id = input("Master aggregate id: ")
master_roster_id = input("Master roster id: ")


gauth = GoogleAuth()
try:
    #if(os.path.exists("creds.json")):
        gauth.LoadCredentialsFile("creds.json")
        gauth.Authorize()
except:
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("creds.json")
drive = GoogleDrive(gauth)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


rooms = get_rooms()
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                'version=v4')
service = discovery.build('sheets', 'v4', http=http,
                          discoveryServiceUrl=discoveryUrl)


c = drive.auth.service.files().copy(fileId=master_agg_id, body={"title": "Aggregate Scoresheets"}).execute()
agg_id = c["id"]

for room in rooms:
        c = drive.auth.service.files().copy(fileId=master_scoresheet_id, body={"title": room}).execute()
        rooms[room] = c["id"]

k = 0
for name in sheet_names:
        i = 1
        for room in sorted(rooms):
                left_col_fmted = copy(left_col)
                left_col_fmted.insert(0, room)
                left_col_fmted[1] = left_col_fmted[1].format(rooms[room], name)
                left_col_fmted[2] = left_col_fmted[2].format(rooms[room], name)
                left_col_fmted[8] = left_col_fmted[8].format(rooms[room], name)
                data = [{"range": name+"!A{}:A{}".format(i, i+9), "values":[left_col_fmted]}, {"range": name+"!B{}".format(i), "values":[[importrange_fstring.format(rooms[room], team_a_range.format(name), rooms[room], team_b_range.format(name))]]},{"range": name+"!B{}".format(i+3), "values":[[importrange_fstring.format(rooms[room], indiv_a_range.format(name), rooms[room], indiv_b_range.format(name))]]}]
                data.append({"range": name + "!B{}".format(i+8),"values":[["https://docs.google.com/spreadsheets/d/{}/edit".format(rooms[room])]]})
                d = {}
                for j in data:
                        j["majorDimension"] = "COLUMNS"
                d["data"] = data
                d["valueInputOption"] = "USER_ENTERED"
                res = service.spreadsheets().values().batchUpdate(spreadsheetId=agg_id, body=d).execute()
                i += 10
        sleep(5)
        print("Finished: "  + name)
print("Finished aggregation")

TEAM_A = "C1"
TEAM_B = "M1"
TEAMS = "X4"
A_ROSTERS = "Y4"
B_ROSTERS = "Z4"
A_PLAYERS = ["C3","D3","E3","F3","G3","H3"]
B_PLAYERS = ["M3","N3","O3","P3","Q3","R3"]

data = [{"range": "Rosters!A1", "values":[["=IMPORTRANGE(\"{}\", \"Rosters!A:G\")".format(master_roster_id)]]}]
for s in sheet_names:
    data.append({"range":"{}!{}".format(s, A_ROSTERS), "values":[["=TRANSPOSE(FILTER(Rosters!B:G, Rosters!A:A = C1))"]]})
    data.append({"range":"{}!{}".format(s, B_ROSTERS), "values":[["=TRANSPOSE(FILTER(Rosters!B:G, Rosters!A:A = M1))"]]})
    data.append({"range":"{}!{}".format(s, TEAMS), "values":[["=ARRAYFORMULA(Rosters!A:A)"]]})

d = {}
for j in data:
        j["majorDimension"] = "COLUMNS"
d["data"] = data
d["valueInputOption"] = "USER_ENTERED"
for i in rooms:
    res = service.spreadsheets().values().batchUpdate(spreadsheetId=rooms[i], body=d).execute()

sheetIds = {}
for i in rooms:
	a = []
	b = service.spreadsheets().get(spreadsheetId=rooms[i]).execute()
	for j in b["sheets"]:
		a.append(j["properties"]["sheetId"])
	sheetIds[i] = a


def j():
    for i in rooms:
        request = []
        k = 0
        for sheetname in sheet_names:
            for A in A_PLAYERS:
                dropdown_action = {
                    'setDataValidation':{
                        'range':
                            get_gridRange(A, sheetIds[i][k])
                        ,
                        'rule':{
                            'condition':{
                                'type':'ONE_OF_RANGE', 
                                'values': [
                                    { "userEnteredValue" : "=Y:Y"
                                    }
                                ],
                            },
                            'inputMessage' : 'Choose one from dropdown',
                            'showCustomUi': True
                        }

                    }
                }
                request.append(dropdown_action)
            for B in B_PLAYERS:
                dropdown_action = {
                    'setDataValidation':{
                        'range':
                            get_gridRange(B, sheetIds[i][k])
                        ,
                        'rule':{
                            'condition':{
                                'type':'ONE_OF_RANGE', 
                                'values': [
                                    { "userEnteredValue" : "=Z:Z"
                                    }
                                ],
                            },
                            'inputMessage' : 'Choose one from dropdown',
                            'showCustomUi': True
                        }

                    }
                }
                request.append(dropdown_action)
            dropdown_action = {
                'setDataValidation':{
                    'range':
                        get_gridRange(TEAM_A, sheetIds[i][k])
                    ,
                    'rule':{
                        'condition':{
                            'type':'ONE_OF_RANGE', 
                            'values': [
                                { "userEnteredValue" : "=X:X"
                                }
                            ],
                        },
                        'inputMessage' : 'Choose one from dropdown',
                        'showCustomUi': True
                    }

                }
            }
            request.append(dropdown_action)
            dropdown_action = {
                'setDataValidation':{
                    'range':
                        get_gridRange(TEAM_B, sheetIds[i][k])
                    ,
                    'rule':{
                        'condition':{
                            'type':'ONE_OF_RANGE', 
                            'values': [
                                { "userEnteredValue" : "=X:X"
                                }
                            ],
                        },
                        'inputMessage' : 'Choose one from dropdown',
                        'showCustomUi': True
                    }

                }
            }
            request.append(dropdown_action)
            k+=1

        #print(request)
        batchUpdateRequest = {'requests': request}
        service.spreadsheets().batchUpdate(spreadsheetId = rooms[i], body = batchUpdateRequest).execute()


j()
print("Finished Rosters")
"""
for i in rooms:
    a = service.spreadsheets().sheets().copyTo(spreadsheetId=master_roster_id, sheetId="0", body={"destinationSpreadsheetId": rooms[i]}).execute()
"""
