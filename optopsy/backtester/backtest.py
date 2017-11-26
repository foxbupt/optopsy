import collections
import queue
import itertools
import time

from optopsy.datafeeds.sqlite_adapter import SqliteAdapter
from optopsy.backtester.broker import BaseBroker
from optopsy.backtester.event import EventType


class Backtest(object):
    def __init__(self, strategy, datafeed=SqliteAdapter,
                 path=None,  **params):

        # initialize backtest components
        self.queue = queue.Queue()
        self.datafeed = datafeed(path)
        self.broker = BaseBroker(self.queue, self.datafeed)

        # apply cartesian product of all params to generate all
        # combinations of strategies to test for
        self.strats = list()
        opt_keys = list(params)

        vals = self._iterize(params.values())
        opt_vals = itertools.product(*vals)
        o_kwargs1 = map(zip, itertools.repeat(opt_keys), opt_vals)
        opt_kwargs = map(dict, o_kwargs1)

        it = itertools.product([strategy], opt_kwargs)
        for strat in it:
            self.strats.append(strat)

    def _iterize(self, iterable):
        """
        Handy function which turns things into things that can be iterated upon
        including iterables

        :param iterable:
        """
        niterable = list()
        for elem in iterable:
            if isinstance(elem, str):
                elem = (elem,)
            elif not isinstance(elem, collections.Iterable):
                elem = (elem,)

            niterable.append(elem)

        return niterable

    def run(self):

        # program timer
        program_starts = time.time()

        for scenario in self.strats:
            # initialize a new instance strategy from the strategy list
            # and an account instance for each scenario
            strategy = scenario[0](self.broker, self.queue, **scenario[1])
            self.broker.continue_backtest = True

            while self.broker.continue_backtest:
                # run backtesting loop
                try:
                    event = self.queue.get(False)
                except queue.Empty:
                    self.broker.stream_next()
                else:
                    if event is not None:
                        if event.event_type == EventType.DATA:
                            # update strategy instance with current data
                            strategy.on_data_event(event)
                        elif event.event_type == EventType.ORDER:
                            # send the order to the broker for processing
                            self.broker.process_order(event)
                        elif event.event_type == EventType.FILL:
                            # notify the strategy that we have a fill on one of its orders
                            strategy.on_fill_event(event)
                        elif event.event_type == EventType.REJECTED:
                            strategy.on_rejected_event(event)
                        else:
                            raise NotImplementedError("Unsupported event.type '%s'" % event.type)

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
