import csv
import mintapi
import mint_client
import os.path
import os
import urllib.parse
from datetime import datetime
import logging
import glob
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MERCHANT_MAPPINGS_FILE = '/data/mint-merchant-categories.csv'
CDC_TRANSACTIONS_GLOB = "/data/card_transactions_record*.csv"
CATEGORY_MAPPINGS_TXT = '/data/mint-categories.txt'
UNCATEGORIZED_CATEGORY_ID = '20'


def main():
    logging.info(f"Reading merchant mapping file {MERCHANT_MAPPINGS_FILE}")
    with open(MERCHANT_MAPPINGS_FILE) as csvfile:
        mappings = list(csv.reader(csvfile))

    mint = mint_client.get_mint_client()

    for file in glob.glob(CDC_TRANSACTIONS_GLOB):
        process_file(file, mint, mappings)

    mint.close()

    logging.info(f"Updating merchant mapping file {MERCHANT_MAPPINGS_FILE}")
    with open(MERCHANT_MAPPINGS_FILE, 'w') as mapping_fh:
        for mapping in mappings:
            mapping_fh.write(f"{mapping[0]},{mapping[1]}\n")


def fill_in_merchant_category(transaction, mappings):
    merchant = transaction[1]
    merchant_category = get_merchant_category(mappings, merchant)

    if merchant_category is None:
        print(transaction)

        pattern = input(f"What is the identifying substring for '{merchant}'? ").strip()
        if len(pattern) <= 2:
            pattern = merchant

        print(''.join(open(CATEGORY_MAPPINGS_TXT).readlines()))
        input_category = input(f"What category ID do you want to assign to '{pattern}'? ").strip()

        if len(input_category) > 0:
            mappings.append((input_category, pattern))
            transaction.append(input_category)
        else:
            print(f"Merchant {merchant} will be uncategorized")
            transaction.append(UNCATEGORIZED_CATEGORY_ID)
    else:
        transaction.append(merchant_category)


def write_transactions_to_mint(mint, transactions):
    for transaction in transactions:
        payload = {
            'cashTxnType': 'on',
            'mtCheckNo': '',
            'tag1548116': '0',
            'tag809992': '0',
            'tag809994': '0',
            'task': 'txnadd',
            'txnId': ':0',
            'mtType': 'cash',
            'mtAccount': '8054108',
            'symbol': '',
            'note': 'Synced from Crypto.com account',
            'isInvestment': 'false',
            'catId': str(transaction[10]),
            'merchant': transaction[1],
            'date': datetime.fromisoformat(transaction[0]).strftime('%m/%d/%Y'),
            'amount': transaction[3],
            'token': mint.token
        }

        if float(transaction[3]) > 0:
            payload.update({
                'mtIsExpense': 'false',
                'mtCashSplitPref': '1',
                'mtCashSplit': 'on',
            })
        else:
            payload.update({
                'mtIsExpense': 'true',
                'mtCashSplitPref': '2',
            })

        logging.info(f"Writing transaction: {payload['date']} {payload['merchant']} for {payload['amount']}...")
        response = mint.post(
            f'{mintapi.api.MINT_ROOT_URL}/updateTransaction.xevent',
            data='&'.join([f'{key}={urllib.parse.quote_plus(val)}' for key, val in payload.items()]),
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        if response.status_code != 200:
            logging.warning(response)
            logging.error(response.text)


def process_file(file_name, mint, mappings):
    logging.info(f"Processing {file_name}")

    with open(file_name) as csvfile:
        transactions = list(csv.reader(csvfile, delimiter=','))
        transactions.pop(0)

    logging.info(f"Found {len(transactions)} transactions in {file_name}. Checking for category mappings.")
    for transaction in transactions:
        fill_in_merchant_category(transaction, mappings)

    logging.info(f"All categories filled for {file_name}")
    write_transactions_to_mint(mint, transactions)

    logging.info(f"Transactions written to Mint. Deleting {file_name}")
    os.remove(file_name)


def get_merchant_category(mappings, merchant_name):
    for mapping in mappings:
        if mapping[1] in merchant_name:
            return mapping[0]

    return None


if __name__ == '__main__':
    main()
