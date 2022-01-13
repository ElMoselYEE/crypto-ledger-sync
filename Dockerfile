FROM python:3.7

RUN apt update && apt install -y chromium chromium-driver

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY crypto-ledger-sync /crypto-ledger-sync
COPY data /data
