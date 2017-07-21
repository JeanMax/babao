import babao.utils.log as log


def test_initLogLevel():
    assert not log.VERBOSE

    log.initLogLevel(False)
    assert not log.VERBOSE

    log.initLogLevel(True)
    assert log.VERBOSE


def test_error():
    log.error("error")


def test_warning():
    log.warning("warning")


def test_debug():
    log.debug("debug")


def test_log():
    log.log("log")
