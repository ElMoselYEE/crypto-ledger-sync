import gspread
import os
import mintapi
import mint_client
from oauth2client.service_account import ServiceAccountCredentials
import logging
import sys
import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')

SHEETS_SPREADSHEET_NAME = os.environ.get('SHEETS_NAME', 'Moseley Investing Strategy')
SHEETS_WORKSHEET_NAME = os.environ.get('SHEETS_WORKSHEET_NAME', "New House")

SHEETS_CELL_SAVINGS = os.environ.get('SHEETS_CELL_SAVINGS', 'C11')
SHEETS_CELL_EQUITY = os.environ.get('SHEETS_CELL_EQUITY', 'C12')


def main():
    mint = mint_client.get_mint_client()
    sheets = get_sheets_client()

    balances = get_portfolio_balances(mint.get_account_data())
    write_balances_to_sheets(sheets, balances)

    mint.close()


def write_balances_to_sheets(sheets_client, balances):
    logging.info("Updating Sheet values")

    spreadsheet = sheets_client.open(SHEETS_SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)

    worksheet.update(SHEETS_CELL_SAVINGS, balances['savings'])
    worksheet.update(SHEETS_CELL_EQUITY, balances['equity'])


def get_sheets_client():
    logging.info(f"Connecting to Sheets")

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(GOOGLE_CREDENTIALS), scopes)
    return gspread.authorize(creds)


def get_portfolio_balances(accounts):
    logging.info(f"Categorizing accounts [total={len(accounts)}]")

    balances = {
        'savings': 0,
        'equity': 0
    }

    for account in accounts:
        if account['name'] == 'Savings':
            balances['savings'] = account['availableBalance']
        if account['name'] == 'Twilio Equity Awards':
            balances['equity'] = account['currentBalance']

    logging.info(f"Discovered values: [{balances}]")

    return balances


if __name__ == '__main__':
    main()
    logging.info("Complete")
