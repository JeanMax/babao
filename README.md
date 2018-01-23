# babao

> I've got 99 problems But A Bot Ain't One

Just a little [insert crypto-currency] trade bot, using [insert strategy] over [insert market-place] api.


## Install:

```
git clone https://github.com/JeanMax/babao
cd babao
```

* Using make:
```
make
```


optional dependencies (matplotlib):
```
make install_graph
```


optional dependencies (pytest/pylint/flake8):
```
make install_test
```


if you're not planning to develop:
```
make install
```


* Or Using pip:
```
pip install .
```


optional dependencies:
```
pip install .[graph]
pip install .[test]
```


## Requirements:

* python3
* pip
* hdf5

* optional:
  * make


## Dependencies:

Pip will handle these during install.

* machine learning:
    * keras
    * tensorflow
    * scikit-learn (this includes scipy)
    * joblib (just for saving scikit models...)

* data handling:
    * pandas (this includes numpy)
    * tables

* parsing:
    * configparser
    * argparse

* api:
    * krakenex

* graph: (optional)
    * matplotlib

* test: (optional)
    * pytest
    * pylint
    * flake8


## Usage:

```
> babao --help
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

## TODO:

* grep -ri todo
* there is a concurrent access issue with the hdf database (core/graph)
* switch to another market api
* refactor models as objects?
