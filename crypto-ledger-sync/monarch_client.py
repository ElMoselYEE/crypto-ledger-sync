import os
import logging
import sys
import asyncio

from monarchmoney import MonarchMoney

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MONARCH_EMAIL = os.environ.get('MONARCH_EMAIL')
MONARCH_PASSWORD = os.environ.get('MONARCH_PASSWORD')
MFA_TOKEN = os.environ.get('MFA_TOKEN')

async def get_client():
    logging.info(f"Connecting to Monarch [email={MONARCH_EMAIL}]")

    mm = MonarchMoney()

    await mm.login(
        email=MONARCH_EMAIL,
        password=MONARCH_PASSWORD,
        save_session=False,
        use_saved_session=False,
        mfa_secret_key=MFA_TOKEN,
    )

    return mm