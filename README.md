This code allows Blayne to perform the following syncing operations:

* Mint → Sheets ([mint-to-sheets_house.py](crypto-ledger-sync/mint_to_sheets_house.py))

The crypto operations are shelved.

# Running

1. Build the container

       docker build -t crypto-ledger-sync .

2. Pull down the .env file from LastPass

       lpass show crypto-ledger-sync-env --notes > .env

3. Run the jobs you're interested in e.g.
      
       # Monarch to Sheets
       docker run --env-file=.env crypto-ledger-sync python3 /crypto-ledger-sync/monarch_to_sheets.py

# Upload Edited Env File

      cat .env | lpass edit --non-interactive --notes crypto-ledger-sync-env

# Deploy (Scheduled Jobs)

Only jobs that are to be scheduled should be deployed, otherwise we can just
run the job from the host machine.

Deployment is done by building container on the server:

    docker build -t crypto-ledger-sync --no-cache .

An example of how crontab might look when setup

    0 0 * * * docker run --env-file=.env crypto-ledger-sync python /crypto-ledger-sync/mint_to_sheets_house.py