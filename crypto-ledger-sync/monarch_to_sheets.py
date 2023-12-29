import gspread
import os
import json
import monarch_client
from google.oauth2 import service_account
import logging
import sys
import asyncio

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')
SHEETS_SPREADSHEET_NAME = os.environ.get('SHEETS_NAME', 'Moseley Investing Strategy')
SHEETS_WORKSHEET_NAME = os.environ.get('SHEETS_WORKSHEET_NAME', "Over Time")

ACCOUNT_NAMES_401K = os.environ.get('ACCOUNT_NAMES_401K').split(':')
ACCOUNT_NAMES_MORTGAGE = os.environ.get('ACCOUNT_NAMES_MORTGAGE').split(':')
ACCOUNT_NAMES_HOUSE = os.environ.get('ACCOUNT_NAMES_HOUSE').split(':')

SHEETS_CELL_401K = os.environ.get('SHEETS_CELL_401K', 'E46')
SHEETS_CELL_MORTGAGE = os.environ.get('SHEETS_CELL_MORTGAGE', 'E47')
SHEETS_CELL_HOUSE = os.environ.get('SHEETS_CELL_HOUSE', 'E48')

def main():
    mm = asyncio.run(monarch_client.get_client())
    sheets = get_sheets_client()

    totals = tabulate_portfolio_totals(asyncio.run(mm.get_accounts()))

    import pprint
    pprint.pprint(totals)
    write_totals_to_sheets(sheets, totals)


def write_totals_to_sheets(sheets_client, totals):
    logging.info("Updating Sheet values")

    spreadsheet = sheets_client.open(SHEETS_SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)

    worksheet.update(range_name=SHEETS_CELL_401K, values=[[totals['401k']]])
    worksheet.update(range_name=SHEETS_CELL_MORTGAGE, values=[[totals['Mortgage']]])
    worksheet.update(range_name=SHEETS_CELL_HOUSE, values=[[totals['House']]])


def get_sheets_client():
    logging.info(f"Connecting to Sheets")

    credentials = service_account.Credentials.from_service_account_info(json.loads(GOOGLE_CREDENTIALS))

    scoped_credentials = credentials.with_scopes([
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])

    return gspread.authorize(scoped_credentials)


def tabulate_portfolio_totals(accounts):
    logging.info(f"Categorizing accounts [total={len(accounts['accounts'])}]")

    working_totals = {
        '401k': 0,
        'Mortgage': 0,
        'House': 0
    }

    for account in accounts['accounts']:
        if account['displayName'] in ACCOUNT_NAMES_401K:
            working_totals['401k'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_HOUSE:
            working_totals['House'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_MORTGAGE:
            working_totals['Mortgage'] += account['currentBalance']

    param_parts = ' | '.join([f"{category} = ${value:,.2f}" for category, value in working_totals.items()])
    logging.info(f"Discovered values: [{param_parts}]")

    return working_totals


if __name__ == '__main__':
    main()
    logging.info("Complete")
