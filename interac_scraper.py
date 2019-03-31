import os.path
import pandas as pd
import pickle
import re
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_interac_payments_from_gmail(mindate=None):
    """

    """
    transactions = pd.DataFrame(columns=['id', 'Payer', 'Amount', 'Date'])
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    query = "from:notify@payments.interac.ca "
    if mindate:
         query += ' after:'+mindate
    results = service.users().messages().list(userId='me',
                                              q=query).execute()
    if 'messages' in results.keys():
        for message_id in results['messages']:
            m = service.users().messages().get(userId="me",
                                               id=message_id['id']).execute()

            snippet = m['snippet']
            whomatch = re.search(', (.*) has sent you an INTERAC e-Transfer.',
                                 snippet)
            who = whomatch.group(1) if whomatch else None
            amountmatch = re.search('Amount: \$(.*) \(CAD\)', snippet)
            amount = float(amountmatch.group(1) if amountmatch else None)
            date = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.gmtime(int(m['internalDate'])/1000))
            g_id = m['id']
            transactions = transactions.append({'id':g_id,
                                                'Payer':who,
                                                'Amount':amount,
                                                'Date':date},
                                                ignore_index=True)
    else:
        print('No messages found.')
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    return transactions

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output",
                    help="Name of output csv.")
parser.add_argument("-d", "--mindate",
                    help="Minidum Date to search", default=None)
args = parser.parse_args()
transactions = get_interac_payments_from_gmail(mindate=args.mindate)
if args.output:
    transactions.to_csv(args.output, index=False)
else:
    print(transactions)
