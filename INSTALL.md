# Install:

```shell
git clone https://github.com/JeanMax/babao
cd babao
```

### Using make...:
```shell
make
```


optional dependencies (matplotlib):
```shell
make install_graph
```


optional dependencies (pytest/pylint/flake8):
```shell
make install_test
```


if you're not planning to develop:
```shell
make install
```


### ...or using pip:
```shell
pip install .
```


optional dependencies:
```shell
pip install .[graph]
pip install .[test]
```


## Requirements:

* python3
* pip
* hdf5

### optional:
* make


## Dependencies:

Pip will handle these during install.

### machine learning:
* keras
* tensorflow
* scikit-learn (this includes scipy)
* joblib (just for saving scikit models...)

### data handling:
* pandas (this includes numpy)
* tables

### parsing:
* configparser
* argparse

### api:
* krakenex

### graph: (optional)
* matplotlib

### test: (optional)
* pytest
* pylint
* flake8
