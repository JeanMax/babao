# babao

> I've got 99 problems But A Bot Ain't One

Just a little [insert crypto-currency] trade bot, using [insert strategy] over [insert market-place] api.


## Modes:

* bot (duh)
* real-time simulation (dry-run bot)
* simulation on a given data file
* training on a given data file
* real-time chart with matplotlib would be neat


### TODO:

* run the script as a service? (without main loop)
* dump transaction to ledger-cli
* use compressed hdf instead of csv
* resample data starting from the last time stamp? (that way the current candle is always "full")


### Process:

* fetch raw trade data from api
* resample data (ohlc++)
* update indicators
* make decision (sell/buy)
* apply decision (if any) and log transaction
