"""Commands launched by parseArgv"""

import os
import time

import babao.config as conf
import babao.inputs.ledger.ledgerManager as lm
import babao.inputs.inputManager as im
import babao.inputs.inputBase as ib
import babao.models.modelManager as mm
import babao.utils.date as du
import babao.utils.log as log
import babao.utils.signal as sig


def wetRun(unused_args):
    """Dummy"""
    print("Sorry, this is not implemented yet :/")


def dryRun(unused_args):
    """Real-time bot simulation"""
    while not sig.EXIT:
        if im.fetchInputs():
            mm.predictModelsMaybeTrade(
                since=du.nowMinus(weeks=1)  # TODO: do not hardcode the lookback
            )


def fetch(unused_args):
    """Fetch raw trade data since the beginning of times"""
    if os.path.isfile(conf.DB_FILE):
        # os.remove(conf.DB_FILE)  # TODO: warn user / create backup?
        log.warning(
            "Database file already exists (" + conf.DB_FILE + ")."
        )

    while not sig.EXIT and not im.fetchInputs():
        last_fetch = min(
            (i.last_row.name for i in ib.INPUTS if i.last_row is not None)
        )
        log.info("Fetched data till", du.to_datetime(last_fetch))

    if not sig.EXIT:
        log.info("Database up to date!")


def backtest(args):
    """
    Just a naive backtester

    It will call the trained strategies on each test data point
    """
    start_time = time.time()

    now = du.getTime(force=True)
    epoch_to_now = now - du.EPOCH
    t = du.EPOCH + epoch_to_now / 2

    while t < now and not lm.gameOver() and not sig.EXIT:
        t += du.secToNano(4 * 60 * 60)
        du.setTime(t)
        mm.predictModelsMaybeTrade(
            since=du.nowMinus(weeks=1)
            # TODO:  do not hardcode the lookback
        )

    score = lm.getGlobalBalanceInQuote()
    # hodl = price / big_fat_data_prices[0] * 100
    log.info(
        "Backtesting done! Score: " + str(round(float(score)))
        # + "% vs HODL: " + str(round(hodl)) + "%"
    )
    log.debug(
        "Backtesting took "
        + str(round(time.time() - start_time, 3)) + "s"
    )

    # TODO: fix graph
    if args.graph:
        # TODO: exit if graph is closed
        while not sig.EXIT:
            time.sleep(0.1)


def train(args):
    """Train the various (awesome) algorithms"""
    epoch_to_now = du.getTime(force=True) - du.EPOCH
    till = du.EPOCH + epoch_to_now / 2
    du.setTime(till)

    log.debug(
        "Train data: from", du.to_datetime(du.EPOCH),
        "to", du.to_datetime(till)
    )
    mm.trainModels(since=du.EPOCH)

    if args.graph:
        log.debug("Plot models on train data")
        mm.plotModels(since=du.EPOCH)

        log.debug("Plot models on test data")
        du.setTime(None)
        log.debug(
            "Test data: from", du.to_datetime(till),
            "to", du.to_datetime(du.getTime())
        )
        mm.plotModels(since=till)

    log.debug("Job done!")

    if args.graph:
        import matplotlib.pyplot as plt
        plt.show()
