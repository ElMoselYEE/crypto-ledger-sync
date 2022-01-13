import gspread
import os
import mintapi
from oauth2client.service_account import ServiceAccountCredentials
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MINT_USERNAME = os.environ.get('MINT_USERNAME')
MINT_PASSWORD = os.environ.get('MINT_PASSWORD')
MFA_METHOD = os.environ.get('MFA_METHOD')
MFA_TOKEN = os.environ.get('MFA_TOKEN')
CREDENTIAL_KEYFILE = os.environ.get('CREDENTIAL_KEYFILE')
SHEETS_SPREADSHEET_NAME = os.environ.get('SHEETS_NAME', 'Moseley Investing Strategy')
SHEETS_WORKSHEET_NAME = os.environ.get('SHEETS_WORKSHEET_NAME', "Over Time")

ACCOUNT_NAMES_401K = os.environ.get('ACCOUNT_NAMES_401K').split(':')
ACCOUNT_NAMES_MORTGAGE = os.environ.get('ACCOUNT_NAMES_MORTGAGE').split(':')
ACCOUNT_NAMES_HOUSE = os.environ.get('ACCOUNT_NAMES_HOUSE').split(':')
ACCOUNT_NAMES_BITCOIN = os.environ.get('ACCOUNT_NAMES_BITCOIN').split(':')
ACCOUNT_NAMES_SCP = os.environ.get('ACCOUNT_NAMES_SCP').split(':')
ACCOUNT_NAMES_DEFI = os.environ.get('ACCOUNT_NAMES_DEFI').split(':')
ACCOUNT_NAMES_RESERVES = os.environ.get('ACCOUNT_NAMES_RESERVES').split(':')

SHEETS_CELL_401K = os.environ.get('SHEETS_CELL_401K', 'E46')
SHEETS_CELL_MORTGAGE = os.environ.get('SHEETS_CELL_MORTGAGE', 'E47')
SHEETS_CELL_HOUSE = os.environ.get('SHEETS_CELL_HOUSE', 'E48')
SHEETS_CELL_BITCOIN = os.environ.get('SHEETS_CELL_BITCOIN', 'E54')
SHEETS_CELL_SCP = os.environ.get('SHEETS_CELL_SCP', 'E55')
SHEETS_CELL_DEFI = os.environ.get('SHEETS_CELL_DEFI', 'E56')
SHEETS_CELL_RESERVES = os.environ.get('SHEETS_CELL_RESERVES', 'E58')


def main():
    mint = get_mint_client()

    totals = tabulate_portfolio_totals(mint.get_accounts())

    sheets = get_sheets_client()

    write_totals_to_sheets(sheets, totals)

    mint.close()


def write_totals_to_sheets(sheets_client, totals):
    logging.info("Updating Sheet values")

    spreadsheet = sheets_client.open(SHEETS_SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)

    worksheet.update(SHEETS_CELL_401K, totals['401k'])
    worksheet.update(SHEETS_CELL_MORTGAGE, totals['Mortgage'])
    worksheet.update(SHEETS_CELL_HOUSE, totals['House'])
    worksheet.update(SHEETS_CELL_BITCOIN, totals['BTC'])
    worksheet.update(SHEETS_CELL_SCP, totals['Smart Contracts'])
    worksheet.update(SHEETS_CELL_DEFI, totals['DeFi'])
    worksheet.update(SHEETS_CELL_RESERVES, totals['Reserves'])


def get_sheets_client():
    logging.info(f"Connecting to Sheets")

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_KEYFILE, scopes)
    return gspread.authorize(creds)


def get_mint_client():
    logging.info(f"Connecting to Mint [username={MINT_USERNAME} | mfa_method={MFA_METHOD}]")

    return mintapi.Mint(
        MINT_USERNAME,
        MINT_PASSWORD,
        mfa_method=MFA_METHOD,
        mfa_token=MFA_TOKEN,
        headless=True,
        use_chromedriver_on_path=True
    )


def tabulate_portfolio_totals(accounts):
    logging.info(f"Categorizing accounts [total={len(accounts)}]")

    working_totals = {
        '401k': 0,
        'Mortgage': 0,
        'House': 0,
        'BTC': 0,
        'Smart Contracts': 0,
        'DeFi': 0,
        'Reserves': 0
    }

    for account in accounts:
        if account['name'] in ACCOUNT_NAMES_401K:
            working_totals['401k'] += account['value']
        if account['name'] in ACCOUNT_NAMES_HOUSE:
            working_totals['House'] += account['value']
        if account['name'] in ACCOUNT_NAMES_MORTGAGE:
            working_totals['Mortgage'] += account['value']
        if account['name'] in ACCOUNT_NAMES_BITCOIN:
            working_totals['BTC'] += account['value']
        if account['name'] in ACCOUNT_NAMES_SCP:
            working_totals['Smart Contracts'] += account['value']
        if account['name'] in ACCOUNT_NAMES_DEFI:
            working_totals['DeFi'] += account['value']
        if account['name'] in ACCOUNT_NAMES_RESERVES:
            working_totals['Reserves'] += account['value']

    param_parts = ' | '.join([f"{category} = ${value:,.2f}" for category, value in working_totals.items()])
    logging.info(f"Discovered values: [{param_parts}]")

    return working_totals


if __name__ == '__main__':
    main()
    logging.info("Complete")
