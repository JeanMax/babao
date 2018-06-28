# TODO:

* grep -ri todo
* switch to another market api (-> gdax?)
* refactor models as objects?
    * there is some redundant code between models, handle that while you're at it
* babao is now too slow for dry-run on an old raspberry :/ solve that!
    * (might be linked to the recent kraken '0 fee' policy...)
* optimize real-time graph: since kraken is (more) laggy, it's really slow
* handle log files
* ideally the test/train data should look like the real-time data (new slice every few seconds)
* write more tests!
* multiproc.lock for lock


## Work-around'd:

* there is a concurrent access issue with the hdf database (core/graph)
