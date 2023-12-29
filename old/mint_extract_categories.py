import mint_client
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    mint = mint_client.get_mint_client()

    categories = mint.get_categories()

    category_parents = extract_category_parents(categories)

    logging.info('Writing categories as human-readable TXT')
    txt_fh = open('/data/mint-categories.txt', "w")
    write_categories(txt_fh, category_parents, '0', '', -1)
    txt_fh.close()

    mint.close()


def extract_category_parents(categories):
    logging.info('Writing categories as CSV')

    csv_fh = open('/data/mint-categories.csv', "w")

    category_parents = {}

    for category in categories:
        category_id = category['id'].split('_')[1]
        parent_id = category['parentId'].split('_')[1] if 'parentId' in category else '0'
        csv_fh.write(','.join([str(category_id), category['name'], parent_id]) + "\n")

        if parent_id not in category_parents:
            category_parents[parent_id] = []

        category_parents[parent_id].append((str(category_id), category['name']))

    csv_fh.close()

    return category_parents


def write_categories(txt_fh, category_parents, category_id, category_name, depth):
    if depth >= 0:
        txt_fh.write(f"{'  ' * depth} {category_name:<{30 - (depth * 2)}} {category_id}\n")

    if category_id in category_parents:
        children = category_parents[category_id]
        for child in children:
            write_categories(txt_fh, category_parents, child[0], child[1], depth + 1)


if __name__ == '__main__':
    main()
