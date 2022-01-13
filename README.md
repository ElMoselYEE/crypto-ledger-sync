This code allows Blayne to perform the following syncing operations:

* Crypto.com → Mint ([cdc-to-mint.py](crypto-ledger-sync/cdc-to-mint.py))
* ZenLedger → CoinTracking ([zen-to-cointracking.py](crypto-ledger-sync/zen-to-cointracking.py))
* CoinTracking → Mint ([cointracking-to-mint.py](crypto-ledger-sync/cointracking-to-mint.py))
* Mint → Sheets ([mint-to-sheets.py](crypto-ledger-sync/mint-to-sheets.py))

# Running

1. Build the container

       docker build -t crypto-ledger-sync .

2. Pull down the .env file from LastPass

       lpass show crypto-ledger-sync-env --notes > .env

3. Run the jobs you're interested in e.g.
      
       # Mint to Sheets
       docker run --env-file=.env crypto-ledger-sync python3 /crypto-ledger-sync/mint-to-sheets.py

       # CoinTracking to Mint
       docker run --env-file=.env crypto-ledger-sync python3 /crypto-ledger-sync/cointracking-to-mint.py

       # ZenLedger to CoinTracking
       docker run -v $PWD/data:/data crypto-ledger-sync python3 /crypto-ledger-sync/zen-to-cointracking.py



# Deploy (Scheduled Jobs)

Only jobs that are to be scheduled should be deployed, otherwise we can just
run the job from the host machine.

    ./deploy.sh

This script will copy the files needed to build an image onto the server then
build the image. 

The crontab must be setup just one time, after that the new image builds will
be picked up automatically. The crontab might look like this:

    0 */4 * * * docker run --env-file=.env crypto-ledger-sync python /crypto-ledger-sync/cointracking-to-mint.py
    0 0 * * * docker run --env-file=.env crypto-ledger-sync python /crypto-ledger-sync/mint-to-sheets.py