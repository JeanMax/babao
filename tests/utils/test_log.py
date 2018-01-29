import pytest

import babao.utils.log as log


def test_initLogLevel():
    assert log.VERBOSE == 1

    log.initLogLevel(1, False)
    assert log.VERBOSE == 1

    log.initLogLevel(2, False)
    assert log.VERBOSE == 2

    log.initLogLevel(3, False)
    assert log.VERBOSE == 3

    log.initLogLevel(42, True)
    assert log.VERBOSE == 0



def test_error():
    with pytest.raises(SystemExit):
        log.error("error")


def test_warning():
    log.warning("warning")


def test_debug():
    log.debug("debug")


def test_info():
    log.info("info")
