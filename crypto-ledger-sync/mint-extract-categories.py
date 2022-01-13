import csv
import mintapi
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MINT_USERNAME = os.environ.get('MINT_USERNAME')
MINT_PASSWORD = os.environ.get('MINT_PASSWORD')
MFA_METHOD = os.environ.get('MFA_METHOD')
MFA_TOKEN = os.environ.get('MFA_TOKEN')


def main():
    mint = get_mint_client()

    categories = mint.get_categories()

    category_parents = extract_category_parents(categories)

    print_categories(category_parents, '0', '', -1)

    mint.close()


def extract_category_parents(categories):
    logging.warning(categories)

    csv_fh = open('/data/mint-categories.csv', "w")

    category_parents = {}

    for category in categories:
        category_id = category['id']
        parent_id = category['parentId'] if 'parentId' in category else ''
        csv_fh.write(','.join([str(category_id), category['name'], parent_id]) + "\n")

        if parent_id not in category_parents:
            category_parents[parent_id] = []

        category_parents[parent_id].append((str(category_id), category['name']))

    csv_fh.close()

    return category_parents


def print_categories(category_parents, category_id, category_name, depth):
    txt_fh = open('/data/mint-categories.txt', "w")

    if depth >= 0:
        txt_fh.write(f"{'  ' * depth} {category_name:<{30 - (depth * 2)}} {category_id}\n")

    if category_id in category_parents:
        children = category_parents[category_id]
        for child in children:
            print_categories(category_parents, child[0], child[1], depth + 1)

    txt_fh.close()


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


if __name__ == '__main__':
    main()
