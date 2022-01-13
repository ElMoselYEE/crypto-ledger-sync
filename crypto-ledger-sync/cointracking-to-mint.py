import mintapi
import json
import requests
import re
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# e.g. https://cointracking.info/ajax/portfolio_current_balance.php?portfolio=12345678901234567812&fiat=0
COINTRACKER_DATA_URL = os.environ.get('COINTRACKER_DATA_URL')
MINT_USERNAME = os.environ.get('MINT_USERNAME')
MINT_PASSWORD = os.environ.get('MINT_PASSWORD')
MFA_METHOD = os.environ.get('MFA_METHOD')
MFA_TOKEN = os.environ.get('MFA_TOKEN')
MINT_CRYPTO_ACCOUNT_PREFIX = os.environ.get('MINT_CRYPTO_ACCOUNT_PREFIX')


def main():
    portfolio = get_cointracking_portfolio_data()

    mint = get_mint_client()
    accounts = get_slimmed_accounts(mint)

    for account_name in accounts.keys():
        if MINT_CRYPTO_ACCOUNT_PREFIX in account_name:
            cur_account = accounts[account_name]

            ticker = account_name[account_name.index(' - ') + 3:]
            if ticker in portfolio:
                new_value = float(portfolio[ticker])
                update_account_value(mint, cur_account, new_value)


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


def get_slimmed_accounts(mint):
    logging.info("Fetching account data")

    providers = mint.get_providers()

    accounts_slimmed = {}

    for provider in providers:
        for account in provider['providerAccounts']:
            for link in account['metaData']['link']:
                if link['operation'] == 'updateAccount':
                    accounts_slimmed[account['name']] = {
                        'id': account['id'],
                        'name': account['name'],
                        'type': account['type'],
                        'updateAccountHref': link['href'],
                        'propertyValue': account.get('propertyValue', None),
                        'otherPropertyType': account.get('otherPropertyType', None)
                    }

    return accounts_slimmed


def update_account_value(mint, account, new_value):
    logging.info(f"Updating balance: {account['name']} was ${account['propertyValue']} is now worth ${new_value}")

    headers = mint._get_api_key_header()
    headers['content-type'] = 'application/json'

    logging.debug(f"PATCH {mintapi.api.MINT_ROOT_URL}/mas{account['updateAccountHref']}")
    response = mint.patch(
        f"{mintapi.api.MINT_ROOT_URL}/mas{account['updateAccountHref']}",
        headers=headers,
        data=json.dumps({
            "name": account['name'],
            "value": new_value,
            "associatedLoanAccounts": [],
            "hasAssociatedLoanAccounts": False,
            "type": account['type']
        })
    )

    if response.status_code != 204:
        logging.error(f"ERROR {response.status_code}: {response.content.decode('utf-8')}")


def map_currency(currency):
    if currency == 'DOT2':
        return 'DOT'

    return currency


def get_cointracking_portfolio_data():
    logging.info("Downloading from CoinTracking")

    coin_data = json.loads(requests.get(COINTRACKER_DATA_URL).text)

    portfolio = {}

    for data in coin_data['data']:
        symbol_search = re.search(">([A-Z0-9]*)</a>", data['c'])

        if symbol_search is not None:
            symbol = map_currency(data['c'][symbol_search.start() + 1:symbol_search.end() - 4])

            portfolio[symbol] = data['f']

    return portfolio


if __name__ == '__main__':
    main()
