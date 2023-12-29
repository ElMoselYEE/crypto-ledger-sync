import glob
import csv
import sys
from dateutil import parser
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ZEN_TRX_GLOB = "/data/user_transaction_data_*.csv"
OUTPUT_FILE = "/data/for-cointracker-from-zen.csv"
SUPPORTED_OPERATIONS = ['buy', 'sell', 'trade', 'Receive', 'Send', 'interest_received', 'staking_reward']
OUTPUT_HEADERS = ["Type", "Buy Amount", "Buy Currency",
                  "Sell Amount", "Sell Currency", "Fee",
                  "Fee Currency", "Exchange", "Trade-Group",
                  "Comment", "Date", "Tx-ID"]


def map_currency(currency):
    if currency == 'DOT':
        return 'DOT2'

    return currency


def read_transactions():
    for file in glob.glob(ZEN_TRX_GLOB):
        with open(file) as csvfile:
            transactions = list(csv.reader(csvfile))[1:]

            logging.info(f"Found {file} with {len(transactions)} transactions")

    return transactions


def main():
    data_to_write = [OUTPUT_HEADERS]
    for transaction in [x for x in read_transactions() if x[1] in SUPPORTED_OPERATIONS]:
        data_to_write.extend(parse_transaction_data(transaction))

    write_buffered_transactions(data_to_write)


def write_buffered_transactions(data_to_write):
    write_file = open(OUTPUT_FILE, 'w')
    for data in data_to_write:
        write_file.write(','.join(data) + "\n")

    write_file.close()

    logging.info(f"Wrote {len(data_to_write)} lines to {OUTPUT_FILE}")


def parse_transaction_data(transaction):
    data_to_write = []
    output = {}

    (
        timestamp,
        kind,
        in_amount,
        in_currency,
        out_amount,
        out_currency,
        fee_amount,
        fee_currency,
        exchange,
        us_based,
        txn_id
    ) = transaction

    if kind in ['trade', 'buy', 'sell']:
        output['type'] = 'Trade'
    if kind in ['Receive']:
        output['type'] = 'Deposit'
    if kind in ['Send']:
        output['type'] = 'Withdrawal'
    if kind in ['interest_received', 'staking_reward']:
        output['type'] = 'Income'

    output['buy_amount'] = in_amount
    output['buy_currency'] = map_currency(in_currency)
    output['sell_amount'] = out_amount
    output['sell_currency'] = map_currency(out_currency)
    output['fee'] = fee_amount
    output['fee_currency'] = map_currency(fee_currency)
    output['exchange'] = exchange
    output['trade_group'] = ''
    output['comment'] = ''
    output['date'] = parser.parse(timestamp).strftime("%d.%-m.%Y %H:%M:%S")
    output['tx_id'] = txn_id

    data_to_write.append([
        output['type'],
        output['buy_amount'],
        output['buy_currency'],
        output['sell_amount'],
        output['sell_currency'],
        output['fee'],
        output['fee_currency'],
        output['exchange'],
        output['trade_group'],
        output['comment'],
        output['date'],
        output['tx_id'],

    ])

    # offset USD balances since ZenLedger does not track these
    if (kind == 'buy' and out_currency == 'USD') or (kind == 'sell' and in_currency == 'USD'):
        data_to_write.append([
            'Deposit',
            str(float(out_amount) if kind == 'buy' else float(in_amount) * -1),
            'USD',
            '',
            '',
            '',
            '',
            output['exchange'],
            '',
            'Offset for USD not being tracked',
            output['date'],
            ''
        ])

    return data_to_write


if __name__ == '__main__':
    main()
