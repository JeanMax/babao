# babao

> I've got 99 problems But A Bot Ain't One

Just a little [insert crypto-currency] trade bot, using [insert strategy] over [insert market-place] api.


## Usage:

```shell
> babao --help
```
```
usage: babao [-h] [-g] [-f] [-v | -q] <command> [<args>] ...

A bitcoin trading machine.

optional arguments:
  -h, --help          show this help message and exit
  -g, --graph         show a chart (matplotlib)
  -f, --fuck-it       stop bitching about existing lockfile
  -v, --verbose       increase output verbosity
  -q, --quiet         stfu damn bot

commands:
  <command> [<args>]
    dry-run (d)       real-time bot simulation
    wet-run (w)       real-time bot with real-money!
    training (t)      train bot on the given raw trade data file
    backtest (b)      test strategy on the given raw trade data file
    fetch (f)         fetch raw trade data since the beginning of times

Run 'babao <command> --help' for detailed help.
```


## Install:

See [INSTALL.md](INSTALL.md)


## License:

[BeerWare License](LICENSE)
