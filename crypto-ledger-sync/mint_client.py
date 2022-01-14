import mintapi
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MINT_USERNAME = os.environ.get('MINT_USERNAME')
MINT_PASSWORD = os.environ.get('MINT_PASSWORD')
MFA_METHOD = os.environ.get('MFA_METHOD')
MFA_TOKEN = os.environ.get('MFA_TOKEN')


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
