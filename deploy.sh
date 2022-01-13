#!/usr/bin/env bash

ssh boontubox "rm -rf crypto-ledger-sync && mkdir -p crypto-ledger-sync/crypto-ledger-sync"
scp -r $PWD/* boontubox:crypto-ledger-sync
scp -r $PWD/.env boontubox:crypto-ledger-sync
ssh boontubox "cd crypto-ledger-sync && docker build -t crypto-ledger-sync --no-cache ."
