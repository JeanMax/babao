# babao

> I've got 99 problems But A Bot Ain't One

Just a little bitcoin trade bot, using Parabolic SAR strategy over kraken market api.


### Dep: (TODO: add links)

* jq (that could be avoided... not sure I want to parse any json with python tho)
* pandas


## Modes:

* bot (duh)
* real-time simulation (dry-run bot)
* simulation on a given data file
* training on a given data file
* real-time chart with matplotlib would be neat


### TODO:

* run the script as a service? (without main loop)
* dump transaction to ledger-cli


### Process:

* fetch raw trade data from api
* resample data (ohlc++)
* update indicators
* make decision (sell/buy)
* apply decision (if any) and log transaction
