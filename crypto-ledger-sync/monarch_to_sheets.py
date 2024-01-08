import gspread
import os
import json
import monarch_client
from google.oauth2 import service_account
import logging
import sys
import asyncio
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')
SHEETS_SPREADSHEET_NAME = os.environ.get('SHEETS_NAME', 'Moseley Investing Strategy')

ACCOUNT_NAMES_401K = os.environ.get('ACCOUNT_NAMES_401K').split(':')
ACCOUNT_NAMES_MORTGAGE = os.environ.get('ACCOUNT_NAMES_MORTGAGE').split(':')
ACCOUNT_NAMES_HOUSE = os.environ.get('ACCOUNT_NAMES_HOUSE').split(':')
ACCOUNT_NAMES_SAVINGS = os.environ.get('ACCOUNT_NAMES_SAVINGS').split(':')
ACCOUNT_NAMES_EQUITY = os.environ.get('ACCOUNT_NAMES_EQUITY').split(':')
ACCOUNT_NAMES_MONEY_MARKET = os.environ.get('ACCOUNT_NAMES_MONEY_MARKET').split(':')

SHEETS_CELL_401K = os.environ.get('SHEETS_CELL_401K', 'E46')
SHEETS_CELL_MORTGAGE = os.environ.get('SHEETS_CELL_MORTGAGE', 'E47')
SHEETS_CELL_HOUSE = os.environ.get('SHEETS_CELL_HOUSE', 'E48')
SHEETS_CELL_OVER_TIME_UPDATED = os.environ.get('SHEETS_CELL_UPDATED_OVER_TIME', 'B84')

SHEETS_CELL_SAVINGS = os.environ.get('SHEETS_CELL_SAVINGS', 'C3')
SHEETS_CELL_EQUITY = os.environ.get('SHEETS_CELL_EQUITY', 'C5')
SHEETS_CELL_MONEY_MARKET = os.environ.get('SHEETS_CELL_MONEY_MARKET', 'C6')
SHEETS_CELL_HOME_FINANCING_UPDATED = os.environ.get('SHEETS_CELL_UPDATED_HOME_FINANCING', 'B19')

def main():
    mm = asyncio.run(monarch_client.get_client())
    sheets = get_sheets_client()

    totals = tabulate_portfolio_totals(asyncio.run(mm.get_accounts()))

    update_over_time_sheet(sheets, totals)
    update_home_financing_sheet(sheets, totals)


def update_over_time_sheet(sheets_client, totals):
    logging.info("Updating Over Time Sheet values")

    spreadsheet = sheets_client.open(SHEETS_SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet('Over Time')

    worksheet.update(range_name=SHEETS_CELL_401K, values=[[totals['401k']]])
    worksheet.update(range_name=SHEETS_CELL_MORTGAGE, values=[[totals['Mortgage']]])
    worksheet.update(range_name=SHEETS_CELL_HOUSE, values=[[totals['House']]])

    worksheet.update(range_name=SHEETS_CELL_OVER_TIME_UPDATED, values=[["Updated " + datetime.now().strftime("%B %-d, %Y")]])

def update_home_financing_sheet(sheets_client, totals):
    logging.info("Updating Home Financing Sheet values")

    spreadsheet = sheets_client.open(SHEETS_SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet('Home Financing')

    worksheet.update(range_name=SHEETS_CELL_SAVINGS, values=[[totals['Savings']]])
    worksheet.update(range_name=SHEETS_CELL_EQUITY, values=[[totals['Equity']]])
    worksheet.update(range_name=SHEETS_CELL_MONEY_MARKET, values=[[totals['Money Market']]])

    worksheet.update(range_name=SHEETS_CELL_HOME_FINANCING_UPDATED,
                     values=[["Updated " + datetime.now().strftime("%B %-d, %Y")]])


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
        'House': 0,
        'Savings': 0,
        'Equity': 0,
        'Money Market': 0,
    }

    for account in accounts['accounts']:
        if account['displayName'] in ACCOUNT_NAMES_401K:
            working_totals['401k'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_HOUSE:
            working_totals['House'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_MORTGAGE:
            working_totals['Mortgage'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_SAVINGS:
            working_totals['Savings'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_EQUITY:
            working_totals['Equity'] += account['currentBalance']
        if account['displayName'] in ACCOUNT_NAMES_MONEY_MARKET:
            working_totals['Money Market'] += account['currentBalance']

    param_parts = ' | '.join([f"{category} = ${value:,.2f}" for category, value in working_totals.items()])
    logging.info(f"Discovered values: [{param_parts}]")

    return working_totals


if __name__ == '__main__':
    main()
    logging.info("Complete")
