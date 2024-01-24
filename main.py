import os.path
import urllib.request
import json
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# need to run above in cmd

def getClanTag():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    with open("spreadsheet_id.txt") as f:
        SPREADSHEET_ID = f.read().rstrip("\n")


    """
    Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        clan_tag = str(sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range=f'Sheet1!A55').execute().get('values')[0][0])

        return clan_tag

    except HttpError as err:
        print(err)


def readClashData(clan_tag):
    clan_tag = "%23" + clan_tag
    with open("clash_key.txt") as f:
        clash_key = f.read().rstrip("\n")

        base_url = "https://api.clashroyale.com/v1"

        endpoint = f"/clans/{clan_tag}/members"

        request = urllib.request.Request(
            base_url + endpoint,
            None,
            {
                "Authorization": "Bearer %s" % clash_key
            }
        )

        response = urllib.request.urlopen(request).read().decode("utf-8")

        clan_data = json.loads(response)

        endpoint = f"/clans/{clan_tag}/riverracelog?limit=10"

        request = urllib.request.Request(
            base_url + endpoint,
            None,
            {
                "Authorization": "Bearer %s" % clash_key
            }
        )

        response = urllib.request.urlopen(request).read().decode("utf-8")

        riverrace_log = json.loads(response)

        data = [clan_data, riverrace_log]

        return data


# Organizes JSON data into a list
def organizeData(data, clan_tag):
    sheet_list = [["Name", "Trophies", "Points", "Avg Points", "Weeks", "Donations", "Donations Received"]]
    for i in range(1, 51):
        sheet_list.append(["---", "---", "---", "---", "---", "---", "---"])

    count = 0
    for item in data[0]["items"]:
        count += 1
        # Add Name, Trophies, Donations, and Donations Received
        sheet_list[count][0] = item["name"]
        sheet_list[count][1] = item["trophies"]
        sheet_list[count][5] = item["donations"]
        sheet_list[count][6] = item["donationsReceived"]

        # Get the was data for Points, Avg Points, and Weeks
        points = 0
        weeks = 0
        for war in data[1]["items"]:
            for participant in war["standings"][0]["clan"]["participants"]:
                if participant["tag"] == item["tag"] and war["standings"][0]["clan"]["tag"][1:] == clan_tag:
                    weeks += 1
                    points += participant["fame"]
            for participant in war["standings"][1]["clan"]["participants"]:
                if participant["tag"] == item["tag"] and war["standings"][1]["clan"]["tag"][1:] == clan_tag:
                    weeks += 1
                    points += participant["fame"]
            for participant in war["standings"][2]["clan"]["participants"]:
                if participant["tag"] == item["tag"] and war["standings"][2]["clan"]["tag"][1:] == clan_tag:
                    weeks += 1
                    points += participant["fame"]
            for participant in war["standings"][3]["clan"]["participants"]:
                if participant["tag"] == item["tag"] and war["standings"][3]["clan"]["tag"][1:] == clan_tag:
                    weeks += 1
                    points += participant["fame"]
            for participant in war["standings"][4]["clan"]["participants"]:
                if participant["tag"] == item["tag"] and war["standings"][4]["clan"]["tag"][1:] == clan_tag:
                    weeks += 1
                    points += participant["fame"]


        sheet_list[count][2] = points
        if weeks != 0:
            sheet_list[count][3] = round(points / weeks)
        else:
            sheet_list[count][3] = points
        sheet_list[count][4] = weeks

    print(sheet_list)
    return sheet_list


def updateGoogleSheets(sheet_list):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    with open("spreadsheet_id.txt") as f:
        SPREADSHEET_ID = f.read().rstrip("\n")

    """
    Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        for row in range(0, 51):
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!A{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][0]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!B{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][1]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!C{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][2]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!D{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][3]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!E{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][4]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!F{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][5]]]}).execute()
            time.sleep(1)
            sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                  range=f'Sheet1!G{row+1}', valueInputOption='USER_ENTERED',
                                  body={'values': [[sheet_list[row][6]]]}).execute()
            time.sleep(1.05)

    except HttpError as err:
        print(err)


def main():
    print("Updating Clan Data Sheet...")
    clan_tag = getClanTag()
    # data is [clan_data, riverrace_log]
    data = readClashData(clan_tag)
    sheet_list = organizeData(data, clan_tag)
    updateGoogleSheets(sheet_list)
    print("Done!")




if __name__ == '__main__':
    main()
