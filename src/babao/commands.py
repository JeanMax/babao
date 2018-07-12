"""Commands launched by parseArgv"""

import time

import babao.config as conf
import babao.inputs.ledger.ledgerManager as lm
import babao.inputs.inputManager as im
import babao.inputs.inputBase as ib
import babao.models.modelManager as mm
import babao.utils.date as du
import babao.utils.file as fu
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
                since=du.nowMinus(days=ib.REAL_TIME_LOOKBACK_DAYS)
            )


def fetch(unused_args):
    """Fetch raw trade data since the beginning of times"""
    fu.maintenance()        # DEBUG
    while not sig.EXIT and not im.fetchInputs():
        last_fetch = min(
            (i.current_row.name for i in ib.INPUTS if i.current_row is not None)
        )
        log.info("Fetched data till", du.toStr(last_fetch))

    if not sig.EXIT:
        log.debug("Fetching done, optimizing database...")
        fu.maintenance()
        log.info("Database up to date!")


def backtest(args):
    """
    Just a naive backtester

    It will call the trained strategies on each test data point
    """
    now = du.getTime(force=True)
    t = du.getTime()
    log.info(
        "Test data: from", du.toStr(t),
        "to", du.toStr(now)
    )
    while t < now and not lm.gameOver() and not sig.EXIT:
        t += du.secToNano(conf.TIME_INTERVAL * 60)  # TODO
        im.timeTravel(t)
        mm.predictModelsMaybeTrade(
            since=du.nowMinus(days=ib.REAL_TIME_LOOKBACK_DAYS)
        )

    score = lm.getGlobalBalanceInQuote()
    # hodl = price / big_fat_data_prices[0] * 100
    log.info(
        "Backtesting done! Score: " + str(round(float(score)))
        # + "% vs HODL: " + str(round(hodl)) + "%"
        # TODO
    )

    # TODO: fix graph
    if args.graph:
        # TODO: exit if graph is closed
        while not sig.EXIT:
            time.sleep(0.1)


def train(args):
    """Train the various (awesome) algorithms"""
    im.timeTravel(ib.SPLIT_DATE)

    log.debug(
        "Train data: from", du.toStr(du.EPOCH),
        "to", du.toStr(ib.SPLIT_DATE)
    )
    mm.trainModels(since=du.EPOCH)

    if args.graph:
        log.debug("Plot models on train data")
        mm.plotModels(since=du.EPOCH)

        log.debug("Plot models on test data")
        im.timeTravel(du.getTime(force=True))  # back to the future
        log.debug(
            "Test data: from", du.toStr(du.toStr(ib.SPLIT_DATE)),
            "to", du.toStr(du.getTime())
        )
        mm.plotModels(since=ib.SPLIT_DATE)

    log.debug("Job done!")

    if args.graph:
        import matplotlib.pyplot as plt
        plt.show()
